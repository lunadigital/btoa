import bpy
import gpu
import numpy
import time

from arnold import *

from . import bridge

from bl_ui.space_outliner import OUTLINER_MT_collection_view_layer


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_viewport = False
        self.display_driver = None

    def ai_abort(self):
        AiRenderAbort(None)

    def ai_begin(self):
        AiBegin(AI_SESSION_INTERACTIVE)
        self.display_driver = bridge.DisplayDriver(self.ai_display_callback)

    @staticmethod
    def ai_end(self=None):
        AiRenderInterrupt(None, AI_BLOCKING)
        AiRenderEnd(None)
        bridge.clear_node_cache()
        AiEnd()

    def ai_destroy(self, node):
        AiNodeDestroy(node.data)

    def ai_export(self, depsgraph, context=None):
        self.ai_begin()

        options = bridge.UniverseOptions()
        options.export(depsgraph, context)

        # Create the camera
        # If this is a viewport render, we must recreate the camera
        # object from `context`
        cdata = bridge.get_viewport_camera_object(context) if context else depsgraph.scene.camera.evaluated_get(depsgraph)
        camera = bridge.ArnoldCamera(frame_set=self.frame_set).from_datablock(depsgraph, cdata)
        options.set_pointer('camera', camera)

        # Materials
        for db in depsgraph.ids:
            if isinstance(db, bpy.types.Material):
                ntree = db.arnold.node_tree

                if ntree and ntree.has_surface():
                    shader = ntree.export_active_surface()
                    shader.set_string("name", db.name)
                    shader.set_uuid(db.uuid)

        shader = bridge.ArnoldNode("facing_ratio")
        shader.set_string("name", "BTOA_MISSING_SHADER")

        # Geometry and lights
        for ob in depsgraph.object_instances:
            if isinstance(ob.object.data, bridge.BTOA_CONVERTIBLE_TYPES):
                bridge.ArnoldPolymesh(frame_set=self.frame_set).from_datablock(depsgraph, ob)
            elif isinstance(ob.object.data, bridge.BTOA_CURVES_TYPES):
                bridge.ArnoldCurves(frame_set=self.frame_set).from_datablock(depsgraph, ob)
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
    _outliner_context_menu_draw = None

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depsgraph = None
        self.pass_index = 0
        self.total_passes = 0
        self.framebuffer = None
        self.tag_viewport_resize = False
        self.viewport_camera = bridge.CameraCache()
        self.display_driver = None

    def ai_display_callback(self, buffer):
        try:
            # Check if the render engine is still valid
            if not hasattr(self, 'depsgraph') or self.depsgraph is None:
                return

            render = self.depsgraph.scene.render
            view_layer = self.depsgraph.view_layer_eval
            rdata = buffer.contents
            options = bridge.UniverseOptions()

            # Calculate X/Y image coordinates
            if render.use_border:
                min_x, min_y, max_x, max_y = options.get_render_region()
                region_height = max_y - min_y + 1
            else:
                min_x, min_y = 0, 0
                max_x, max_y = options.get_render_resolution()
                region_height = max_y

            x = rdata.x - min_x
            y = region_height - (rdata.y - min_y) - rdata.height

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

            self.ai_free_buffer(buffer)
            self.update_progress(self.pass_index / self.total_passes)

            if self.test_break():
                self.ai_abort()
        except ReferenceError:
            # Render engine was destroyed, ignore callback
            pass

    def ai_status_callback(self, private_data, update_type, update_info):
        try:
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

            info = update_info.contents
            self.pass_index = info.pass_index
            self.total_passes = info.total_passes

            return int(status)
        except ReferenceError:
            # Render engine was destroyed, ignore callback
            return int(bridge.FAILED)

    def ai_message_callback(self, logmask, severity, message, metadata, user):
        msg = AtPythonStringToStr(message)
        msg = msg.split("|")[1].lstrip()

        self.update_stats(msg, "")

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

        # Register message callback
        callback = AtMsgExtendedCallBack(self.ai_message_callback)
        cbid = AiMsgRegisterCallback(callback, AI_LOG_ALL, None)

        # Render
        result = self.ai_render(self.ai_status_callback)
        if result == AI_SUCCESS.value:
            status = AiRenderGetStatus(None)
            while status not in (AI_RENDER_STATUS_FINISHED.value, AI_RENDER_STATUS_FAILED.value):
                time.sleep(0.001)
                status = AiRenderGetStatus(None)

        # Cleanup
        AiMsgDeregisterCallback(cbid)
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
            updated_materials = set()

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

                    # Track which materials were updated for displacement refresh
                    updated_materials.add(mat.original.uuid)

                elif world_ntree and update.id.name == world_ntree.name:
                    old = bridge.get_node_by_uuid(scene.world.uuid)

                    if old:
                        new = bridge.ArnoldWorld().from_datablock(scene.world)
                        self.ai_replace_node(old, new)
                        new.set_string("name", scene.world.name)

            # Update displacement on meshes that use updated materials
            if updated_materials:
                for obj_inst in depsgraph.object_instances:
                    if isinstance(obj_inst.object.data, bridge.BTOA_CONVERTIBLE_TYPES) or isinstance(obj_inst.object.data, bridge.BTOA_CURVES_TYPES):
                        obj = obj_inst.instance_object if obj_inst.is_instance else obj_inst.object

                        # Check if object uses any updated material
                        needs_update = False
                        for slot in obj.material_slots:
                            if slot.material and slot.material.uuid in updated_materials:
                                needs_update = True
                                break

                        if needs_update:
                            # Get the polymesh node and reapply displacement
                            node = bridge.get_node_by_uuid(obj.uuid)
                            if node:
                                # Reapply displacement from materials
                                for slot in obj.material_slots:
                                    mat = slot.material
                                    if mat and mat.arnold.node_tree and mat.arnold.node_tree.has_displacement():
                                        disp_data = mat.arnold.node_tree.export_active_displacement()
                                        if disp_data and disp_data.type == bridge.types.ExportDataType.GROUP:
                                            disp_input, disp_padding, disp_height, disp_zero, disp_autobump = disp_data.value

                                            if disp_input.type == bridge.types.ExportDataType.NODE:
                                                node.set_pointer("disp_map", disp_input.value)
                                            if disp_padding.type == bridge.types.ExportDataType.FLOAT:
                                                node.set_float("disp_padding", disp_padding.value)
                                            if disp_height.type == bridge.types.ExportDataType.FLOAT:
                                                node.set_float("disp_height", disp_height.value)
                                            if disp_zero.type == bridge.types.ExportDataType.FLOAT:
                                                node.set_float("disp_zero_value", disp_zero.value)
                                            node.set_bool("disp_autobump", disp_autobump)
                                            break

        # Update everything else
        if depsgraph.id_type_updated("OBJECT"):
            # Determine if world needs re-export (only when it uses a rotation controller
            # that references an object in the scene, e.g. physical sky textures)
            world_needs_update = bool(scene.world.arnold.rotation_controller)

            for update in reversed(depsgraph.updates):
                light_data_needs_update = False
                polymesh_data_needs_update = False

                if isinstance(update.id, bpy.types.Scene):
                    options = bridge.UniverseOptions()
                    options.export(depsgraph, context)

                if hasattr(update.id, "data"):
                    if isinstance(update.id.data, bpy.types.Light):
                        light_data_needs_update = True
                    elif isinstance(update.id.data, bridge.BTOA_CONVERTIBLE_TYPES):
                        polymesh_data_needs_update = True
                    elif isinstance(update.id.data, bridge.BTOA_CURVES_TYPES):
                        polymesh_data_needs_update = True

                if isinstance(update.id, bpy.types.Object):
                    node = bridge.get_node_by_uuid(update.id.uuid)

                    if update.id.type == "LIGHT" and (update.is_updated_transform or light_data_needs_update):
                        bridge.ArnoldLight(node, self.frame_set).from_datablock(depsgraph, update)
                    elif update.id.type == "CURVES" and polymesh_data_needs_update:
                        bridge.ArnoldCurves(node, self.frame_set).from_datablock(depsgraph, update)
                    elif polymesh_data_needs_update:
                        bridge.ArnoldPolymesh(node, self.frame_set).from_datablock(depsgraph, update)

                    # Transforms for lights have to be handled brute-force by the LightExporter to
                    # account for size and other parameters
                    if node and update.is_updated_transform and update.id.type != 'LIGHT':
                        node.set_matrix("matrix", bridge.flatten_matrix(update.id.matrix_world))

            # Only re-export world shader if it uses a rotation controller object.
            # Previously this ran inside the per-object loop, causing N redundant
            # world re-exports for N object updates.
            if world_needs_update:
                old = bridge.get_node_by_uuid(scene.world.uuid)

                if old:
                    new = bridge.ArnoldWorld().from_datablock(scene.world)
                    self.ai_replace_node(old, new)
                    new.set_string("name", scene.world.name)

        # Sync Arnold universe with depsgraph visibility
        # Only perform the expensive visibility sync when objects were actually
        # added/removed/hidden. depsgraph.id_type_updated("OBJECT") covers
        # visibility toggles, collection changes, and object deletion.
        if depsgraph.id_type_updated("OBJECT"):
            # Build set of UUIDs that should be visible according to the depsgraph
            visible_uuids = set()
            for instance in depsgraph.object_instances:
                obj = instance.instance_object if instance.is_instance else instance.object
                visible_uuids.add(obj.uuid)

            # Build set of UUIDs currently in the Arnold universe
            existing_uuids = set()
            iterator = AiUniverseGetNodeIterator(None, AI_NODE_SHAPE | AI_NODE_LIGHT)

            while not AiNodeIteratorFinished(iterator):
                node = AiNodeIteratorGetNext(iterator)
                btoa_id = AiNodeGetStr(node, 'btoa_id')

                if btoa_id and not AiNodeIs(node, 'skydome_light'):
                    existing_uuids.add(btoa_id)

                    # Destroy nodes for objects no longer visible
                    if btoa_id not in visible_uuids:
                        bridge.uncache_node(btoa_id)
                        AiNodeDestroy(node)

            AiNodeIteratorDestroy(iterator)

            # Re-create nodes for objects that became visible again
            for ob in depsgraph.object_instances:
                obj = ob.instance_object if ob.is_instance else ob.object
                if obj.uuid not in existing_uuids:
                    if isinstance(ob.object.data, bridge.BTOA_CONVERTIBLE_TYPES):
                        bridge.ArnoldPolymesh(frame_set=self.frame_set).from_datablock(depsgraph, ob)
                    elif isinstance(ob.object.data, bridge.BTOA_CURVES_TYPES):
                        bridge.ArnoldCurves(frame_set=self.frame_set).from_datablock(depsgraph, ob)
                    elif isinstance(ob.object.data, bpy.types.Light):
                        bridge.ArnoldLight(frame_set=self.frame_set).from_datablock(depsgraph, ob)

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

    panels = set()
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and panel.__name__ not in exclude_panels:
            # Skip all Cycles-specific panels (they start with CYCLES_)
            if panel.__name__.startswith('CYCLES_'):
                continue
            # Skip all EEVEE-specific panels (they start with EEVEE_)
            if panel.__name__.startswith('EEVEE_'):
                continue
            # Skip NODE_ prefixed Cycles/EEVEE panels
            if panel.__name__.startswith('NODE_CYCLES_') or panel.__name__.startswith('NODE_EEVEE_'):
                continue

            # Only add panels that have CYCLES or BLENDER_EEVEE compatibility
            if 'CYCLES' in panel.COMPAT_ENGINES or 'BLENDER_EEVEE' in panel.COMPAT_ENGINES:
                panels.add(panel)

    return panels


def register():
    bpy.utils.register_class(ArnoldRender)
    bpy.utils.register_class(ArnoldRenderMonitor)

    panels = get_panels()

    print(f"\n=== Arnold Addon: Registering with {len(panels)} panels ===")

    # Add Arnold to compatible panels
    for panel in panels:
        panel.COMPAT_ENGINES.add(ArnoldRender.bl_idname)

    print("===\n")

    # Remove Arnold from DATA_PT_light
    for panel in bpy.types.Panel.__subclasses__():
        if panel.__name__ == "DATA_PT_light":
            if ArnoldRender.bl_idname in panel.COMPAT_ENGINES:
                panel.COMPAT_ENGINES.remove(ArnoldRender.bl_idname)


def unregister():
    bpy.utils.unregister_class(ArnoldRenderMonitor)
    bpy.utils.unregister_class(ArnoldRender)

    for panel in get_panels():
        if ArnoldRender.bl_idname in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove(ArnoldRender.bl_idname)

    ArnoldRender.unregister_outliner_context_menu_draw()
