import bpy
from bpy.props import *
from .. import base
from ... import utils

'''
AiMultiply
https://docs.arnoldrenderer.com/display/A5NodeRef/multiply

Returns input1 x input2.
'''
class AiMultiply(bpy.types.Node, base.ArnoldNode):
    bl_label = "Multiply"
    ai_name = "multiply"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Input 1", identifier="input1").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Input 2", identifier="input2").default_value = (1, 1, 1)

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

'''
AiRange
https://docs.arnoldrenderer.com/display/A5NodeRef/range

Remap input from the [input_min, input_max] range to the
[ouput_min, output_max] range linearly. The result is not
clamped unless smoothstep is on, and the result is
interpolated smoothly and the result is clamped in the
[output_min, output_max] range.
'''
class AiRange(bpy.types.Node, base.ArnoldNode):
    bl_label = "Range"
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

classes = (
    AiMultiply,
    AiRange,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)