import bpy
import arnold
import numpy
import time
import os

from .exporter import PolymeshExporter, CameraExporter, OptionsExporter, LightExporter

from .array import ArnoldArray
from .colormanager import ArnoldColorManager
from .node import ArnoldNode
from .polymesh import ArnoldPolymesh
from .universe_options import UniverseOptions
from .constants import BTOA_CONVERTIBLE_TYPES
from .session_cache import SessionCache
from . import utils as export_utils

class Session:
    def __init__(self):
        self.reset()

    def abort(self):
        arnold.AiRenderAbort()

    def end(self):
        if self.is_interactive:
            arnold.AiRenderInterrupt(arnold.AI_BLOCKING)
            arnold.AiRenderEnd()
        
        arnold.AiEnd()
    
    def destroy(self, node):
        arnold.AiNodeDestroy(node.data)

    def export(self, engine, depsgraph):
        self.cache.sync(engine, depsgraph)

        OptionsExporter(self).export(interactive=self.is_interactive)

        for instance in depsgraph.object_instances:
            ob = export_utils.get_object_data_from_instance(instance)

            if isinstance(ob.data, BTOA_CONVERTIBLE_TYPES):
                PolymeshExporter(self).export(ob)
            elif isinstance(ob.data, bpy.types.Light):
                LightExporter(self).export(ob)
            elif isinstance(ob.data, bpy.types.Camera) and ob.name == depsgraph.scene.camera.name:
                CameraExporter(self).export(ob)
        
        default_filter = ArnoldNode("gaussian_filter")
        default_filter.set_string("name", "gaussianFilter")

        options = UniverseOptions()

        outputs = ArnoldArray()
        outputs.allocate(1, 1, 'STRING')
        outputs.set_string(0, "RGBA RGBA gaussianFilter __display_driver")
        options.set_array("outputs", outputs)

        #color_manager = ArnoldColorManager()
        #color_manager.set_string("config", os.getenv("OCIO"))
        #options.set_pointer("color_manager", color_manager)

    def free_buffer(self, buffer):
        arnold.AiFree(buffer)

    def get_node_by_name(self, name):
        ainode = arnold.AiNodeLookUpByName(name)

        node = ArnoldNode()
        node.set_data(ainode)

        return node

    def pause(self):
        arnold.AiRenderInterrupt(arnold.AI_BLOCKING)
        self.is_running = False

    def render(self):
        result = arnold.AiRenderBegin()
        if result == arnold.AI_SUCCESS.value:
            status = arnold.AiRenderGetStatus()
            while status == arnold.AI_RENDER_STATUS_RENDERING.value:
                time.sleep(0.001)
                status = arnold.AiRenderGetStatus()
        
        result = arnold.AiRenderEnd()

        self.end()
        self.reset()

    def render_interactive(self, callback):
        render_mode = arnold.AI_RENDER_MODE_CAMERA
        private_data = None

        result = arnold.AiRenderBegin(render_mode, callback, private_data)
        if result != arnold.AI_SUCCESS.value:
            self.end()
            self.reset()

    def reset(self):
        self.is_interactive = False
        self.is_running = False
        self.cache = SessionCache()

    def restart(self):
        arnold.AiRenderRestart()
        self.is_running = True

    def start(self, interactive=False):
        self.is_running = True
        self.is_interactive = interactive

        render_mode = arnold.AI_SESSION_INTERACTIVE if interactive else arnold.AI_SESSION_BATCH
        arnold.AiBegin(render_mode)