import bpy
from bpy.types import NodeSocket
from bpy.props import FloatVectorProperty

from .ainodesocket import AiNodeSocket
from .constants import Color

class AiNodeSocketVector(NodeSocket, AiNodeSocket):
    bl_label = "Vector",
    color = Color.mapping_3d
    default_type = "VECTOR"

    default_value: FloatVectorProperty()

    def export_default(self):
        return self.default_value, self.default_type

classes = (
    AiNodeSocketVector,
)
register, unregister = bpy.utils.register_classes_factory(classes)