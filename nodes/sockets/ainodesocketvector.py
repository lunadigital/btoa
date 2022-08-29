import bpy
from bpy.types import NodeSocket
from bpy.props import *
from .ainodesocket import AiNodeSocket, SocketColor

class AiNodeSocketVector(NodeSocket, AiNodeSocket):
    bl_label = "Vector"
    color = SocketColor.VECTOR
    default_type = "VECTOR"

    default_value: FloatVectorProperty()
    show_socket_value = BoolProperty()

    def draw_prop(self, context, layout, node, text):
        if self.show_socket_value:
            col = layout.column()
            col.prop(self, "default_value", text=text)            
        else:
            row = layout.row(align=True)
            row.label(text=text)
            
    def export_default(self):
        return self.default_value, self.default_type

classes = (
    AiNodeSocketVector,
)
register, unregister = bpy.utils.register_classes_factory(classes)