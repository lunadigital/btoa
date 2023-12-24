from bpy.types import NodeSocket
from bpy.props import *
from .ainodesocket import AiNodeSocket, SocketColor
from ...bridge.types import ColorData

class AiNodeSocketSurface(NodeSocket, AiNodeSocket):
    bl_label = "Surface"
    color = SocketColor.SHADER
    
    default_value: FloatVectorProperty(name="Color", subtype='COLOR', default=(0, 0, 0, 1), size=4, min=0, max=1)

    def draw_prop(self, context, layout, node, text):
        row = layout.row(align=True)
        row.label(text=text)

    def export_default(self):
        return ColorData(list(self.default_value))

def register():
    from bpy.utils import register_class
    register_class(AiNodeSocketSurface)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiNodeSocketSurface)