import bpy
from bpy.props import *
from .. import base
from ... import utils

'''
AiColorConstant

Returns a constant RGBA color value. This is a dummy node for a
similar node in Blender/Cycles, but doesn't have an equivalent
node in Arnold.
'''
class AiColorConstant(bpy.types.Node, base.ArnoldNode):
    bl_label = "Constant"

    def init(self, context):
        self.inputs.new("AiNodeSocketRGB", name="Color", identifier="input")
        self.outputs.new("AiNodeSocketRGB", "RGB", identifier="output")

    def export(self):
        return self.inputs[0].export()

'''
AiColorCorrect
https://docs.arnoldrenderer.com/display/A5NodeRef/color_correct

Allows you to adjust the gamma, hue, saturation, contrast, and exposure of
an image. Alters the Input color with the following operator, applied in
the same order as the parameters.
'''
class AiColorCorrect(bpy.types.Node, base.ArnoldNode):
    bl_label = "Color Correct"
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

'''
AiColorJitter
https://docs.arnoldrenderer.com/display/A5NodeRef/color_jitter

This shader enables you to alter the input color by applying a random
    color variation. For each of the following parameters, you can specify
    the range of hue, saturation, and gain (HSV) for the random colors.
    The seed is used to get a different random variation.
'''
class AiColorJitter(bpy.types.Node, base.ArnoldNode):
    bl_label = "Color Jitter"
    ai_name = "color_jitter"

    jitter_type: EnumProperty(
        name="Type",
        items=[
            # ('data', "User Data", ""),
            ('proc', "Procedural", ""),
            ('obj', "Object", ""),
            ('face', "Face", "")
        ]
    )

    gain_min: FloatProperty(name="Gain Min", min=0, soft_max=1)
    gain_max: FloatProperty(name="Gain Max", min=0, soft_max=1)
    hue_min: FloatProperty(name="Hue Min", min=-1, max=1)
    hue_max: FloatProperty(name="Hue Max", min=-1, max=1)
    saturation_min: FloatProperty(name="Saturation Min", min=0, soft_max=1)
    saturation_max: FloatProperty(name="Saturation Max", min=0, soft_max=1)
    seed: IntProperty(name="Seed", min=0, soft_max=10)

    face_mode: EnumProperty(
        name="Mode",
        items=[
            ("face id", "Face ID", ""),
            ("uniform id", "Uniform ID", ""),
        ]
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Input", identifier="input")
        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "jitter_type")

        layout.prop(self, "gain_min")
        layout.prop(self, "gain_max")
        layout.prop(self, "hue_min")
        layout.prop(self, "hue_max")
        layout.prop(self, "saturation_min")
        layout.prop(self, "saturation_max")
        layout.prop(self, "seed")

        if self.jitter_type == "face":
            layout.prop(self, "face_mode")

    def sub_export(self, node):
        node.set_float("{}_gain_min".format(self.jitter_type), self.gain_min)
        node.set_float("{}_gain_max".format(self.jitter_type), self.gain_max)
        node.set_float("{}_hue_min".format(self.jitter_type), self.hue_min)
        node.set_float("{}_hue_max".format(self.jitter_type), self.hue_max)
        node.set_float("{}_saturation_min".format(self.jitter_type), self.saturation_min)
        node.set_float("{}_saturation_max".format(self.jitter_type), self.saturation_max)
        node.set_int("{}_seed".format(self.jitter_type), self.seed)

        if self.jitter_type == "face":
            node.set_string("face_mode", self.face_mode)

'''
AiComposite
https://docs.arnoldrenderer.com/display/A5NodeRef/composite

The composite shader mixes two RGBA inputs according to a blend mode.
'''
class AiComposite(bpy.types.Node, base.ArnoldNode):
    bl_label = "Composite"
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

'''
AiShuffle
https://docs.arnoldrenderer.com/display/A5NodeRef/shuffle

Combines RGB and alpha inputs to output an RGBA by default.
Additionally, there are parameters to shuffle the channels.
'''
class AiShuffle(bpy.types.Node, base.ArnoldNode):
    bl_label = "Shuffle"
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

classes = (
    AiColorConstant,
    AiColorCorrect,
    AiColorJitter,
    AiComposite,
    AiShuffle,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)