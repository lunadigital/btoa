import bpy
from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

class AiColorCorrect(Node, ArnoldNode):
    '''
    Allows you to adjust the gamma, hue, saturation, contrast, and exposure of
    an image. Alters the Input color with the following operator, applied in
    the same order as the parameters.
    '''
    bl_label = "Color Correct"
    bl_icon = 'NONE'
    
    ai_name = "color_correct"

    alpha_is_luminance: BoolProperty(
        name="Alpha is Luminance",
        description="Ignore the input alpha, setting the output alpha to the luminance of the RGB color"
    )

    invert: BoolProperty(
        name="Invert",
        description="Invert the input RGB color"
    )

    invert_alpha: BoolProperty(
        name="Invert Alpha",
        description="Invert the input alpha"
    )

    def init(self, context):
        self.inputs.new("AiNodeSocketRGBA", "Image", identifier="input")
        self.inputs.new("AiNodeSocketFloatUnbounded", "Alpha Multiply", identifier="alpha_multiply").default_value = 1
        self.inputs.new("AiNodeSocketFloatUnbounded", "Alpha Add", identifier="alpha_add")
        self.inputs.new("AiNodeSocketFloatUnbounded", "Gamma", identifier="gamma").default_value = 1
        self.inputs.new("AiNodeSocketFloatNormalizedAlt", "Hue Shift", identifier="hue_shift")
        self.inputs.new("AiNodeSocketFloatPositive", "Saturation", identifier="saturation").default_value = 1
        self.inputs.new("AiNodeSocketFloatNormalized", "Contrast", identifier="contrast").default_value = 1
        self.inputs.new("AiNodeSocketFloatNormalized", "Contrast Pivot", identifier="contrast_pivot").default_value = 0.18
        self.inputs.new("AiNodeSocketFloatUnbounded", "Exposure", identifier="exposure")
        self.inputs.new("AiNodeSocketRGB", "Multiply", identifier="multiply").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketRGB", "Add", identifier="add").default_value = (0, 0, 0)
        self.inputs.new("AiNodeSocketFloatNormalized", "Mask", identifier="mask").default_value = 1

        self.outputs.new("AiNodeSocketRGBA", "RGBA")

    def draw_buttons(self, context, layout):
        layout.prop(self, "alpha_is_luminance")
        layout.prop(self, "invert")
        layout.prop(self, "invert_alpha")

    def sub_export(self, node):
        node.set_bool("alpha_is_luminance", self.alpha_is_luminance)
        node.set_bool("invert", self.invert)
        node.set_bool("invert_alpha", self.invert_alpha)

classes = (
    AiColorCorrect,
)

register, unregister = bpy.utils.register_classes_factory(classes)