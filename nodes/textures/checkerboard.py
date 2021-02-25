import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiCheckerboard(Node, ArnoldNode):
    ''' Represents a checkerboard pattern. '''
    bl_label = "Checkerboard"
    ai_name = "checkerboard"

    def init(self, context):
        self.inputs.new("AiNodeSocketRGB", "Color1", identifier="color1")
        self.inputs.new("AiNodeSocketRGB", "Color2", identifier="color2").default_value = (0, 0 ,0)
        self.inputs.new("AiNodeSocketFloatPositive", "U Frequency", identifier="u_frequency").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "V Frequency", identifier="v_frequency").default_value = 1
        self.inputs.new("AiNodeSocketFloatUnbounded", "U Offset", identifier="u_offset")
        self.inputs.new("AiNodeSocketFloatUnbounded", "V Offset", identifier="v_offset")
        self.inputs.new("AiNodeSocketFloatNormalized", "Contrast", identifier="contrast").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Filter Strength", identifier="filter_strength").default_value = 1
        self.inputs.new("AiNodeSocketFloatNormalized", "Filter Offset", identifier="filter_offset")
        # uvset

        self.outputs.new("AiNodeSocketRGB", "RGB")

classes = (
    AiCheckerboard,
)
register, unregister = bpy.utils.register_classes_factory(classes)