from bpy.types import NodeSocket
from bpy.props import FloatVectorProperty

from .ainodesocket import AiNodeSocket
from .constants import Color

class AiNodeSocketColor(AiNodeSocket):
    bl_label = "Color"

    color = Color.color_texture

    def draw_prop(self, context, layout, node, text):
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text=text)
        row.prop(self, "default_value", text="")
    
    def export_default(self):
        return list(self.default_value), self.default_type

class AiNodeSocketColorRGB(NodeSocket, AiNodeSocketColor):
    default_type = 'RGB'
    default_value: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.8, 0.8, 0.8),
        min=0,
        max=1
    )

class AiNodeSocketColorRGBA(NodeSocket, AiNodeSocketColor):
    default_type = 'RGBA'
    default_value: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.8, 0.8, 0.8, 1.0),
        size=4,
        min=0,
        max=1
    )

classes = (
    AiNodeSocketColorRGB,
    AiNodeSocketColorRGBA
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)