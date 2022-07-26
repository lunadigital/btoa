from typing import Optional
import bpy, bgl, mathutils
import ctypes
import math
import numpy
import os
import gpu
import arnold

from .. import btoa
from ..btoa import utils, OptionsExporter
from ..props.light import ArnoldLight

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
AI_SESSION: Optional[btoa.Session] = None
AI_FRAMEBUFFER:Optional[btoa.FrameBuffer] = None
AI_DRIVER_UPDATE_VIEWPORT = False

def ai_render_update_callback(private_data, update_type, display_output):
    global AI_FRAMEBUFFER
    global AI_ENGINE_TAG_REDRAW
    global AI_DRIVER_UPDATE_VIEWPORT

    assert AI_FRAMEBUFFER is not None
    AI_FRAMEBUFFER.requires_update = True

    assert AI_ENGINE_TAG_REDRAW
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
        AI_DRIVER_UPDATE_VIEWPORT = True
    elif update_type == int(btoa.RENDER_FINISHED):
        status = btoa.RENDER_FINISHED
        AI_DRIVER_UPDATE_VIEWPORT = False
    elif update_type == int(btoa.PAUSED):
        status = btoa.RESTARTING
    elif update_type == int(btoa.ERROR):
        status = btoa.FAILED
        AI_DRIVER_UPDATE_VIEWPORT = False

    return int(status)

def update_viewport(x, y, width, height, buffer):
    global AI_SESSION
    global AI_FRAMEBUFFER
    global AI_DRIVER_UPDATE_VIEWPORT

    options = btoa.UniverseOptions()
    min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

    x = x - min_x
    y = max_y - y - height

    if buffer:
        try:
            b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
            rect = numpy.ctypeslib.as_array(b, shape=(width * height, 4))
            assert AI_FRAMEBUFFER is not None
            AI_FRAMEBUFFER.write_bucket(x, y, width, height, rect.flatten())

        finally:
            if (AI_SESSION):
                AI_SESSION.free_buffer(buffer)

                if AI_DRIVER_UPDATE_VIEWPORT:
                    AI_FRAMEBUFFER.requires_update = True
                    AI_ENGINE_TAG_REDRAW()

AI_DISPLAY_CALLBACK = btoa.ArnoldDisplayCallback(update_viewport)
AI_RENDER_CALLBACK = ai_render_update_callback

'''
Render engine class, registration, and other UI goodies
'''
class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_eevee_viewport = True
    bl_use_postprocess = True

    _outliner_context_menu_draw = None

    def __init__(self):
        self.progress = 0
        self._progress_increment = 0
        self.session = btoa.Session()

    def __del__(self):
        global AI_SESSION
        if (AI_SESSION is not None):
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
        prefs = bpy.context.preferences.addons[btoa.constants.BTOA_PACKAGE_NAME].preferences

        self.session.start()
        self.session.export(self, depsgraph, prefs)

    def render(self, depsgraph):
        # Configure display callback
        # NOTE: We can't do this in the exporter because it results in a nasty MEMORY_ACCESS_VIOLATION error
        options = btoa.UniverseOptions()
        engine = self
        self.use_highlight_tiles = True

        def update_render_result(aovs, x, y, width, height, buffer):
            render = depsgraph.scene.render
            cache = engine.session.cache

            bucket_size = width * height * 4

            if render.use_border:
                min_x, min_y, max_x, max_y = options.get_render_region()
            else:
                min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

            x = x - min_x
            y = max_y - y - height

            aovs = ctypes.cast(aovs, ctypes.c_char_p).value.decode().split("\\")[:-1]
            aovs = list(map(lambda x: x.replace("RGBA", "Combined"), aovs))

            print(aovs)

            b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
            b = numpy.ctypeslib.as_array(b, shape=(width * height * len(aovs), 4))

            result = engine.begin_result(x, y, width, height, layer=cache.view_layer.name)

            for aov in aovs:
                start = aovs.index(aov) * bucket_size
                result.layers[0].passes[aov].rect = b[start:start + bucket_size]

            engine.end_result(result)
            engine.session.free_buffer(buffer)

            # Update progress counter
            engine.progress += engine._progress_increment
            engine.update_progress(engine.progress)

            if engine.test_break():
                engine.session.abort()
                engine.end_result(result, cancel=True)

        cb = btoa.ArnoldDisplayCallback(update_render_result)
        driver = btoa.ArnoldNode("driver_display_callback")
        driver.set_string("name", "btoa_driver")
        driver.set_pointer("callback", cb)

        # Set up custom render passes
        aovs = depsgraph.view_layer.arnold.passes
        
        for aov in aovs.__annotations__.keys():
            if not getattr(aovs, aov):
                continue

            aov_name = "Z" if aov[9:] == 'z' else aov[9:]

            if aov_name == 'beauty':
                continue
            
            self.add_pass(aov_name, 4, "RGBA")

        # Calculate progress increment
        (width, height) = options.get_render_resolution()
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

        region = context.region
        scene = depsgraph.scene
        prefs = bpy.context.preferences.addons[btoa.constants.BTOA_PACKAGE_NAME].preferences

        if not AI_SESSION or not AI_SESSION.is_running:
            AI_FRAMEBUFFER = btoa.FrameBuffer((region.width, region.height), float(scene.arnold.viewport_scale))

            AI_SESSION = self.session
            AI_SESSION.start(interactive=True)
            AI_SESSION.export(self, depsgraph, prefs, context)

            global AI_ENGINE_TAG_REDRAW
            AI_ENGINE_TAG_REDRAW = self.tag_redraw

            display_driver = btoa.ArnoldNode("driver_display_callback")
            display_driver.set_string("name", "btoa_driver")
            display_driver.set_pointer("callback", AI_DISPLAY_CALLBACK)

            AI_SESSION.render_interactive(AI_RENDER_CALLBACK)

        AI_SESSION.pause()

        AI_SESSION.cache.sync(self, depsgraph, prefs, context)
        OptionsExporter(AI_SESSION).export(interactive=True)

        if AI_SESSION.update_viewport_dimensions:
            AI_SESSION.update_viewport_dimensions = False

            options = btoa.UniverseOptions()
            options.set_int("xres", int(region.width * float(scene.arnold.viewport_scale)))
            options.set_int("yres", int(region.height * float(scene.arnold.viewport_scale)))

            AI_FRAMEBUFFER = btoa.FrameBuffer((region.width, region.height), float(scene.arnold.viewport_scale))

        # Update viewport camera
        node = AI_SESSION.get_node_by_name("BTOA_VIEWPORT_CAMERA")

        bl_camera = utils.get_viewport_camera_object(context)

        if node.type_is(bl_camera.data.arnold.camera_type):
            btoa.CameraExporter(AI_SESSION, node).export(bl_camera)
        else:
            new_node = btoa.CameraExporter(AI_SESSION).export(bl_camera)
            AI_SESSION.replace_node(node, new_node)

            new_node.set_string("name", bl_camera.name)

        AI_SESSION.cache.viewport_camera.sync(bl_camera)

        # Update shaders
        if depsgraph.id_type_updated("MATERIAL"):
            for update in reversed(depsgraph.updates):
                material = utils.get_parent_material_from_nodetree(update.id)
                world_ntree = scene.world.arnold.node_tree

                if material:
                    unique_name = utils.get_unique_name(material)
                    old_node = AI_SESSION.get_node_by_name(unique_name)

                    if old_node.is_valid():
                        surface, volume, displacement = update.id.export()
                        new_node = surface[0]

                        AI_SESSION.replace_node(old_node, new_node)

                        # We have to rename the node AFTER we swap them to
                        # avoid memory and session.get_node_by_name() issues
                        new_node.set_string("name", unique_name)

                elif world_ntree and update.id.name == world_ntree.name:
                    # This code is repeated in view_draw() below
                    # Consider cleaning this up
                    unique_name = utils.get_unique_name(scene.world)
                    old_node = AI_SESSION.get_node_by_name(unique_name)

                    if old_node.is_valid():
                        new_node = btoa.WorldExporter(AI_SESSION, node).export(scene.world)

                        AI_SESSION.replace_node(old_node, new_node)

                        new_node.set_string("name", unique_name)

        # Update everything else
        if depsgraph.id_type_updated("OBJECT"):
            light_data_needs_update = False
            polymesh_data_needs_update = False

            for update in reversed(depsgraph.updates):
                if isinstance(update.id, bpy.types.Light) or hasattr(update.id, "data") and isinstance(update.id.data.arnold, ArnoldLight):
                    light_data_needs_update = True
                elif isinstance(update.id, btoa.BTOA_CONVERTIBLE_TYPES) and update.is_updated_geometry:
                    polymesh_data_needs_update = True

                if isinstance(update.id, bpy.types.Object):
                    unique_name = utils.get_unique_name(update.id)
                    node = AI_SESSION.get_node_by_name(unique_name)

                    if update.id.type == 'LIGHT':
                        if update.is_updated_transform or light_data_needs_update:
                            btoa.LightExporter(AI_SESSION, node).export(update.id)

                    elif polymesh_data_needs_update:
                        btoa.PolymeshExporter(AI_SESSION, node).export(update.id, interactive=True)

                    # Transforms for lights have to be handled brute-force by the LightExporter to
                    # account for size and other parameters
                    if update.is_updated_transform and update.id.type != 'LIGHT':
                        node.set_matrix("matrix", utils.flatten_matrix(update.id.matrix_world))

                # Update world material if rotation controller changed
                rotation_controller = scene.world.arnold.rotation_controller
                if rotation_controller and update.id.name == rotation_controller.name:
                    unique_name = utils.get_unique_name(scene.world)
                    old_node = AI_SESSION.get_node_by_name(unique_name)

                    if old_node.is_valid():
                        new_node = btoa.WorldExporter(AI_SESSION, node).export(scene.world)

                        AI_SESSION.replace_node(old_node, new_node)

                        new_node.set_string("name", unique_name)

        AI_SESSION.restart()

    def view_draw(self, context, depsgraph):
        global AI_SESSION
        global AI_FRAMEBUFFER

        assert AI_SESSION
        
        region = context.region
        dimensions = region.width, region.height

        # Check to see if viewport camera changed
        bl_camera = utils.get_viewport_camera_object(context)

        if AI_SESSION.cache.viewport_camera.redraw_required(bl_camera):
            self.tag_update()

        if AI_FRAMEBUFFER and (dimensions != AI_FRAMEBUFFER.get_dimensions(scaling=False) or float(depsgraph.scene.arnold.viewport_scale) != AI_FRAMEBUFFER.scale):
            AI_SESSION.update_viewport_dimensions = True
            self.tag_update()
            
        if AI_FRAMEBUFFER.requires_update:
            AI_FRAMEBUFFER.tag_update()

        gpu.state.blend_set('ALPHA_PREMULT')
        self.bind_display_space_shader(depsgraph.scene)

        AI_FRAMEBUFFER.draw()

        self.unbind_display_space_shader()
        gpu.state.blend_set('NONE')

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
