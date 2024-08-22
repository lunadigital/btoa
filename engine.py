import bpy
import gpu
import numpy
import sys
import time
import math

from arnold import *

from . import bridge

class RenderViewManager:
    def __init__(self):
        self.views = {}

    def add(self, space):
        self.views[space.uuid] = space.shading.type

    def exists(self, space):
        return space.uuid in self.views.keys()
    
    def render_exited(self, space):
        return self.views[space.uuid] != space.shading.type and space.shading.type != "RENDERED"

class ArnoldRenderMonitor(bpy.types.Operator):
    """Used to detect when a user exits IPR rendering"""
    bl_idname = "wm.ai_render_monitor"
    bl_label = "Arnold Render Monitor"

    _timer = None
    views = RenderViewManager()

    def modal(self, context, event):
        if event.type == 'TIMER':
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    space = area.spaces[0]

                    if not self.views.exists(space):
                        self.views.add(space)
                    
                    if self.views.render_exited(space) and ArnoldRender.active:
                        ArnoldRender.ai_end()
                        self.cancel(context)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        return {'CANCELLED'}

def start_shading_monitor():
    bpy.ops.wm.ai_render_monitor('INVOKE_DEFAULT')

class ArnoldExport(bpy.types.RenderEngine):
    def __init__(self):
        self.is_viewport = False

    def ai_abort(self):
        AiRenderAbort(None)

    @staticmethod
    def ai_end(self=None):
        AiRenderInterrupt(None, AI_BLOCKING)
        AiRenderEnd(None)
        AiEnd()
    
    def ai_destroy(self, node):
        AiNodeDestroy(node.data)
    
    def ai_export(self, depsgraph, context=None):
        options = bridge.UniverseOptions()
        options.export(depsgraph, context)

        # Create the camera
        # If this is a viewport render, we must recreate the camera
        # object from `context`
        cdata = bridge.get_viewport_camera_object(context) if context else depsgraph.scene.camera.evaluated_get(depsgraph)
        camera = bridge.ArnoldCamera(frame_set=self.frame_set).from_datablock(depsgraph, cdata)
        options.set_pointer('camera', camera)

        # Materials
        materials = set()

        for obj in depsgraph.objects:
            if isinstance(obj.data, bridge.BTOA_CONVERTIBLE_TYPES):
                eval_obj = obj.evaluated_get(depsgraph)
                
                for slot in eval_obj.material_slots:
                    if slot.material:
                        materials.add(slot.material)
        
        for mat in materials:
            ntree = mat.arnold.node_tree

            if ntree and ntree.has_surface():
                shader = ntree.export_active_surface()
                shader.set_string("name", mat.name)
                shader.set_uuid(mat.uuid)
        
        shader = bridge.ArnoldNode("facing_ratio")
        shader.set_string("name", "BTOA_MISSING_SHADER")

        # Geometry and lights
        for ob in depsgraph.object_instances:
            if isinstance(ob.object.data, bridge.BTOA_CONVERTIBLE_TYPES):
                bridge.ArnoldPolymesh(frame_set=self.frame_set).from_datablock(depsgraph, ob)
            elif isinstance(ob.object.data, bpy.types.Light):
                bridge.ArnoldLight(frame_set=self.frame_set).from_datablock(depsgraph, ob)

        # World
        if depsgraph.scene.world.arnold.node_tree:
            bridge.ArnoldWorld().from_datablock(depsgraph.scene.world)

        # AOVs
        scene = depsgraph.scene
        aovs = depsgraph.view_layer.arnold.aovs
        enabled_aovs = [aovs.beauty] if self.is_viewport else aovs.enabled_aovs

        default_filter = bridge.ArnoldNode(scene.arnold.filter_type)
        default_filter.set_string("name", "btoa_default_filter")
        default_filter.set_float("width", scene.arnold.filter_width)

        outputs = bridge.ArnoldArray()
        outputs.allocate(len(enabled_aovs), 1, 'STRING')

        for aov in enabled_aovs:
            filter_type = "btoa_default_filter"

            if aov.name in ('Z', 'N', 'P'):
                closest_filter = bridge.ArnoldNode("closest_filter")
                closest_filter.set_string("name", "btoa_closest_filter")
                filter_type = "btoa_closest_filter"

            outputs.set_string(enabled_aovs.index(aov), f"{aov.ainame} {aov.pixel_type} {filter_type} btoa_driver")

        options.set_array("outputs", outputs)
        AiRenderAddInteractiveOutput(None, 0)
        
        # TODO
        '''
        # Color Management
        color_manager = ArnoldColorManager()

        if 'OCIO' in os.environ:
            ocio = os.getenv('OCIO')
        else:
            install_dir = os.path.dirname(bpy.app.binary_path)
            major, minor, fix = bpy.app.version
            
            if sys.platform.startswith('linux') and not Path(install_dir).joinpath(f'{major}.{minor}', 'datafiles', 'colormanagement').exists():
                install_dir = "/usr/share/blender"
            
            ocio = os.path.join(install_dir, f'{major}.{minor}', 'datafiles', 'colormanagement', 'config.ocio')

        color_manager.set_string('config', ocio)
        options.set_pointer('color_manager', color_manager)
        '''
    
    def ai_free_buffer(self, buffer):
        rdata = buffer.contents

        for i in range(0, rdata.count):
            aov = rdata.aovs[i]
            AiFree(aov.data)
            
        AiFree(rdata.aovs)
        AiFree(buffer)

    def ai_render(self, callback):
        return AiRenderBegin(None, AI_RENDER_MODE_CAMERA, callback, None)

    def ai_render_restart(self):
        AiRenderRestart(None)
    
    def ai_render_pause(self):
        AiRenderInterrupt(None, AI_BLOCKING)
    
    def ai_replace_node(self, old, new):
        AiNodeReplace(old.data, new.data, True)

class ArnoldRender(ArnoldExport):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_eevee_viewport = True
    bl_use_postprocess = True

    active = False

    def __init__(self):
        super().__init__()
        AiBegin(AI_SESSION_INTERACTIVE)

        self.depsgraph = None
        self.progress = 0
        self.progress_increment = 0
        self.framebuffer = None
        self.tag_viewport_resize = False
        self.viewport_camera = bridge.CameraCache()
        self.display_driver = bridge.DisplayDriver(self.ai_display_callback)

    def ai_display_callback(self, buffer):
        render = self.depsgraph.scene.render
        view_layer = self.depsgraph.view_layer_eval
        rdata = buffer.contents
        options = bridge.UniverseOptions()

        # Calculate X/Y image coordinates
        if render.use_border:
            min_x, min_y, max_x, max_y = options.get_render_region()
        else:
            min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

        x = rdata.x - min_x
        y = max_y - rdata.y - rdata.height

        # Handle render result
        if self.is_viewport:
            aov = rdata.aovs[0] # Get beauty AOV
            pixels = numpy.ctypeslib.as_array(aov.data, shape=(rdata.width * rdata.height, aov.channels))
            self.framebuffer.write_bucket(x, y, rdata.width, rdata.height, pixels.flatten())
            self.tag_redraw()
        else:
            result = self.begin_result(x, y, rdata.width, rdata.height, layer=view_layer.name)
            
            for i in range(0, rdata.count):
                aov = rdata.aovs[i]
                name = 'Combined' if aov.name == b'RGBA' else aov.name.decode()
                pixels = numpy.ctypeslib.as_array(aov.data, shape=(rdata.width * rdata.height, aov.channels))
                result.layers[0].passes[name].rect = pixels
        
            self.end_result(result)
            self.update_result(result)

        self.ai_free_buffer(buffer)
        
        # Update progress counter
        self.progress += self.progress_increment
        self.update_progress(self.progress)

        if self.test_break():
            self.ai_abort()

    def ai_status_callback(self, private_data, update_type, display_output):
        status = bridge.FAILED

        if update_type == int(bridge.INTERRUPTED):
            status = bridge.PAUSED
        elif update_type == int(bridge.BEFORE_PASS):
            status = bridge.RENDERING
        elif update_type == int(bridge.DURING_PASS):
            status = bridge.RENDERING
        elif update_type == int(bridge.AFTER_PASS):
            status = bridge.RENDERING
        elif update_type == int(bridge.RENDER_FINISHED):
            status = bridge.RENDER_FINISHED
        elif update_type == int(bridge.PAUSED):
            status = bridge.RESTARTING

        return int(status)

    def update(self, data, depsgraph):
        self.ai_export(depsgraph)

    def render(self, depsgraph):
        self.depsgraph = depsgraph

        # Set up render passes
        aovs = depsgraph.view_layer.arnold.aovs

        for aov in aovs.enabled_aovs:
            if aov.name == "Beauty":
                continue
            
            self.add_pass(aov.ainame, aov.channels, aov.chan_id, layer=depsgraph.view_layer_eval.name)
        
        # Calculate progress increment
        options = bridge.UniverseOptions()
        width, height = options.get_render_resolution()
        bucket_size = options.get_int("bucket_size")

        h_buckets = math.ceil(width / bucket_size)
        v_buckets = math.ceil(height / bucket_size)
        total_buckets = h_buckets * v_buckets

        self.progress = 0
        self.progress_increment = 1 / total_buckets

        # Render
        result = self.ai_render(self.ai_status_callback)
        if result == AI_SUCCESS.value:
            status = AiRenderGetStatus(None)
            while status not in (AI_RENDER_STATUS_FINISHED.value, AI_RENDER_STATUS_FAILED.value):
                time.sleep(0.001)
                status = AiRenderGetStatus(None)
        
        # Cleanup
        self.ai_end()
        self.depsgraph = None

    def view_update(self, context, depsgraph):
        region = context.region
        scene = depsgraph.scene

        # The only time self.is_viewport would be false
        # for a viewport/IPR render would be the first
        # time this function runs, so we can use it to
        # check if the render is running or not.
        if not self.is_viewport:
            ArnoldRender.active = self.is_viewport = True
            self.depsgraph = depsgraph
            self.total_objects = len(context.scene.objects)
            self.framebuffer = bridge.FrameBuffer((region.width, region.height), float(scene.arnold.viewport_scale))

            start_shading_monitor()
            self.ai_export(depsgraph, context)
            self.ai_render(self.ai_status_callback)
        
        self.ai_render_pause()

        if scene.arnold.preview_pause:
            return
        
        # Update viewport dimensions
        if self.tag_viewport_resize:
            self.tag_viewport_resize = False

            options = bridge.UniverseOptions()
            options.set_int("xres", int(region.width * float(scene.arnold.viewport_scale)))
            options.set_int("yres", int(region.height * float(scene.arnold.viewport_scale)))

            self.framebuffer = bridge.FrameBuffer((region.width, region.height), float(scene.arnold.viewport_scale))

        # Update viewport camera
        node = bridge.get_node_by_name("BTOA_VIEWPORT_CAMERA")
        cdata = bridge.get_viewport_camera_object(context)

        if node.type_is(cdata.data.arnold.camera_type):
            bridge.ArnoldCamera(node, self.frame_set).from_datablock(depsgraph, cdata)
        else:
            new = bridge.ArnoldCamera(frame_set=self.frame_set).from_datablock(depsgraph, cdata)
            self.ai_replace_node(node, new)
            new.set_string("name", cdata.name)
        
        self.viewport_camera.sync(cdata)

        # Update shaders
        if depsgraph.id_type_updated("MATERIAL"):
            for update in reversed(depsgraph.updates):
                mat = bridge.get_parent_material_from_nodetree(update.id)
                world_ntree = scene.world.arnold.node_tree

                if mat:
                    old = bridge.get_node_by_uuid(mat.original.uuid)
                    surface, volume, displacement = update.id.export()
                    new = surface.value

                    if old:
                        self.ai_replace_node(old, new)
                    
                    new.set_string("name", mat.name)
                    new.set_uuid(mat.original.uuid)
                
                elif world_ntree and update.id.name == world_ntree.name:
                    # This code is repeated in view_draw() below
                    # Consider cleaning this up
                    old = bridge.get_node_by_uuid(scene.world.uuid)

                    if old:
                        new = bridge.ArnoldWorld().from_datablock(scene.world)
                        self.ai_replace_node(old, new)
                        new.set_string("name", scene.world.name)

        # Update everything else
        if depsgraph.id_type_updated("OBJECT"):
            for update in reversed(depsgraph.updates):
                light_data_needs_update = False
                polymesh_data_needs_update = False

                if isinstance(update.id, bpy.types.Scene):
                    options = bridge.UniverseOptions()
                    options.export(depsgraph, context)

                if hasattr(update.id, "data"):
                    if isinstance(update.id.data, bpy.types.Light):
                        light_data_needs_update = True
                    elif isinstance(update.id.data, bridge.BTOA_CONVERTIBLE_TYPES) and update.is_updated_geometry:
                        polymesh_data_needs_update = True

                if isinstance(update.id, bpy.types.Object):
                    node = bridge.get_node_by_uuid(update.id.uuid)

                    if update.id.type == "LIGHT" and (update.is_updated_transform or light_data_needs_update):
                        bridge.ArnoldLight(node, self.frame_set).from_datablock(depsgraph, update)
                    elif polymesh_data_needs_update:
                        bridge.ArnoldPolymesh(node, self.frame_set).from_datablock(depsgraph, update)
                    
                    # Transforms for lights have to be handled brute-force by the LightExporter to
                    # account for size and other parameters
                    if node and update.is_updated_transform and update.id.type != 'LIGHT':
                        node.set_matrix("matrix", bridge.flatten_matrix(update.id.matrix_world))

                    # Force update world material in case we have any physical sky textures that
                    # reference the rotation of an object in the scene.
                    old = bridge.get_node_by_uuid(scene.world.uuid)

                    if old:
                        new = bridge.ArnoldWorld().from_datablock(scene.world)
                        self.ai_replace_node(old, new)
                        new.set_string("name", scene.world.name)

        # Check for deleted objects
        if len(depsgraph.object_instances) < self.total_objects:
            uuids = [instance.uuid for instance in depsgraph.object_instances]

            iterator = AiUniverseGetNodeIterator(None, AI_NODE_SHAPE | AI_NODE_LIGHT)

            while not AiNodeIteratorFinished(iterator):
                node = AiNodeIteratorGetNext(iterator)
                
                if AiNodeGetStr(node, 'btoa_id') not in uuids and not AiNodeIs(node, 'skydome_light'):
                    AiNodeDestroy(node)

            AiNodeIteratorDestroy(iterator)
        
        self.total_objects = len(context.scene.objects)

        self.ai_render_restart()

    def view_draw(self, context, depsgraph):   
        region = context.region
        dimensions = region.width, region.height

        # Check if viewport camera changed
        cdata = bridge.get_viewport_camera_object(context)

        if self.viewport_camera.redraw_required(cdata):
            self.tag_update()

        # Check if framebuffer is resized
        if self.framebuffer and (dimensions != self.framebuffer.get_dimensions(scaling=False) or float(depsgraph.scene.arnold.viewport_scale) != self.framebuffer.scale):
            self.tag_viewport_resize = True
            self.tag_update()

        if self.framebuffer.requires_update:
            self.framebuffer.tag_update()

        # Draw the pixels to screen
        gpu.state.blend_set("ALPHA_PREMULT")
        self.bind_display_space_shader(depsgraph.scene)

        self.framebuffer.draw()

        self.unbind_display_space_shader()
        gpu.state.blend_set("NONE")

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

    panels = set()
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES and panel.__name__ not in exclude_panels:
            panels.add(panel)

    return panels

def register():
    bpy.utils.register_class(ArnoldRender)
    bpy.utils.register_class(ArnoldRenderMonitor)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add(ArnoldRender.bl_idname)

def unregister():
    bpy.utils.unregister_class(ArnoldRenderMonitor)
    bpy.utils.unregister_class(ArnoldRender)

    for panel in get_panels():
        if ArnoldRender.bl_idname in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove(ArnoldRender.bl_idname)

    # TODO
    #ArnoldRender.unregister_outliner_context_menu_draw()
