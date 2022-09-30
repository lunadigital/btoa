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

def update_viewport(buffer):
    global AI_SESSION
    global AI_FRAMEBUFFER
    global AI_DRIVER_UPDATE_VIEWPORT

    rdata = buffer.contents
    options = btoa.UniverseOptions()
    min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

    x = rdata.x - min_x
    y = max_y - rdata.y - rdata.height

    aov = rdata.aovs[0] # Get beauty aov
    pixels = numpy.ctypeslib.as_array(aov.data, shape=(rdata.width * rdata.height, aov.channels))
    AI_FRAMEBUFFER.write_bucket(x, y, rdata.width, rdata.height, pixels.flatten())
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
        self.total_objects_in_ipr = 0

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

        def update_render_result(buffer):
            render = depsgraph.scene.render
            cache = engine.session.cache
            rdata = buffer.contents

            if render.use_border:
                min_x, min_y, max_x, max_y = options.get_render_region()
            else:
                min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

            x = rdata.x - min_x
            y = max_y - rdata.y - rdata.height

            result = engine.begin_result(x, y, rdata.width, rdata.height, layer=cache.view_layer.name)

            for i in range(0, rdata.count):
                aov = rdata.aovs[i]
                name = 'Combined' if aov.name == b'RGBA' else aov.name.decode()
                pixels = numpy.ctypeslib.as_array(aov.data, shape=(rdata.width * rdata.height, aov.channels))
                result.layers[0].passes[name].rect = pixels

            engine.end_result(result)
            engine.session.free_buffer(buffer)

            engine.update_result(result)

            # Update progress counter
            engine.progress += engine._progress_increment
            engine.update_progress(engine.progress)

            if engine.test_break():
                engine.session.abort()
                engine.end_result(result, cancel=True)

        cb = btoa.ArnoldDisplayCallback(update_render_result)
        driver = btoa.ArnoldNode("btoa_display_driver")
        driver.set_string("name", "btoa_driver")
        driver.set_pointer("callback", cb)

        # Set up custom render passes
        aovs = depsgraph.view_layer.arnold.aovs

        for aov in aovs.enabled_aovs:
            if aov.name == "Beauty":
                continue
            
            self.add_pass(aov.ainame, aov.channels, aov.chan_id, layer=depsgraph.view_layer_eval.name)

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
            self.total_objects_in_ipr = len(context.scene.objects)

            AI_FRAMEBUFFER = btoa.FrameBuffer((region.width, region.height), float(scene.arnold.viewport_scale))

            AI_SESSION = self.session
            AI_SESSION.start(interactive=True)
            AI_SESSION.export(self, depsgraph, prefs, context)

            global AI_ENGINE_TAG_REDRAW
            AI_ENGINE_TAG_REDRAW = self.tag_redraw

            display_driver = btoa.ArnoldNode("btoa_display_driver")
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
                    old_node = AI_SESSION.get_node_by_uuid(material.original.uuid)

                    if old_node.is_valid:
                        surface, volume, displacement = update.id.export()
                        new_node = surface[0]

                        AI_SESSION.replace_node(old_node, new_node)

                        # We have to rename the node AFTER we swap them to
                        # avoid memory and session.get_node_by_name() issues
                        new_node.set_string("name", material.name)
                        new_node.set_uuid(material.original.uuid)

                elif world_ntree and update.id.name == world_ntree.name:
                    # This code is repeated in view_draw() below
                    # Consider cleaning this up
                    old_node = AI_SESSION.get_node_by_uuid(scene.world.uuid)

                    if old_node.is_valid:
                        new_node = btoa.WorldExporter(AI_SESSION, node).export(scene.world)
                        AI_SESSION.replace_node(old_node, new_node)
                        new_node.set_string("name", scene.world.name)

        # Update everything else
        if depsgraph.id_type_updated("OBJECT"):
            light_data_needs_update = False
            polymesh_data_needs_update = False

            for update in reversed(depsgraph.updates):
                if isinstance(update.id, bpy.types.Light):
                    light_data_needs_update = True
                elif isinstance(update.id, btoa.BTOA_CONVERTIBLE_TYPES) and update.is_updated_geometry:
                    polymesh_data_needs_update = True

                if isinstance(update.id, bpy.types.Object):
                    node = AI_SESSION.get_node_by_uuid(update.id.uuid)
                    
                    if update.id.type == 'LIGHT':
                        if update.is_updated_transform or light_data_needs_update:
                            btoa.LightExporter(AI_SESSION, node).export(update)

                    elif polymesh_data_needs_update:
                        btoa.PolymeshExporter(AI_SESSION, node).export(update)

                    # Transforms for lights have to be handled brute-force by the LightExporter to
                    # account for size and other parameters
                    if update.is_updated_transform and update.id.type != 'LIGHT':
                        node.set_matrix("matrix", utils.flatten_matrix(update.id.matrix_world))

                # Update world material if rotation controller changed
                rotation_controller = scene.world.arnold.rotation_controller
                if rotation_controller and update.id.name == rotation_controller.name:
                    old_node = AI_SESSION.get_node_by_uuid(scene.world.uuid)

                    if old_node.is_valid:
                        new_node = btoa.WorldExporter(AI_SESSION, node).export(scene.world)
                        AI_SESSION.replace_node(old_node, new_node)
                        new_node.set_string("name", scene.world.name)

        # Check for deleted objects
        if len(depsgraph.object_instances) < self.total_objects_in_ipr:
            uuids = [instance.uuid for instance in depsgraph.object_instances]

            iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_SHAPE | arnold.AI_NODE_LIGHT)

            while not arnold.AiNodeIteratorFinished(iterator):
                node = arnold.AiNodeIteratorGetNext(iterator)
                
                if arnold.AiNodeGetStr(node, 'btoa_id') not in uuids and not arnold.AiNodeIs(node, 'skydome_light'):
                    arnold.AiNodeDestroy(node)

            arnold.AiNodeIteratorDestroy(iterator)
        
        self.total_objects_in_ipr = len(context.scene.objects)

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

    def update_render_passes(self, scene=None, renderlayer=None):
        self.register_pass(scene, renderlayer, "Combined", 4, "RGBA", 'COLOR')

        aovs = renderlayer.arnold.aovs

        for aov in aovs.enabled_aovs:
            if aov.name == "Beauty":
                continue 
                
            self.register_pass(scene, renderlayer, aov.ainame, aov.channels, aov.chan_id, aov.pass_type)

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
