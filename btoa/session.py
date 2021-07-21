from .exporter import Exporter
from .node import ArnoldNode
from .polymesh import ArnoldPolymesh
from .universe_options import UniverseOptions
from .constants import BTOA_CONVERTIBLE_TYPES

import arnold
import numpy

class Session:
    def __init__(self):
        self.reset()

    def abort(self):
        arnold.AiRenderAbort()

    def end(self):
        arnold.AiEnd()

    def export(self, engine, depsgraph):
        self.engine = engine
        self.depsgraph = depsgraph
        self.exporter = Exporter(self)

        self.exporter.export()

    def free_buffer(self, buffer):
        arnold.AiFree(buffer)

    def get_node_by_name(self, name):
        ainode = arnold.AiNodeLookUpByName(name)

        node = ArnoldNode()
        node.set_data(ainode)

        return node

    def render(self):
        arnold.AiRender(arnold.AI_RENDER_MODE_CAMERA)

    def reset(self):
        self.engine = None
        self.depsgraph = None
        self.exporter = None

    def start(self):
        arnold.AiBegin()
    


    