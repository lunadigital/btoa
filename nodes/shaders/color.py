import bpy
from bpy.props import *
from .. import base
from ... import btoa
from ... import utils

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

    def sub_export(self, node, socket_index=0):
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

    face_mode: EnumProperty(
        name="Mode",
        items=[
            ("face id", "Face ID", ""),
            ("uniform id", "Uniform ID", ""),
        ]
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Input", identifier="input")
        self.inputs.new('AiNodeSocketFloatPositive', name="Min Gain", identifier="gain_min")
        self.inputs.new('AiNodeSocketFloatPositive', name="Max Gain", identifier="gain_max")
        self.inputs.new('AiNodeSocketFloatPositive', name="Min Hue", identifier="hue_min")
        self.inputs.new('AiNodeSocketFloatPositive', name="Max Hue", identifier="hue_max")
        self.inputs.new('AiNodeSocketFloatPositive', name="Min Saturation", identifier="saturation_min")
        self.inputs.new('AiNodeSocketFloatPositive', name="Max Saturation", identifier="saturation_max")
        self.inputs.new('AiNodeSocketIntPositive', name="Seed", identifier="seed")

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def export(self):
        node = btoa.ArnoldNode(self.ai_name)

        self.sub_export(node)

        for i in self.inputs:
            socket_value, value_type = i.export()
            
            # We need to rebuild the identifier value to account for the different enum options in jitter_type
            identifier = "{}_{}".format(self.jitter_type, i.identifier)
            
            if socket_value is not None and value_type is not None:
                if value_type == 'BTNODE':
                    socket_value.link(identifier, node)
                else:
                    btoa.BTOA_SET_LAMBDA[value_type](node, identifier, socket_value)

        return node, 'BTNODE'

    def draw_buttons(self, context, layout):
        layout.prop(self, "jitter_type")

        if self.jitter_type == "face":
            layout.prop(self, "face_mode")

    def sub_export(self, node, socket_index=0):
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

    def sub_export(self, node, socket_index=0):
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

    def sub_export(self, node, socket_index=0):
        node.set_string("channel_r", self.channel_r)
        node.set_string("channel_g", self.channel_g)
        node.set_string("channel_b", self.channel_b)
        node.set_string("channel_a", self.channel_a)

        node.set_bool("negate_r", self.negate_r)
        node.set_bool("negate_g", self.negate_g)
        node.set_bool("negate_b", self.negate_b)
        node.set_bool("negate_a", self.negate_a)

classes = (
    AiColorCorrect,
    AiColorJitter,
    AiComposite,
    AiShuffle,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)