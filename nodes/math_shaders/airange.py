import bpy
from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

class AiRange(Node, ArnoldNode):
    '''
    Remap input from the [input_min, input_max] range to the
    [ouput_min, output_max] range linearly. The result is not
    clamped unless smoothstep is on, and the result is
    interpolated smoothly and the result is clamped in the
    [output_min, output_max] range.
    '''
    bl_label = "Range"
    bl_icon = 'NONE'

    ai_name = "range"

    smoothstep: BoolProperty(name="Smoothstep")

    def init(self, context):
        self.inputs.new('AiNodeSocketSurface', name="Input", identifier="input")
        self.inputs.new('AiNodeSocketFloatPositive', name="Input Min", identifier="input_min")
        self.inputs.new('AiNodeSocketFloatPositive', name="Input Max", identifier="input_max").default_value = 1
        self.inputs.new('AiNodeSocketFloatPositive', name="Output Min", identifier="output_min")
        self.inputs.new('AiNodeSocketFloatPositive', name="Output Max", identifier="output_max").default_value = 1
        self.inputs.new('AiNodeSocketFloatPositive', name="Contrast", identifier="contrast").default_value = 1
        self.inputs.new('AiNodeSocketFloatNormalized', name="Contrast Pivot", identifier="contrast_pivot").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatNormalized', name="Bias", identifier="bias").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatPositive', name="Gain", identifier="gain").default_value = 0.5

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "smoothstep")

    def sub_export(self, node):
        node.set_bool("smoothstep", self.smoothstep)

def register():
    bpy.utils.register_class(AiRange)

def unregister():
    bpy.utils.unregister_class(AiRange)