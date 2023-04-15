import arnold
import bpy
import numpy as np

from .bridge.driver import *
from .bridge import export
from .bridge import session
from .bridge import utils

class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'ARNOLD'
    bl_label = 'Arnold'
    bl_use_postprocess = True

    def __init__(self):
        session.start()

    def export(self, depsgraph, ipr=False, region=None):
        # Export universe options

        # Export scene objects
        for inst in depsgraph.object_instances:
            if not inst.is_instance:
                if isinstance(inst.object.data, bpy.types.Mesh):
                    export.MeshData.to_arnold(inst.object, depsgraph.scene)
                else:
                    import arnold
                    camera = arnold.AiNode('persp_camera')
                    camdata = export.ObjectData.init_from_object(inst.object)
                    arnold.AiNodeSetMatrix(camera, 'matrix', arnold.AtMatrix(*camdata.transform))
        
        # Set up AOVs
        scene = depsgraph.scene
        aovs = depsgraph.view_layer.arnold.aovs
        enabled_aovs = [aovs.beauty] # if ipr else aovs.enabled_aovs

        default_filter = arnold.AiNode(scene.arnold.filter_type)
        arnold.AiNodeSetStr(default_filter, 'name', 'btoa_default_filter')
        arnold.AiNodeSetFlt(default_filter, 'width', scene.arnold.filter_width)

        outputs = arnold.AiArrayAllocate(len(enabled_aovs), 1, arnold.AI_TYPE_STRING)
        
        for i, aov in enumerate(enabled_aovs):
            filter_type = 'btoa_default_filter'

            if aov.name == 'Z':
                closest_filter = arnold.AiNode('closest_filter')
                arnold.AiNodeSetStr(closest_filter, 'name', 'btoa_closest_filter')
                arnold.AiNodeSetFlt(closest_filter, 'width', scene.arnold.filter_width)

                filter_type = 'btoa_closest_filter'
            
            arnold.AiArraySetStr(outputs, i, f'{aov.ainame} {aov.pixel_type} {filter_type} btoa_driver')

        options = arnold.AiUniverseGetOptions()
        arnold.AiNodeSetArray(options, 'outputs', outputs)

        arnold.AiRenderAddInteractiveOutput(None, 0)
    
    def update(self, data, depsgraph):
        self.export(depsgraph)

    def render(self, depsgraph):
        engine = self

        def update_render_result(buffer):
            render = depsgraph.scene.render
            view_layer = depsgraph.view_layer
            rdata = buffer.contents

            if render.use_border:
                min_x, min_y, max_x, max_y = options.get_render_region()
            else:
                min_x, min_y, max_x, max_y = 0, 0, *utils.get_render_resolution(depsgraph)

            x = rdata.x - min_x
            y = max_y - rdata.y - rdata.height

            result = engine.begin_result(x, y, rdata.width, rdata.height, layer=view_layer.name)

            for i in range(0, rdata.count):
                aov = rdata.aovs[i]
                name = 'Combined' if aov.name == b'RGBA' else aov.name.decode()
                pixels = np.ctypeslib.as_array(aov.data, shape=(rdata.width * rdata.height, aov.channels))
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

        cb = ArnoldDisplayCallback(update_render_result)
        driver = arnold.AiNode("btoa_display_driver")
        arnold.AiNodeSetStr(driver, "name", "btoa_driver")
        arnold.AiNodeSetPtr(driver, "callback", cb)

        session.render()

def register():
    bpy.utils.register_class(ArnoldRenderEngine)

def unregister():
    bpy.utils.unregister_class(ArnoldRenderEngine)