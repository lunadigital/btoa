import bpy
from bpy.types import Node
from bpy.props import EnumProperty

from ..base import ArnoldNode

class AiFlakes(Node, ArnoldNode):
    '''
    Creates a procedural flake normal map that can be used for materials
    such as car paint.
    '''
    bl_label = "Flakes"
    bl_icon = 'NONE'
    
    ai_name = "flakes"

    output_space: EnumProperty(
        name="Output Space",
        description="",
        items=[
            ("0", "World", "World"),
            ("1", "Tangent", "Tangent")
        ]
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Scale", identifier="scale").default_value = 0.1
        self.inputs.new('AiNodeSocketFloatNormalized', "Density", identifier="density").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Step", identifier="step").default_value
        self.inputs.new('AiNodeSocketFloatPositive', "Depth", identifier="depth")
        self.inputs.new('AiNodeSocketFloatAboveOne', "IOR", identifier="ior").default_value = 1.52
        self.inputs.new('AiNodeSocketFloatNormalized', "Normal Randomize", identifier="normal_randomize").default_value = 0.5
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")
        # pref name

        self.outputs.new("AiNodeSocketRGB", "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "output_space", text="")
    
    def sub_export(self, node):
        node.set_int("pattern", int(self.output_space))

classes = (
    AiFlakes,
)
register, unregister = bpy.utils.register_classes_factory(classes)