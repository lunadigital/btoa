from bpy.types import Node
from bpy.props import EnumProperty

from ..base import ArnoldNode

class AiSkydome(Node, ArnoldNode):
    ''' Returns a skydome light for World rendering '''
    bl_label = "Skydome"
    bl_icon = 'MATERIAL'

    ai_name = "skydome_light"

    image_format: EnumProperty(
        name="Format",
        items=[
            ("0", "Lat-long", "Lat-long"),
            ("1", "Mirrored Ball", "Mirrored Ball"),
            ("2", "Angular", "Angular"),
        ]
    )

    portal_mode: EnumProperty(
        name="Portal Mode",
        items=[
            ("0", "Off", "Off"),
            ("1", "Interior Only", "Interior Only"),
            ("2", "Interior/Exterior", "Interior/Exterior"),
        ],
        default="1"
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="color")
        self.inputs.new('AiNodeSocketFloatPositive', "Intensity", identifier="intensity").default_value = 1
        self.inputs.new('AiNodeSocketFloatPositive', "Exposure", identifier="exposure")
        self.inputs.new('AiNodeSocketIntPositive', "Resolution", identifier="resolution").default_value = 1000

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "image_format")
        layout.prop(self, "portal_mode")

    def sub_export(self, node):
        node.set_int("format", int(self.image_format))
        node.set_int("portal_mode", int(self.portal_mode))

def register():
    from bpy.utils import register_class
    register_class(AiSkydome)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiSkydome)