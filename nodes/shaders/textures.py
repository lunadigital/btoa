import bpy
import math
import mathutils
import os
from bpy.props import *
from .. import base, constants
from ... import utils

'''
AiCellNoise
https://docs.arnoldrenderer.com/display/A5NodeRef/cell_noise

A cell noise pattern generator.
'''
class AiCellNoise(bpy.types.Node, base.ArnoldNode):
    bl_label = "Cell Noise"
    ai_name = "cell_noise"

    pattern: EnumProperty(
        name="Pattern",
        items=[
            ("0", "Noise1", "Noise1"),
            ("1", "Noise2", "Noise2"),
            ("2", "Cell1", "Cell1"),
            ("3", "Cell2", "Cell2"),
            ("4", "Worley1", "Worley1"),
            ("5", "Worley2", "Worley2"),
            ("6", "Alligator", "Alligator")
        ],
        default="0"
    )

    additive: BoolProperty(name="Additive")

    def init(self, context):
        self.inputs.new("AiNodeSocketIntAboveOne", "Octaves", identifier="octaves").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Randomness", identifier="randomness").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Lacunarity", identifier="lacunarity").default_value = 1.92
        self.inputs.new("AiNodeSocketFloatNormalized", "Amplitude", identifier="amplitude").default_value = 1
        self.inputs.new("AiNodeSocketVector", "Scale", identifier="scale").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketVector", "Offset", identifier="offset")
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")
        self.inputs.new("AiNodeSocketFloatUnbounded", "Time", identifier="time")
        self.inputs.new("AiNodeSocketRGB", "Palette", identifier="palette").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketFloatPositive", "Density", identifier="density").default_value = 0.5

        self.outputs.new("AiNodeSocketRGB", "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pattern", text="")
        layout.prop(self, "additive")
    
    def sub_export(self, node, socket_index=0):
        node.set_int("pattern", int(self.pattern))
        node.set_bool("additive", self.additive)

'''
AiCheckerboard
https://docs.arnoldrenderer.com/display/A5NodeRef/checkerboard

Represents a checkerboard pattern.
'''
class AiCheckerboard(bpy.types.Node, base.ArnoldNode):
    bl_label = "Checkerboard"
    ai_name = "checkerboard"

    def init(self, context):
        self.inputs.new("AiNodeSocketFloatPositive", "U Frequency", identifier="u_frequency").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "V Frequency", identifier="v_frequency").default_value = 1
        self.inputs.new("AiNodeSocketFloatUnbounded", "U Offset", identifier="u_offset")
        self.inputs.new("AiNodeSocketFloatUnbounded", "V Offset", identifier="v_offset")
        self.inputs.new("AiNodeSocketFloatNormalized", "Contrast", identifier="contrast").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Filter Strength", identifier="filter_strength").default_value = 1
        self.inputs.new("AiNodeSocketFloatNormalized", "Filter Offset", identifier="filter_offset")
        self.inputs.new("AiNodeSocketRGB", "Color1", identifier="color1")
        self.inputs.new("AiNodeSocketRGB", "Color2", identifier="color2").default_value = (0, 0 ,0)

        self.outputs.new("AiNodeSocketRGB", "RGB")

'''
AiFlakes
https://docs.arnoldrenderer.com/display/A5NodeRef/Flakes

Creates a procedural flake normal map that can be used for materials
such as car paint.
'''
class AiFlakes(bpy.types.Node, base.ArnoldNode):
    bl_label = "Flakes"
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

        self.outputs.new("AiNodeSocketRGB", "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "output_space", text="")
    
    def sub_export(self, node, socket_index=0):
        node.set_int("pattern", int(self.output_space))

'''
AiImageUser

A helper class for AiImage below.
'''
class AiImageUser(bpy.types.PropertyGroup):
    image: PointerProperty(type=bpy.types.Image)

    frame_start: IntProperty(name="First Frame")
    frame_offset: IntProperty(name="Offset")

'''
AiImage
https://docs.arnoldrenderer.com/display/A5NodeRef/image

Performs texture mapping using a specified image file.
'''
class AiImage(bpy.types.Node, base.ArnoldNode):
    bl_label = "Image"
    bl_width_default = constants.BL_NODE_WIDTH_WIDE
    ai_name = "image"

    AI_WRAP_OPTIONS = [
        ("0", "Periodic", "Periodic"),
        ("1", "Black", "Black"),
        ("2", "Clamp", "Clamp"),
        ("3", "Mirror", "Mirror"),
        ("4", "File", "File")
    ]

    image: PointerProperty(name="Image", type=bpy.types.Image)
    image_user: PointerProperty(type=AiImageUser)

    image_filter: EnumProperty(
        name="Filter",
        items=[
            ('closest', "Closest", "Closest"),
            ('bilinear', "Bilinear", "Bilinear"),
            ('bicubic', "Bicubic", "Bicubic"),
            ('smart_bicubic', "Smart Bicubic", "Smart Bicubic")
        ],
        default='smart_bicubic'
    )

    swrap: EnumProperty(name="Wrap U", items=AI_WRAP_OPTIONS, default="0")
    twrap: EnumProperty(name="Wrap V", items=AI_WRAP_OPTIONS, default="0")
    sflip: BoolProperty(name="Flip U")
    tflip: BoolProperty(name="Flip V")
    swap_st: BoolProperty(name="Swap UV")
    uvset: StringProperty(name="UV Set")

    def init(self, context):
        self.inputs.new("AiNodeSocketRGB", "Multiply", identifier="multiply").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketRGB", "Offset", identifier="offset").default_value = (0, 0, 0)
        self.inputs.new("AiNodeSocketIntUnbounded", "Mipmap Bias", identifier="mipmap_bias")
        self.inputs.new("AiNodeSocketUVOffset", "Offset U", identifier="soffset")
        self.inputs.new("AiNodeSocketUVOffset", "Offset V", identifier="toffset")
        self.inputs.new("AiNodeSocketUVScale", "Scale U", identifier="sscale")
        self.inputs.new("AiNodeSocketUVScale", "Scale V", identifier="tscale")

        self.outputs.new("AiNodeSocketRGBA", "RGBA")
        self.outputs.new("AiNodeSocketBW", "R")
        self.outputs.new("AiNodeSocketBW", "G")
        self.outputs.new("AiNodeSocketBW", "B")
        self.outputs.new("AiNodeSocketBW", "A")

    def draw_label(self):
        if self.image:
            return self.image.name
        else:
            return self.bl_label

    def draw_buttons(self, context, layout):
        layout.template_ID(self, "image", open="image.open")

        layout.separator()

        if self.image:
            layout.prop(self.image.colorspace_settings, "name")

        layout.prop(self, "image_filter")
        layout.prop(self, "swrap")
        layout.prop(self, "twrap")
        layout.prop(self, "sflip")
        layout.prop(self, "tflip")
        layout.prop(self, "swap_st")
        #layout.prop(self, "uvset")

    def sub_export(self, node, socket_index=0):
        if self.image:
            if self.image.packed_file:
                filepath = os.path.join(bpy.app.tempdir, self.image.name)
                
                with open(filepath, 'wb+') as f:
                    f.write(self.image.packed_file.data)

                node.set_string("filename", filepath)
            elif self.image.library:
                node.set_string("filename", bpy.path.abspath(self.image.filepath, library=self.image.library))
            else:
                node.set_string("filename", bpy.path.abspath(self.image.filepath))

            node.set_string("color_space", self.image.colorspace_settings.name)
        
        if socket_index > 0:
            node.set_bool("single_channel", True)
            node.set_byte("start_channel", socket_index - 1)

        node.set_string("filter", self.image_filter)
        node.set_int("swrap", int(self.swrap))
        node.set_int("twrap", int(self.twrap))
        node.set_bool("sflip", self.sflip)
        node.set_bool("tflip", self.tflip)
        node.set_bool("swap_st", self.swap_st)
        node.set_string("uvset", self.uvset)

        prefs = bpy.context.preferences.addons["btoa"].preferences
        node.set_bool("ignore_missing_textures", prefs.ignore_missing_textures)
        node.set_rgba("missing_texture_color", *prefs.missing_texture_color)

'''
LayerProperties

A helper class for layered shaders.
'''
class LayerProperties(bpy.types.PropertyGroup):
    enabled: BoolProperty(name="Enable", default=True)
    name: StringProperty(name="Name")
    operation: EnumProperty(
        name="Operation",
        items=[
            ("atop", "Atop", ""),
            ("average", "Average", ""),
            ("cojoint_over", "Cojoint Over", ""),
            ("color_burn", "Color Burn", ""),
            ("color_dodge", "Color Dodge", ""),
            ("difference", "Difference", ""),
            ("disjoint_over", "Disjoint Over", ""),
            ("divide", "Divide", ""),
            ("exclusion", "Exclusion", ""),
            ("from", "From", ""),
            ("geometric", "Geometric", ""),
            ("glow", "Glow", ""),
            ("hard_light", "Hard Light", ""),
            ("hard_mix", "Hard Mix", ""),
            ("hypot_diagonal", "Hypot Diagonal", ""),
            ("in", "In", ""),
            ("linear_light", "Linear Light", ""),
            ("mask", "Mask", ""),
            ("matte", "Matte", ""),
            ("max", "Max", ""),
            ("min", "Min", ""),
            ("minus", "Minus", ""),
            ("multiply", "Multiply", ""),
            ("negation", "Negation", ""),
            ("out", "Out", ""),
            ("over", "Over", ""),
            ("overlay", "Overlay", ""),
            ("overwrite", "Overwrite", ""),
            ("phoenix", "Phoenix", ""),
            ("pin_light", "Pin Light", ""),
            ("plus", "Plus", ""),
            ("reflect", "Reflect", ""),
            ("screen", "Screen", ""),
            ("soft_light", "Soft Light", ""),
            ("stencil", "Stencil", ""),
            ("subtract", "Subtract", ""),
            ("under", "Under", ""),
            ("vivid_light", "Vivid Light", ""),
            ("xor", "XOR", "")
        ],
        default="over"
    )
    alpha_operation: EnumProperty(
        name="Alpha Channel Operation",
        description="",
        items=[
            ("result", "Result", ""),
            ("preserve", "Preserve", ""),
            ("overwrite", "Overwrite", ""),
            ("mask", "Mask", ""),
        ],
        default="result"
    )

'''
AiLayer

A base class for layered Arnold texture nodes (layer_float,
layer_rgba). This is NOT a public-facing class.
'''
class AiLayer(bpy.types.Node, base.ArnoldNode):
    bl_width_default = constants.BL_NODE_WIDTH_WIDE

    layers: CollectionProperty(type=LayerProperties)

    def init(self, context):
        for i in range(1, 9):
            layer = self.layers.add()
            layer.name = "Layer{}".format(i)

    def template_layer_properties(self, layout, layer):
        split = layout.split(factor=0.1)

        col = split.column()
        col.prop(layer, "enabled", text="")

        col = split.column()
        col.prop(layer, "name", text="")
        col.enabled = layer.enabled

    def draw_buttons(self, context, layout):
        for layer in self.layers:
            self.template_layer_properties(layout, layer)

    def sub_export(self, node, socket_index=0):
        for layer, i in zip(self.layers, range(1, 9)):
            node.set_bool("enable{}".format(i), layer.enabled)
            node.set_string("name{}".format(i), layer.name)

'''
AiLayerFloat
https://docs.arnoldrenderer.com/display/A5NodeRef/layer_float

Combines 8 float layers linearly. Layers are applied in order (bottom to top).
'''
class AiLayerFloat(AiLayer):
    bl_label = "Layer Float"
    ai_name = "layer_float"

    def init(self, context):
        super().init(context)
        
        for i in range(1, 9):
            self.inputs.new('AiNodeSocketFloatUnbounded', "Layer {}".format(i), identifier="input{}".format(i))

        self.outputs.new('AiNodeSocketFloatUnbounded', name="Float", identifier="output")

'''
AiLayerRGBA
https://docs.arnoldrenderer.com/display/A5NodeRef/layer_rgba

The layer_RGBA shader can be used to linearly layer up to eight
shaders together, enabling you to create complex shading effects.
Layers are applied in order (bottom to top) according to a blending
mode specified in the operation. The layer alpha can optionally be
a separate input. A use for this shader could include adding text
to an image for example. 
'''
class AiLayerRGBA(AiLayer):
    bl_label = "Layer RGBA"
    ai_name = "layer_rgba"

    clamp: BoolProperty(name="Clamp Result")

    def init(self, context):
        super().init(context)

        for i in range(1, 9):
            self.inputs.new('AiNodeSocketRGBA', "Layer {}".format(i), identifier="input{}".format(i))
            self.inputs.new('AiNodeSocketFloatNormalized', "Mix", identifier="mix{}".format(i))

        self.outputs.new('AiNodeSocketRGBA', name="RGBA", identifier="output")

    def template_layer_properties(self, layout, layer):
        super().template_layer_properties(layout, layer)

        col = layout.column()
        col.prop(layer, "operation")
        col.prop(layer, "alpha_operation")
        col.enabled = layer.enabled

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

        layout.separator()
        layout.prop(self, "clamp")
        layout.separator()

    def sub_export(self, node, socket_index=0):
        super().sub_export(node)

        for layer, i in zip(self.layers, range(1, 9)):
            node.set_string("operation{}".format(i), layer.operation)
            node.set_string("alpha_operation{}".format(i), layer.alpha_operation)

'''
AiMixRGBA
https://docs.arnoldrenderer.com/display/A5NodeRef/mix_rgba

The mix_RGBA is used to blend or add two colors or textures. It
returns a linear interpolation of input1 and input2 according to
the mix_weight attribute. A mix_weight value of 0 outputs input1,
a value of 1 outputs input2, and a value of 0.5 mixes evenly
between input1 and input2.
'''
class AiMixRGBA(bpy.types.Node, base.ArnoldNode):
    bl_label = "Mix RGBA"
    ai_name = "mix_rgba"

    def init(self, context):
        self.inputs.new("AiNodeSocketFloatNormalized", "Mix", identifier="mix").default_value = 0.5
        self.inputs.new("AiNodeSocketRGBA", "Input 1", identifier="input1")
        self.inputs.new("AiNodeSocketRGBA", "Input 2", identifier="input2").default_value = (0, 0, 0, 1)

        self.outputs.new('AiNodeSocketRGBA', name="RGBA", identifier="output")

'''
AiNoise
https://docs.arnoldrenderer.com/display/A5NodeRef/noise

Evaluates a coherent noise function.
'''
class AiNoise(bpy.types.Node, base.ArnoldNode):
    bl_label = "Noise"
    ai_name = "noise"

    mode: EnumProperty(
        name="Mode",
        items=[
            ("0", "Scalar", "Scalar"),
            ("1", "Vector", "Vector"),
        ],
        default="0"
    )

    def init(self, context):
        self.inputs.new("AiNodeSocketIntAboveOne", "Octaves", identifier="octaves").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Distortion", identifier="distortion").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Lacunarity", identifier="lacunarity").default_value = 1.92
        self.inputs.new("AiNodeSocketFloatNormalized", "Amplitude", identifier="amplitude").default_value = 1
        self.inputs.new("AiNodeSocketVector", "Scale", identifier="scale").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketVector", "Offset", identifier="offset")
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")
        self.inputs.new("AiNodeSocketFloatUnbounded", "Time", identifier="time")
        self.inputs.new("AiNodeSocketRGB", "Color1", identifier="color1")
        self.inputs.new("AiNodeSocketRGB", "Color2", identifier="color2").default_value = (0, 0 ,0)
        
        self.outputs.new("AiNodeSocketRGB", "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode", text="")
    
    def sub_export(self, node, socket_index=0):
        node.set_int("mode", int(self.mode))

'''
AiPhysicalSky
https://docs.arnoldrenderer.com/display/A5NodeRef/physical_sky

This shader implements a variation of the Hosek-Wilkie sky radiance
model, including the direct solar radiance function.
'''
class AiPhysicalSky(bpy.types.Node, base.ArnoldNode):
    bl_label = "Physical Sky"
    ai_name = "physical_sky"

    enable_sun: BoolProperty(name="Enable Sun", default=True)
    use_degrees: BoolProperty(name="Use Degrees", default=True)
    direction_object: PointerProperty(name="Sun Direction", type=bpy.types.Object)
    direction_vector: FloatVectorProperty(
        default=(-0.4, 0.75, 0.5),
        min=-1.000000,
        max=1.000000,
        subtype="DIRECTION",
        size=3
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositiveToTen', "Turbidity", identifier="turbidity").default_value = 3
        self.inputs.new('AiNodeSocketRGB', "Ground Albedo", identifier="ground_albedo").default_value = (0.1, 0.1, 0.1)
        self.inputs.new('AiNodeSocketFloatHalfRotation', "Elevation", identifier="elevation").default_value = math.pi / 4 # 45deg
        self.inputs.new('AiNodeSocketFloatFullRotation', "Azimuth", identifier="azimuth").default_value = math.pi / 2 # 90deg
        self.inputs.new('AiNodeSocketFloatPositive', "Intensity", identifier="intensity").default_value = 1

        self.inputs.new('AiNodeSocketRGB', "Sky Tint", identifier="sky_tint").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Sun Tint", identifier="sun_tint").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketFloatPositive', "Sun Size", identifier="sun_size").default_value = 0.51

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "enable_sun")
        layout.prop(self, "use_degrees")

        row = layout.row()
        row.prop(self, "direction_vector", text="")
        row.enabled = not self.use_degrees and not self.direction_object
        
        row = layout.row()
        row.prop(self, "direction_object")
        row.enabled = not self.use_degrees

    def sub_export(self, node, socket_index=0):
        node.set_bool("enable_sun", self.enable_sun)
        node.set_bool("use_degrees", self.use_degrees)

        if not self.use_degrees:
            if self.direction_object:
                neg_z_axis = mathutils.Vector((0, 0, -1))
                mw = self.direction_object.matrix_world
                direction = (mw @ neg_z_axis - mw.translation).normalized()  
            else:
                direction = self.direction_vector.copy()
                direction.negate()
    
            vec = mathutils.Vector((direction.x, direction.z, direction.y)) # Swap coordinates to match Arnold
            node.set_vector("sun_direction", *vec)

'''
AiRoundCorners
https://docs.arnoldrenderer.com/display/A5NodeRef/round_corners

Modifies the shading normals near edges to give the appearance
of a round corner.
'''
class AiRoundCorners(bpy.types.Node, base.ArnoldNode):
    bl_label = "Round Corners"
    ai_name = "round_corners"

    inclusive: BoolProperty(name="Inclusive", default=True)
    self_only: BoolProperty(name="Self Only")
    object_space: BoolProperty(name="Object Space", default=True)

    def init(self, context):
        self.inputs.new("AiNodeSocketIntAboveOne", "Samples", identifier="samples").default_value = 6
        self.inputs.new("AiNodeSocketFloatNormalized", "Radius", identifier="radius").default_value = 0.01
        self.inputs.new("AiNodeSocketVector", "Normal", identifier="normal")

        self.outputs.new("AiNodeSocketVector", "Vector")

    def draw_buttons(self, context, layout):
        layout.prop(self, "inclusive")
        layout.prop(self, "self_only")
        layout.prop(self, "object_space")
    
    def sub_export(self, node, socket_index=0):
        node.set_bool("inclusive", self.inclusive)
        node.set_bool("self_only", self.self_only)
        node.set_bool("object_space", self.object_space)

classes = (
    AiCellNoise,
    AiCheckerboard,
    AiFlakes,
    AiImageUser,
    AiImage,
    LayerProperties,
    AiLayerFloat,
    AiLayerRGBA,
    AiMixRGBA,
    AiNoise,
    AiPhysicalSky,
    AiRoundCorners,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)