import bpy, bgl, mathutils
import ctypes
import math
import numpy
import os

from .. import btoa

from bl_ui.properties_render import RENDER_PT_color_management
from bl_ui.space_outliner import OUTLINER_MT_collection_view_layer

'''
Render callbacks and global variables

Listen, I know. This is messy. But the render callback needs to be available in
memory for interactive rendering to work, and the Arnold API handles renders
asynchronously. On top of that, the callback function needs access to the current
session and frame buffer to do it's job.

So, that's it, we're here, deal with it. Let's move on.
'''
AI_ENGINE_TAG_REDRAW = None
AI_SESSION = None
AI_FRAMEBUFFER = None

def ai_render_update_callback(private_data, update_type, display_output):
    global AI_FRAMEBUFFER
    global AI_ENGINE_TAG_REDRAW

    if display_output != int(btoa.NO_DISPLAY_OUTPUTS):
        AI_FRAMEBUFFER.requires_update = True
        AI_ENGINE_TAG_REDRAW()

    status = btoa.FAILED

    if update_type == int(btoa.INTERRUPTED):
        status = btoa.PAUSED  
    elif update_type == int(btoa.BEFORE_PASS):
        status = btoa.RENDERING
    elif update_type == int(btoa.DURING_PASS):
        status = btoa.RENDERING
    elif update_type == int(btoa.AFTER_PASS):
        status = btoa.RENDERING
    elif update_type == int(btoa.RENDER_FINISHED):
        status = btoa.RENDER_FINISHED
    elif update_type == int(btoa.PAUSED):
        status = btoa.RESTARTING
    elif update_type == int(btoa.ERROR):
        status = btoa.FAILED

    return status

def update_viewport(x, y, width, height, buffer, data):
    global AI_SESSION
    global AI_FRAMEBUFFER

    options = btoa.UniverseOptions()
    min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

    x = x - min_x
    y = max_y - y - height

    if buffer:
        try:
            b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
            rect = numpy.ctypeslib.as_array(b, shape=(width * height, 4))

            AI_FRAMEBUFFER.write_bucket(x, y, width, height, rect.flatten())
            
        finally:
            AI_SESSION.free_buffer(buffer)

AI_DISPLAY_CALLBACK = btoa.ArnoldDisplayCallback(update_viewport)
AI_RENDER_CALLBACK = ai_render_update_callback

'''
Render engine class, registration, and other UI goodies
'''
class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True
    bl_use_eevee_viewport = True

    _outliner_context_menu_draw = None

    def __init__(self):
        self.progress = 0
        self._progress_increment = 0
        
        self.session = btoa.Session()

    def __del__(self):
        global AI_SESSION
        AI_SESSION.end()
        AI_SESSION = None

        global AI_ENGINE_TAG_REDRAW
        global dummy_tag_redraw
        AI_ENGINE_TAG_REDRAW = None

        global AI_FRAMEBUFFER
        AI_FRAMEBUFFER = None

    @classmethod
    def is_active(cls, context):
        return context.scene.render.engine == cls.bl_idname

    @classmethod
    def register(cls):
        if cls._outliner_context_menu_draw is None:
            
            def draw(self, context):
                layout = self.layout

                layout.operator("outliner.collection_exclude_set")
                layout.operator("outliner.collection_exclude_clear")

                layout.operator("outliner.collection_holdout_set")
                layout.operator("outliner.collection_holdout_clear")

                if context.engine in ('CYCLES', 'ARNOLD'):
                    layout.operator("outliner.collection_indirect_only_set")
                    layout.operator("outliner.collection_indirect_only_clear")

            cls._outliner_context_menu_draw = OUTLINER_MT_collection_view_layer.draw
            OUTLINER_MT_collection_view_layer.draw = draw

    @classmethod
    def unregister_outliner_context_menu_draw(cls):
        if cls._outliner_context_menu_draw is not None:
            OUTLINER_MT_collection_view_layer.draw = cls._outliner_context_menu_draw
            cls._outliner_context_menu_draw = None              

    def update(self, data, depsgraph):
        self.session.start()
        self.session.export(self, depsgraph)

    def render(self, depsgraph):
        # Configure display callback
        # NOTE: We can't do this in the exporter because it results in a nasty MEMORY_ACCESS_VIOLATION error

        options = btoa.UniverseOptions()

        engine = self
        buckets = {}

        def update_render_result(x, y, width, height, buffer, data):
            render = depsgraph.scene.render
            cache = engine.session.cache

            if render.use_border:
                min_x, min_y, max_x, max_y = options.get_render_region()
            else:
                min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

            x = x - min_x
            y = max_y - y - height

            if buffer:
                try:
                    result = buckets.pop((x, y), None)

                    if result is None:
                        result = engine.begin_result(x, y, width, height, layer=cache.view_layer.name)

                    b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
                    rect = numpy.ctypeslib.as_array(b, shape=(width * height, 4))

                    result.layers[0].passes["Combined"].rect = rect
                    engine.end_result(result)

                    # Update progress counter

                    engine.progress += engine._progress_increment
                    engine.update_progress(engine.progress)
                
                finally:
                    engine.session.free_buffer(buffer)
            else:
                buckets[(x, y)] = engine.begin_result(x, y, width, height, layer=cache.view_layer.name)

            if engine.test_break():
                engine.session.abort()
                while buckets:
                    (x, y), result = buckets.popitem()
                    engine.end_result(result, cancel=True)

        cb = btoa.ArnoldDisplayCallback(update_render_result)

        display_node = self.session.get_node_by_name("__display_driver")
        
        if not display_node.is_valid():
            display_node = btoa.ArnoldNode("driver_display_callback")
            display_node.set_string("name", "__display_driver")
        
        display_node.set_pointer("callback", cb)

        # Calculate progress increment
        
        width, height = options.get_render_resolution()
        bucket_size = options.get_int("bucket_size")

        h_buckets = math.ceil(width / bucket_size)
        v_buckets = math.ceil(height / bucket_size)
        total_buckets = h_buckets * v_buckets
        
        self.progress = 0
        self._progress_increment = 1 / total_buckets

        self.session.render()

    def view_update(self, context, depsgraph):
        global AI_SESSION
        global AI_FRAMEBUFFER
        global AI_DISPLAY_CALLBACK
        global AI_RENDER_CALLBACK

        if not AI_SESSION or not AI_SESSION.is_running:
            region = context.region
            scene = depsgraph.scene

            AI_FRAMEBUFFER = btoa.FrameBuffer(self, region, scene)

            AI_SESSION = self.session
            AI_SESSION.start(interactive=True)
            AI_SESSION.export(self, depsgraph, context)

            global AI_ENGINE_TAG_REDRAW
            AI_ENGINE_TAG_REDRAW = self.tag_redraw

            display_node = self.session.get_node_by_name("__display_driver")
            
            if not display_node.is_valid():
                display_node = btoa.ArnoldNode("driver_display_callback")
                display_node.set_string("name", "__display_driver")
            
            display_node.set_pointer("callback", AI_DISPLAY_CALLBACK)

            AI_SESSION.render_interactive(AI_RENDER_CALLBACK)

        # Update viewport camera
        if AI_SESSION.is_interactive:
            AI_SESSION.pause()

            node = AI_SESSION.get_node_by_name("BTOA_VIEWPORT_CAMERA")

            bl_camera = btoa.utils.get_viewport_camera_object(context.space_data)
            AI_SESSION.last_viewport_matrix = bl_camera.matrix_world

            btoa.CameraExporter(AI_SESSION, node).export(bl_camera)

            AI_SESSION.restart()

        if depsgraph.id_type_updated("SCENE"):
            #AI_SESSION.cache.sync(self, depsgraph, context)
            #btoa.OptionsExporter(AI_SESSION).export()
            pass

        if depsgraph.id_type_updated("OBJECT"):
            AI_SESSION.pause()

            light_data_needs_update = False
            polymesh_data_needs_update = False

            for update in reversed(depsgraph.updates):
                if isinstance(update.id, bpy.types.Light):
                    light_data_needs_update = True
                elif isinstance(update.id, btoa.BTOA_CONVERTIBLE_TYPES) and update.is_updated_geometry:
                    polymesh_data_needs_update = True

                if isinstance(update.id, bpy.types.Object):
                    unique_name = btoa.utils.get_unique_name(update.id)
                    node = AI_SESSION.get_node_by_name(unique_name)

                    if update.id.type == 'LIGHT' and light_data_needs_update:
                        btoa.LightExporter(AI_SESSION, node).export(update.id)

                    elif polymesh_data_needs_update:
                        btoa.PolymeshExporter(AI_SESSION, node).export(update.id, interactive=True)

                    if update.is_updated_shading:
                        pass

                    if update.is_updated_transform:
                        node.set_matrix("matrix", btoa.utils.flatten_matrix(update.id.matrix_world))
            
            AI_SESSION.restart()

    def view_draw(self, context, depsgraph):
        global AI_SESSION
        global AI_FRAMEBUFFER

        region = context.region
        scene = depsgraph.scene

        # Check to see if viewport camera changed
        if context.space_data.region_3d.view_matrix.inverted() != AI_SESSION.last_viewport_matrix:
            self.tag_update()

        # This will create weird issues when resizing the screen (Blender will forget about anything in the buffer that was
        # rendered before resizing). Will need to add some kind of resizing method to handle this, instead of blowing the
        # whole thing away with a new class
        if not AI_FRAMEBUFFER:
            AI_FRAMEBUFFER = btoa.FrameBuffer(self, region, scene)

        if AI_FRAMEBUFFER.requires_update:
            AI_FRAMEBUFFER.generate_texture()
            #self.tag_redraw()

        AI_FRAMEBUFFER.draw(self, scene)

def get_panels():
    exclude_panels = {
        'RENDER_PT_gpencil',
        'RENDER_PT_simplify',
        'RENDER_PT_freestyle',
        'RENDER_PT_stereoscopy',
        'DATA_PT_light',
        'DATA_PT_preview',
        'DATA_PT_EEVEE_light',
        'DATA_PT_area',
        'DATA_PT_spot',
        'DATA_pt_context_light',
        'DATA_PT_lens',
        'DATA_PT_camera',
        'DATA_PT_camera_safe_areas',
        'DATA_PT_camera_background_image',
        'DATA_PT_camera_display',
        'WORLD_PT_context_world',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels

gpencil_poll = None

@classmethod
def gpencil_poll_override(cls, context):
    return False

def register():
    bpy.utils.register_class(ArnoldRenderEngine)
    
    for panel in get_panels():
        panel.COMPAT_ENGINES.add(ArnoldRenderEngine.bl_idname)

    # For some reason, there are a handful of classes that get 'ARNOLD'
    # added to COMPAT_ENGINES even though they're left out of the
    # list returned from get_panels(). Need to file a bug report
    # to Blender devs, but for now we'll brute-force remove it.
    for panel in bpy.types.Panel.__subclasses__():
        if panel.__name__ == 'DATA_PT_light':
            panel.COMPAT_ENGINES.remove(ArnoldRenderEngine.bl_idname)

def unregister():
    bpy.utils.unregister_class(ArnoldRenderEngine)
    
    for panel in get_panels():
        if ArnoldRenderEngine.bl_idname in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove(ArnoldRenderEngine.bl_idname)

    ArnoldRenderEngine.unregister_outliner_context_menu_draw()