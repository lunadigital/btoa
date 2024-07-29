import bpy
import numpy
import time

from arnold import *

from . import bridge

class ArnoldExport(bpy.types.RenderEngine):
    def __init__(self):
        self.is_viewport = False

    def ai_abort(self):
        AiRenderAbort(None)

    def ai_end(self):
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
        camera = bridge.CameraExporter(depsgraph).export(cdata)
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
                bridge.ArnoldPolymesh(ob.object.name).from_datablock(depsgraph, ob)
            elif isinstance(ob.object.data, bpy.types.Light):
                pass

        '''
        # World
        if depsgraph.scene.world.arnold.node_tree:
            WorldExporter().export(depsgraph.scene.world)
        '''

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
    
    def ai_get_node_by_name(self, name):
        ainode = AiNodeLookUpByName(None, name)

        node = bridge.ArnoldNode()
        node.set_data(ainode)

        return node
    
    def ai_get_all_by_uuid(self, uuid):
        iterator = AiUniverseGetNodeIterator(None, AI_NODE_SHAPE | AI_NODE_LIGHT | AI_NODE_SHADER)
        result = []

        while not AiNodeIteratorFinished(iterator):
            ainode = AiNodeIteratorGetNext(iterator)
            
            if AiNodeGetStr(ainode, 'btoa_id') == uuid:
                node = bridge.ArnoldNode()
                node.set_data(ainode)
                result.append(node)
        
        return result
    
    def ai_get_node_by_uuid(self, uuid):
        iterator = AiUniverseGetNodeIterator(None, AI_NODE_SHAPE | AI_NODE_LIGHT | AI_NODE_SHADER)
        node = bridge.ArnoldNode()

        while not AiNodeIteratorFinished(iterator):
            ainode = AiNodeIteratorGetNext(iterator)
            btoa_id = AiNodeGetStr(ainode, 'btoa_id')
            
            if btoa_id == uuid:
                node.set_data(ainode)
                break
        
        return node

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

    def __init__(self):
        super().__init__()
        self.depsgraph = None
        self.progress = 0
        self.progress_increment = 0

        AiBegin(AI_SESSION_INTERACTIVE)

    def __del__(self):
        pass

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
        result = self.begin_result(x, y, rdata.width, rdata.height, layer=view_layer.name)

        for i in range(0, rdata.count):
            aov = rdata.aovs[i]
            name = 'Combined' if aov.name == b'RGBA' else aov.name.decode()
            pixels = numpy.ctypeslib.as_array(aov.data, shape=(rdata.width * rdata.height, aov.channels))
            result.layers[0].passes[name].rect = pixels
        
        self.end_result(result)
        self.ai_free_buffer(buffer)
        self.update_result(result)

        # Update progress counter
        self.progress += self.progress_increment
        self.update_progress(self.progress)

        if self.test_break():
            self.ai_abort()

    def ai_status_callback(self, private_data, update_type, display_output):
        # AI_ENGINE_TAG_REDRAW()
        status = bridge.FAILED

        if update_type == int(bridge.INTERRUPTED):
            status = bridge.PAUSED
        elif update_type == int(bridge.BEFORE_PASS):
            status = bridge.RENDERING
        elif update_type == int(bridge.DURING_PASS):
            status = bridge.RENDERING
        elif update_type == int(bridge.AFTER_PASS):
            status = bridge.RENDERING
            #AI_DRIVER_UPDATE_VIEWPORT = True
        elif update_type == int(bridge.RENDER_FINISHED):
            status = bridge.RENDER_FINISHED
            #AI_DRIVER_UPDATE_VIEWPORT = False
        elif update_type == int(bridge.PAUSED):
            status = bridge.RESTARTING
        elif update_type == int(bridge.ERROR):
            status = bridge.FAILED
            #AI_DRIVER_UPDATE_VIEWPORT = False

        return int(status)

    def update(self, data, depsgraph):
        self.ai_export(depsgraph)

    def render(self, depsgraph):
        self.depsgraph = depsgraph

        # Display driver callback
        callback = bridge.ArnoldDisplayCallback(self.ai_display_callback)
        driver = bridge.ArnoldNode("btoa_display_driver")
        driver.set_string("name", "btoa_driver")
        driver.set_pointer("callback", callback)

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

def register():
    bpy.utils.register_class(ArnoldRender)

    #for panel in get_panels():
    #    panel.COMPAT_ENGINES.add(ArnoldRenderEngine.bl_idname)

    # For some reason, there are a handful of classes that get 'ARNOLD'
    # added to COMPAT_ENGINES even though they're left out of the
    # list returned from get_panels(). Need to file a bug report
    # to Blender devs, but for now we'll brute-force remove it.
    #for panel in bpy.types.Panel.__subclasses__():
    #    if panel.__name__ == 'DATA_PT_light':
    #        panel.COMPAT_ENGINES.remove(ArnoldRender.bl_idname)

def unregister():
    bpy.utils.unregister_class(ArnoldRender)

    #for panel in get_panels():
    #    if ArnoldRenderEngine.bl_idname in panel.COMPAT_ENGINES:
    #        panel.COMPAT_ENGINES.remove(ArnoldRenderEngine.bl_idname)

    #ArnoldRender.unregister_outliner_context_menu_draw()
