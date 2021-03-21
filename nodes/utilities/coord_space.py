from bpy.types import Node
from ..base import ArnoldNode

class AiCoordSpace(Node, ArnoldNode):
    bl_label = "Coordinate Space"
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new("AiNodeSocketCoord", "Object")
        self.outputs.new("AiNodeSocketCoord", "World").default_value = "world"
        self.outputs.new("AiNodeSocketCoord", "Pref").default_value = "pref"
        self.outputs.new("AiNodeSocketCoord", "UV").default_value = "uv"

def register():
    from bpy.utils import register_class
    register_class(AiCoordSpace)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiCoordSpace)