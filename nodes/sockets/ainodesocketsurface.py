from bpy.types import NodeSocket
from .ainodesocket import AiNodeSocket, SocketColor

class AiNodeSocketSurface(NodeSocket, AiNodeSocket):
    bl_label = "Surface"
    color = SocketColor.COLOR
    default_value: None

    def draw_prop(self, context, layout, node, text):
        row = layout.row(align=True)
        row.label(text=text)

def register():
    from bpy.utils import register_class
    register_class(AiNodeSocketSurface)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiNodeSocketSurface)