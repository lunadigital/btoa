from .exporter import Exporter
from .node import ArnoldNode
from .polymesh import ArnoldPolymesh
from .universe_options import UniverseOptions
from .constants import BTOA_CONVERTIBLE_TYPES

import arnold
import numpy
import time

class Session:
    def __init__(self):
        self.reset()

    def abort(self):
        arnold.AiRenderAbort()

    def end(self):
        if self.is_interactive:
            print("TRYING TO END RENDER")
            result = arnold.AiRenderEnd()
            if result != arnold.AI_SUCCESS:
                print("Something went wrong")
        
        print("TRYING TO SHUT DOWN RESOURCES")
        arnold.AiEnd()

    def export(self, engine, depsgraph):
        self.depsgraph = depsgraph

        exporter = Exporter()
        exporter.export(self, engine, depsgraph)

    def free_buffer(self, buffer):
        arnold.AiFree(buffer)

    def get_node_by_name(self, name):
        ainode = arnold.AiNodeLookUpByName(name)

        node = ArnoldNode()
        node.set_data(ainode)

        return node

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
        self.depsgraph = None
        self.is_interactive = False
        self.is_running = False

    def start(self, interactive=False):
        self.is_running = True
        self.is_interactive = interactive

        render_mode = arnold.AI_SESSION_INTERACTIVE if interactive else arnold.AI_SESSION_BATCH
        arnold.AiBegin(render_mode)