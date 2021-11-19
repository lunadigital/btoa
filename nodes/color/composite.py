import bpy
from bpy.types import Node
from bpy.props import EnumProperty

from ..base import ArnoldNode

class AiComposite(Node, ArnoldNode):
    ''' The composite shader mixes two RGBA inputs according to a blend mode. '''
    bl_label = "Composite"
    bl_icon = 'NONE'

    ai_name = "composite"

    operation: EnumProperty(
        name="Operation",
        items=[
            ("a", "A", ""),
            ("b", "B", ""),
            ("atop", "Atop", ""),
            ("average", "Average", ""),
            ("cojoint_over", "Cojoint Over", ""),
            ("difference", "Difference", ""),
            ("disjoint_over", "Disjoint Over", ""),
            ("divide", "Divide", ""),
            ("exclusion", "Exclusion", ""),
            ("from", "From", ""),
            ("geometric", "Geometric", ""),
            ("hard_light", "Hard Light", ""),
            ("hypot_diagonal", "Hypot Diagonal", ""),
            ("in", "In", ""),
            ("mask", "Mask", ""),
            ("matte", "Matte", ""),
            ("max", "Max", ""),
            ("min", "Min", ""),
            ("minus", "Minus", ""),
            ("multiply", "Multiply", ""),
            ("out", "Out", ""),
            ("over", "Over", ""),
            ("overlay", "Overlay", ""),
            ("plus", "Plus", ""),
            ("screen", "Screen", ""),
            ("soft_light", "Soft Light", ""),
            ("stencil", "Stencil", ""),
            ("under", "Under", ""),
            ("xor", "XOR", "")
        ],
        default="over"
    )

    alpha_operation: EnumProperty(
        name="Alpha Channel Operation",
        items=[
            ("same", "Same", ""),
            ("a", "A", ""),
            ("b", "B", "")
        ]
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', name="A", identifier="A")
        self.inputs.new('AiNodeSocketRGBA', name="B", identifier="B")

        self.outputs.new('AiNodeSocketRGBA', name="RGBA", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation")
        layout.prop(self, "alpha_operation")

    def sub_export(self, node):
        node.set_string("operation", self.operation)
        node.set_string("alpha_operation", self.alpha_operation)

def register():
    bpy.utils.register_class(AiComposite)

def unregister():
    bpy.utils.unregister_class(AiComposite)