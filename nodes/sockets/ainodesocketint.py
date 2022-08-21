import bpy
from bpy.types import NodeSocket
from bpy.props import IntProperty
from .ainodesocket import AiNodeSocket, SocketColor

class AiNodeSocketInt(AiNodeSocket):
    default_type = 'INT'
    color = SocketColor.FLOAT

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

class AiNodeSocketSkydomeResolution(NodeSocket, AiNodeSocketInt):
    default_value: IntProperty(min=4, default=1000)
    slider = False

classes = (
    AiNodeSocketIntUnbounded,
    AiNodeSocketIntPositive,
    AiNodeSocketIntAboveOne,
    AiNodeSocketSkydomeResolution
)
register, unregister = bpy.utils.register_classes_factory(classes)