import bpy
from bpy.types import NodeSocket
from bpy.props import *
from .ainodesocket import AiNodeSocket, SocketColor
from ...bridge.types import VectorData

class AiNodeSocketVector(NodeSocket, AiNodeSocket):
    bl_label = "Vector"
    color = SocketColor.VECTOR

    default_value: FloatVectorProperty()
    show_value: BoolProperty(default=False)

    def draw_prop(self, context, layout, node, text):
        if self.show_value:
            col = layout.column()
            col.prop(self, "default_value", text=text)
        else:
            row = layout.row(align=True)
            row.label(text=text)
            
    def export_default(self):
        return VectorData(self.default_value)

classes = (
    AiNodeSocketVector,
)
register, unregister = bpy.utils.register_classes_factory(classes)