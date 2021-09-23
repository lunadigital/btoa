import bpy, bgl, mathutils
import ctypes
import math
import numpy
import os

from .. import btoa

from bl_ui.properties_render import RENDER_PT_color_management
from bl_ui.space_outliner import OUTLINER_MT_collection_view_layer

import arnold

'''
Render callbacks and global variables

Listen, I know. This is messy. But the render callback needs to be available in
memory for interactive rendering to work, and the Arnold API handles renders
asynchronously. On top of that, the callback function needs access to the
render engine, current session, and frame buffer to do it's job.

So, that's it, we're here, deal with it. Let's move on.
'''
AI_ENGINE = None
AI_SESSION = None

def exists(struct):
    ''' Checks to see if struct exists in Blender's memory '''
    try:
        id = struct.id_data
    except:
        return False
    
    return True

def ai_render_update_callback(private_data, update_type, display_output):
    global AI_ENGINE
    global AI_SESSION

    print("----- IN CALLBACK -----")

    if exists(AI_ENGINE) and display_output != int(btoa.NO_DISPLAY_OUTPUTS):
        AI_ENGINE.framebuffer.requires_update = True
        AI_ENGINE.tag_redraw()

    if not exists(AI_ENGINE) and update_type in (
        int(btoa.BEFORE_PASS),
        int(btoa.DURING_PASS),
        int(btoa.AFTER_PASS),
    ):
        print("Interrupting, sorry")
        arnold.AiRenderInterrupt()
        #AI_ENGINE = None

    status = btoa.FAILED

    if update_type == int(btoa.INTERRUPTED):
        status = btoa.INTERRUPTED
        print("Status: Interrupted")
    elif update_type == int(btoa.BEFORE_PASS):
        status = btoa.RENDERING
        print("Status: Rendering")
    elif update_type == int(btoa.DURING_PASS):
        status = btoa.RENDERING
        print("Status: Rendering")
    elif update_type == int(btoa.AFTER_PASS):
        status = btoa.RENDERING
        print("Status: Rendering")
    elif update_type == int(btoa.RENDER_FINISHED):
        status = btoa.RENDER_FINISHED
        print("Status: Finished")
    elif update_type == int(btoa.ERROR):
        status = btoa.FAILED
        AI_ENGINE = None
        print("Status: Failed")

    return status

def update_viewport(x, y, width, height, buffer, data):
    global AI_ENGINE
    global AI_SESSION

    options = btoa.UniverseOptions()
    min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

    x = x - min_x
    y = max_y - y - height

    if buffer and exists(AI_ENGINE):
        try:
            b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
            rect = numpy.ctypeslib.as_array(b, shape=(width * height, 4))
            rect = rect.flatten()

            AI_ENGINE.framebuffer.write_bucket(x, y, width, height, rect.tolist())
            
        finally:
            AI_ENGINE.session.free_buffer(buffer)

AI_DISPLAY_CALLBACK = btoa.ArnoldDisplayCallback(update_viewport)
AI_RENDER_CALLBACK = ai_render_update_callback

'''
Render engine class, registration, and other UI goodies
'''
class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True

    _outliner_context_menu_draw = None

    def __init__(self):
        self.progress = 0
        self._progress_increment = 0
        
        self.session = btoa.Session()

    def __del__(self):
        arnold.AiRenderInterrupt()

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
                        result = engine.begin_result(x, y, width, height, layer=engine.session.depsgraph.view_layer_eval.name)

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
                buckets[(x, y)] = engine.begin_result(x, y, width, height, layer=engine.session.depsgraph.view_layer_eval.name)

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
        global AI_DISPLAY_CALLBACK
        global AI_RENDER_CALLBACK

        if not self.session or not self.session.is_running:
            region = context.region
            scene = depsgraph.scene

            self.framebuffer = btoa.FrameBuffer(self, region, scene)

            self.session.start(interactive=True)
            self.session.export(self, depsgraph)

            display_node = self.session.get_node_by_name("__display_driver")
            
            if not display_node.is_valid():
                display_node = btoa.ArnoldNode("driver_display_callback")
                display_node.set_string("name", "__display_driver")
            
            display_node.set_pointer("callback", AI_DISPLAY_CALLBACK)

            self.session.render_interactive(AI_RENDER_CALLBACK)

    def view_draw(self, context, depsgraph):
        global AI_ENGINE
        global AI_SESSION
        AI_ENGINE = self
        AI_SESSION = self.session

        region = context.region
        scene = depsgraph.scene

        # This will create weird issues when resizing the screen (Blender will forget about anything in the buffer that was
        # rendered before resizing). Will need to add some kind of resizing method to handle this, instead of blowing the
        # whole thing away with a new class
        if not self.framebuffer:
            self.framebuffer = btoa.FrameBuffer(self, region, scene)

        if self.framebuffer.requires_update:
            self.framebuffer.generate_texture()
            self.tag_redraw()

        self.framebuffer.draw(self, scene)

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