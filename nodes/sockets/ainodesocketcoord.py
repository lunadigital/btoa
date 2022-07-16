from bpy.types import NodeSocket
from bpy.props import StringProperty
from .ainodesocket import AiNodeSocket, SocketColor

class AiNodeSocketCoord(NodeSocket, AiNodeSocket):
    bl_label = "Coords"
    color = SocketColor.VECTOR
    default_type = "STRING"

    default_value: StringProperty(
        name="Object",
        default="object"
    )

    def draw_prop(self, context, layout, node, text):
        row = layout.row()
        row.label(text=text)

    def export_default(self):
        return self.default_value, self.default_type

    # We're overriding the main export method because Arnold has no "coordinate space" node
    # Just need to get the default value instead
    def export(self):
        return self.export_default()

def register():
    from bpy.utils import register_class
    register_class(AiNodeSocketCoord)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiNodeSocketCoord)