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
            arnold.AiRenderInterrupt(arnold.AI_BLOCKING)
            arnold.AiRenderEnd()
        
        arnold.AiEnd()

    def export(self, engine, depsgraph):
        self.depsgraph = depsgraph
        self.is_updating = True

        exporter = Exporter()
        exporter.export(self, engine, depsgraph)

        self.is_updating = False

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
        self.depsgraph = None
        self.is_interactive = False
        self.is_running = False
        self.is_updating = False

    def restart(self):
        arnold.AiRenderRestart()
        self.is_running = True

    def start(self, interactive=False):
        self.is_running = True
        self.is_interactive = interactive

        render_mode = arnold.AI_SESSION_INTERACTIVE if interactive else arnold.AI_SESSION_BATCH
        arnold.AiBegin(render_mode)