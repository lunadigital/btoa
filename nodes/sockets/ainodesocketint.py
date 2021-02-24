import bpy
from bpy.types import NodeSocket
from bpy.props import IntProperty

from .ainodesocket import AiNodeSocket
from .constants import Color

class AiNodeSocketInt(AiNodeSocket):
    default_type = 'INT'
    color = Color.float_texture

    def export_default(self):
        return self.default_value, self.default_type

class AiNodeSocketIntUnbounded(NodeSocket, AiNodeSocketInt):
    default_value: IntProperty(
        soft_min=-5,
        soft_max=5
    )

class AiNodeSocketIntPositive(NodeSocket, AiNodeSocketInt):
    default_value: IntProperty(
        min=0,
        soft_max=5
    )

class AiNodeSocketIntAboveOne(NodeSocket, AiNodeSocketInt):
    default_value: IntProperty(
        min=1,
        soft_max=5
    )

classes = (
    AiNodeSocketIntUnbounded,
    AiNodeSocketIntPositive,
    AiNodeSocketIntAboveOne,
)
register, unregister = bpy.utils.register_classes_factory(classes)