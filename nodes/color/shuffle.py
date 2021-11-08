import bpy
from bpy.types import Node
from bpy.props import BoolProperty, EnumProperty

from ..base import ArnoldNode

class AiShuffle(Node, ArnoldNode):
    '''
    Combines RGB and alpha inputs to output an RGBA by default.
    Additionally, there are parameters to shuffle the channels.
    '''
    bl_label = "Shuffle"
    bl_icon = 'NONE'

    ai_name = "shuffle"

    channel_r: EnumProperty(
        name="R",
        items=[
            ("R", "R", ""),
            ("G", "G", ""),
            ("B", "B", ""),
            ("A", "A", "")
        ]
    )

    channel_g: EnumProperty(
        name="G",
        items=[
            ("R", "R", ""),
            ("G", "G", ""),
            ("B", "B", ""),
            ("A", "A", "")
        ],
        default="G"
    )

    channel_b: EnumProperty(
        name="B",
        items=[
            ("R", "R", ""),
            ("G", "G", ""),
            ("B", "B", ""),
            ("A", "A", "")
        ],
        default="B"
    )

    channel_a: EnumProperty(
        name="A",
        items=[
            ("R", "R", ""),
            ("G", "G", ""),
            ("B", "B", ""),
            ("A", "A", "")
        ],
        default="A"
    )

    negate_r: BoolProperty(name="R")
    negate_g: BoolProperty(name="G")
    negate_b: BoolProperty(name="B")
    negate_a: BoolProperty(name="A")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Color", identifier="color")
        self.inputs.new('AiNodeSocketFloatUnbounded', name="Alpha", identifier="alpha")

        self.outputs.new('AiNodeSocketRGBA', name="RGBA", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "channel_r")
        layout.prop(self, "channel_g")
        layout.prop(self, "channel_b")
        layout.prop(self, "channel_a")

        layout.separator()

        layout.label(text="Negate")

        split = layout.split()
        
        col = split.column()
        col.prop(self, "negate_r")
        col.prop(self, "negate_b")

        col = split.column()
        col.prop(self, "negate_g")
        col.prop(self, "negate_a")

        layout.separator()

    def sub_export(self, node):
        node.set_string("channel_r", self.channel_r)
        node.set_string("channel_g", self.channel_g)
        node.set_string("channel_b", self.channel_b)
        node.set_string("channel_a", self.channel_a)

        node.set_bool("negate_r", self.negate_r)
        node.set_bool("negate_g", self.negate_g)
        node.set_bool("negate_b", self.negate_b)
        node.set_bool("negate_a", self.negate_a)

def register():
    bpy.utils.register_class(AiShuffle)

def unregister():
    bpy.utils.unregister_class(AiShuffle)