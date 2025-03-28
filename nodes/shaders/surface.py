import bpy
from bpy.props import *
from .. import core, constant
from ...utils import register_utils
from ...bridge.types import DisplacementData

'''
AiAmbientOcclusion

Ambient occlusion shader. Outputs RGB.
'''
class AiAmbientOcclusion(bpy.types.Node, core.ArnoldNode):
    bl_label = "Ambient Occlusion"
    ai_name = "ambient_occlusion"

    invert_normals: BoolProperty(name="Invert Normals")
    self_only: BoolProperty(name="Self Only")

    def init(self, context):
        self.inputs.new('AiNodeSocketIntAboveOne', "Samples", identifier="samples").default_value = 3
        self.inputs.new('AiNodeSocketFloatNormalized', "Spread", identifier="spread").default_value = 1
        self.inputs.new('AiNodeSocketFloatPositive', "Falloff", identifier="falloff").default_value = 1
        self.inputs.new('AiNodeSocketFloatAboveOne', "Near Clip", identifier="near_clip")
        self.inputs.new('AiNodeSocketFloatAboveOne', "Far Clip", identifier="far_clip").default_value = 100
        self.inputs.new("AiNodeSocketRGB", "White", identifier="white").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketRGB", "Black", identifier="black").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketVector', "Normal", identifier="normal")

        self.outputs.new('AiNodeSocketSurface', name="RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "invert_normals")
        layout.prop(self, "self_only")

    def sub_export(self, node):
        node.set_bool("invert_normals", self.invert_normals)
        node.set_bool("self_only", self.self_only)

'''
AiCarPaint

A simple-to-use car paint shader. Outputs RGB.
'''
class AiCarPaint(bpy.types.Node, core.ArnoldNode):
    bl_label = "Car Paint"
    bl_width_default = constant.BL_NODE_WIDTH_WIDE
    ai_name = "car_paint"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Weight", identifier="base").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Base Color", identifier="base_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Roughness", identifier="base_roughness")

        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Weight", identifier="specular").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Specular Color", identifier="specular_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Specular Flip Flop", identifier="specular_flip_flop")
        self.inputs.new('AiNodeSocketRGB', "Specular Light Facing", identifier="specular_light_facing")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Falloff", identifier="specular_falloff")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.52

        self.inputs.new('AiNodeSocketRGB', "Transmission Color", identifier="transmission_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Flake Color", identifier="flake_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketIntAboveOne', "Flake Layers", identifier="flake_layers").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Flake Flip Flop", identifier="flake_flip_flop").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Flake Light Facing", identifier="flake_light_facing").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Falloff", identifier="flake_falloff")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Roughness", identifier="flake_roughness").default_value = 0.4
        self.inputs.new('AiNodeSocketFloatAboveOne', "Flake IOR", identifier="flake_IOR")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Scale", identifier="flake_scale").default_value = 0.001
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Density", identifier="flake_density")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Normal Randomize", identifier="flake_normal_randomize").default_value = 0.2
        self.inputs.new("AiNodeSocketCoord", "Flake Coords", identifier="flake_coord_space")

        self.inputs.new('AiNodeSocketFloatNormalized', "Coat", identifier="coat")
        self.inputs.new('AiNodeSocketRGB', "Coat Color", identifier="coat_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Roughness", identifier="coat_roughness")
        self.inputs.new('AiNodeSocketFloatAboveOne', "Coat IOR", identifier="coat_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketVector', name="Coat Normal", identifier="coat_normal")

        self.outputs.new('AiNodeSocketSurface', name="RGB")

'''
AiCurvature

This shader will sample around the shading point within a given
radius to output the curvature. You can adjust the radius, falloff,
and spread of the curvature sampling as well as specify a trace set
to exclude or include objects. This shader is useful for creating
procedural wear or dirt maps in conjunction with a noise shader.
'''
class AiCurvature(bpy.types.Node, core.ArnoldNode):
    bl_label = "Curvature"
    ai_name = "curvature"

    output: EnumProperty(
        name="Output",
        items=[
            ('convex', "Convex", "Convex (positive) curvature"),
            ('concave', "Concave", "Concave (negative) curvature"),
            ('both', "Both", "Both convex and concave curvature")
        ]
    )

    samples: IntProperty(name="Samples", min=1, soft_max=10, default=3)
    self_only: BoolProperty(name="Self Only")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'self_only')
        layout.prop(self, 'output', text="")
        layout.prop(self, 'samples')

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositive', "Radius", identifier="radius").default_value = 0.1
        self.inputs.new('AiNodeSocketFloatNormalized', "Spread", identifier="spread").default_value = 1
        self.inputs.new('AiNodeSocketFloatNormalized', "Threshold", identifier="threshold")
        self.inputs.new('AiNodeSocketFloatNormalized', "Bias", identifier="bias").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatPositiveToTen', "Multiply", identifier="multiply").default_value = 1

        self.outputs.new('AiNodeSocketRGB', "RGB")

    def sub_export(self, node):
        node.set_string('output', self.output)
        node.set_uint('samples', self.samples)
        node.set_bool('self_only', self.self_only)

'''
AiDisplacement

This is a dummy node that exports displacement data to Arnold by
hijacking the polymesh node.
'''
class AiDisplacement(bpy.types.Node, core.ArnoldNode):
    bl_label = "Displacement"

    disp_autobump: BoolProperty(name="Auto Bump")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositive', "Padding", identifier="disp_padding")
        self.inputs.new('AiNodeSocketFloatUnbounded', "Height", identifier="disp_height").default_value = 1
        self.inputs.new('AiNodeSocketFloatUnbounded', "Zero Value", identifier="disp_zero_value")
        self.inputs.new('AiNodeSocketRGB', "Input", identifier="disp_map").default_value = (0, 0, 0)
        
        self.outputs.new('AiNodeSocketSurface', name="RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "disp_autobump")

    # Overriding export() because this isn't a native Arnold struct
    def export(self):
        data = (
            self.inputs[3].export(), # input
            self.inputs[0].export(), # padding
            self.inputs[1].export(), # height
            self.inputs[2].export(), # zero value
            self.disp_autobump
        )

        return DisplacementData(data)

'''
AiFlat

A simple color shader node which just allows a color with no other effects.
'''
class AiFlat(bpy.types.Node, core.ArnoldNode):
    bl_label = "Flat"
    ai_name = "flat"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="color").default_value = (1, 1, 1)
        self.outputs.new('AiNodeSocketRGB', name="RGB")

'''
AiLambert

Simple Lambertian reflectance model. Outputs a simple color (RGB).
'''
class AiLambert(bpy.types.Node, core.ArnoldNode):
    bl_label = "Lambert"
    ai_name = "lambert"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Weight", identifier="Kd").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="Kd_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Opacity", identifier="opacity").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketVector', "Normal", identifier="normal")

        self.outputs.new('AiNodeSocketSurface', name="Shader")

'''
AiMatte

Enables you to create holdout effects by rendering the alpha as zero.
'''
class AiMatte(bpy.types.Node, core.ArnoldNode):
    bl_label = "Matte"
    ai_name = "matte"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Color", identifier="color")
        self.inputs.new('AiNodeSocketRGB', "Opacity", identifier="opacity").default_value = (1, 1, 1)

        self.outputs.new('AiNodeSocketSurface', name="RGB")

'''
AiMixShader

Used to blend two shaders together.
'''
class AiMixShader(bpy.types.Node, core.ArnoldNode):
    bl_label = "Mix Shader"
    ai_name = "mix_shader"

    def toggle_mix(self, context):
        self.inputs[0].enabled = self.mode == 'blend'

    mode: EnumProperty(
        name="Mode",
        description="",
        items=[
            ('blend', "Blend", "Blend"),
            ('add', "Add", "Add")
        ],
        update=toggle_mix
    )

    add_transparency: BoolProperty(name="Add Transparency")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Mix", identifier="mix").default_value = 0.5
        self.inputs.new('AiNodeSocketSurface', name="Shader", identifier="shader1")
        self.inputs.new('AiNodeSocketSurface', name="Shader", identifier="shader2")

        self.outputs.new('AiNodeSocketSurface', name="Shader")

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode", text="")

        if self.mode == 'add':
            layout.prop(self, "add_transparency")
        
    def sub_export(self, node):
        node.set_string("mode", self.mode)
        node.set_bool("add_transparency", self.add_transparency) 

'''
AiNormalMap

Provides bump mapping cored on a 2d texture map.
'''
class AiNormalMap(bpy.types.Node, core.ArnoldNode):
    bl_label = "Normal Map"
    bl_width_default = 180
    ai_name = "normal_map"

    invert_x: BoolProperty(name="Invert X")
    invert_y: BoolProperty(name="Invert Y")
    invert_z: BoolProperty(name="Invert Z")

    color_to_signed: BoolProperty(
        name="Color To Signed",
        description="For 8-bit maps. If enabled, the input is remapped to the [-1,1] range",
        default=True
    )

    tangent_space: BoolProperty(name="Tangent Space", default=True)

    def init(self, context):
        self.inputs.new('AiNodeSocketVector', name="Input", identifier="input")
        self.inputs.new('AiNodeSocketFloatUnbounded', name="Strength", identifier="strength").default_value = 1
        self.inputs.new('AiNodeSocketVector', name="Tangent", identifier="tangent")
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector")

    def draw_buttons(self, context, layout):
        row = layout.row(heading="Invert", align=True)
        row.prop(self, "invert_x", text="X", toggle=1)
        row.prop(self, "invert_y", text="Y", toggle=1)
        row.prop(self, "invert_z", text="Z", toggle=1)
        
        col = layout.column()
        col.prop(self, "color_to_signed")
        col.prop(self, "tangent_space")

    def sub_export(self, node):
        node.set_bool("invert_x", self.invert_x)
        node.set_bool("invert_y", self.invert_y)
        node.set_bool("invert_z", self.invert_z)
        node.set_bool("color_to_signed", self.color_to_signed)
        node.set_bool("tangent_space", self.tangent_space)

'''
AiRaySwitchRGBA

This shader makes it possible to evaluate different color trees per ray.
'''
class AiRaySwitchRGBA(bpy.types.Node, core.ArnoldNode):
    bl_label = "Ray Switch RGBA"
    ai_name = "ray_switch_rgba"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Camera", identifier="camera").hide_value = True
        self.inputs.new('AiNodeSocketRGBA', "Shadow", identifier="shadow").hide_value = True
        self.inputs.new('AiNodeSocketRGBA', "Diffuse Reflection", identifier="diffuse_reflection").hide_value = True
        self.inputs.new('AiNodeSocketRGBA', "Diffuse Transmission", identifier="diffuse_transmission").hide_value = True
        self.inputs.new('AiNodeSocketRGBA', "Specular Reflection", identifier="specular_reflection").hide_value = True
        self.inputs.new('AiNodeSocketRGBA', "Specular Transmission", identifier="specular_transmission").hide_value = True
        self.inputs.new('AiNodeSocketRGBA', "Volume", identifier="volume").hide_value = True

        self.outputs.new('AiNodeSocketRGBA', "RGBA")

'''
AiRaySwitchShader

This shader makes it possible to evaluate different shader trees per ray. This decreases
the shading complexity of a scene and thus the render times, and increases artistic control.
It can be used to remove unnecessary secondary rays (specular/sss), make speculars even more
glossy in specular rays, control the color of opacity in shadow rays to fake light scattering
through tissue or add a second specular lobe in-camera rays only.
'''
class AiRaySwitchShader(bpy.types.Node, core.ArnoldNode):
    bl_label = "Ray Switch Shader"
    ai_name = "ray_switch_shader"

    def init(self, context):
        self.inputs.new('AiNodeSocketSurface', "Camera", identifier="camera")
        self.inputs.new('AiNodeSocketSurface', "Shadow", identifier="shadow")
        self.inputs.new('AiNodeSocketSurface', "Diffuse Reflection", identifier="diffuse_reflection")
        self.inputs.new('AiNodeSocketSurface', "Diffuse Transmission", identifier="diffuse_transmission")
        self.inputs.new('AiNodeSocketSurface', "Specular Reflection", identifier="specular_reflection")
        self.inputs.new('AiNodeSocketSurface', "Specular Transmission", identifier="specular_transmission")
        self.inputs.new('AiNodeSocketSurface', "Volume", identifier="volume")

        self.outputs.new('AiNodeSocketSurface', "Shader")

'''
AiShadowMatte

Typically used on floor planes to 'catch' shadows from lighting within
the scene. It is useful for integrating a rendered object onto a
photographic background.
'''
class AiShadowMatte(bpy.types.Node, core.ArnoldNode):
    bl_label = "Shadow Matte"
    bl_width_default = constant.BL_NODE_WIDTH_WIDE
    ai_name = "shadow_matte"

    background: EnumProperty(
        name="Background",
        items=[
            ("0", "Scene Background", "Scene Background"),
            ("1", "Background Color", "Background Color"),
        ]
    )

    diffuse_use_background: BoolProperty(name="Diffuse Use Background", default=True)
    indirect_diffuse_enable: BoolProperty(name="Enable Indirect Diffuse")
    indirect_specular_enable: BoolProperty(name="Enable Indirect Specular")

    alpha_mask: BoolProperty(name="Alpha Mask", default=True)

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Background Color", identifier="background_color")
        self.inputs.new('AiNodeSocketRGB', "Offscreen Color", identifier="offscreen_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketRGB', "Shadow Color", identifier="shadow_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatNormalized', "Shadow Opacity", identifier="shadow_opacity").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Diffuse Color", identifier="diffuse_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatPositive', "Diffuse Intensity", identifier="diffuse_intensity").default_value = 1
        self.inputs.new('AiNodeSocketFloatNormalized', "Backlighting", identifier="backlighting")
        self.inputs.new('AiNodeSocketRGB', "Specular Color", identifier="specular_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Intensity", identifier="specular_intensity")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.1
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.52

        self.outputs.new('AiNodeSocketSurface', name="RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "background")
        layout.prop(self, "diffuse_use_background")
        layout.prop(self, "indirect_diffuse_enable")
        layout.prop(self, "indirect_specular_enable")
        layout.prop(self, "alpha_mask")

    def sub_export(self, node):
        node.set_int("background", int(self.background))
        node.set_bool("diffuse_use_background", self.diffuse_use_background)
        node.set_bool("indirect_diffuse_enable", self.indirect_diffuse_enable)
        node.set_bool("indirect_specular_enable", self.indirect_specular_enable)
        node.set_bool("alpha_mask", self.alpha_mask)

'''
AiStandardHair

Standard_hair is a physically-cored shader to render hair and fur,
cored on the d'Eon model for specular and Zinke model for diffuse.
'''
class AiStandardHair(bpy.types.Node, core.ArnoldNode):
    bl_label = "Standard Hair"
    bl_width_default = constant.BL_NODE_WIDTH_WIDE
    ai_name = "standard_hair"

    roughness_anisotropic: BoolProperty(name="Anisotropic Roughness")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Weight", identifier="base").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Base Color", identifier="base_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Melanin", identifier="melanin").default_value = 1
        self.inputs.new('AiNodeSocketFloatNormalized', "Melanin Redness", identifier="melanin_redness").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Melanin Randomize", identifier="melanin_randomize")

        self.inputs.new('AiNodeSocketFloatNormalized', "Roughness", identifier="roughness").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatNormalized', "Azimuthal Roughness", identifier="roughness_azimuthal").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatAboveOne', "IOR", identifier="ior").default_value = 1.55
        self.inputs.new('AiNodeSocketFloatPositive', "Shift", identifier="shift").default_value = 3

        self.inputs.new('AiNodeSocketRGB', "Specular Tint", identifier="specular_tint").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Specular2 Tint", identifier="specular2_tint").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Transmission Tint", identifier="transmission_tint").default_value = (1, 1, 1)

        self.inputs.new('AiNodeSocketFloatNormalized', "Diffuse", identifier="diffuse")
        self.inputs.new('AiNodeSocketRGB', "Diffuse Color", identifier="diffuse_color").default_value = (1, 1, 1)

        self.inputs.new('AiNodeSocketFloatPositive', "Emission", identifier="emission")
        self.inputs.new('AiNodeSocketRGB', "Emission Color", identifier="emission_color").default_value = (1, 1, 1)

        self.inputs.new('AiNodeSocketRGB', "Opacity", identifier="opacity").default_value = (1, 1, 1)

        self.inputs.new('AiNodeSocketFloatPositive', "Indirect Diffuse", identifier="indirect_diffuse").default_value = 1
        self.inputs.new('AiNodeSocketFloatPositive', "Indirect Specular", identifier="indirect_specular")

        self.inputs.new('AiNodeSocketIntPositive', "Extra Depth", identifier="extra_depth").default_value = 16
        self.inputs.new('AiNodeSocketIntPositive', "Extra Samples", identifier="extra_samples")

        self.outputs.new('AiNodeSocketSurface', name="RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "roughness_anisotropic")

    def sub_export(self, node):
        node.set_bool("roughness_anisotropic", self.roughness_anisotropic)

'''
AiStandardSurface

A physically-cored shader. Outputs a simple color (RGB).
'''
class AiStandardSurface(bpy.types.Node, core.ArnoldNode):
    bl_label = "Standard Surface"
    bl_width_default = constant.BL_NODE_WIDTH_WIDE
    ai_name = "standard_surface"

    transmit_aovs: BoolProperty(name="Transmit AOVs")
    thin_walled: BoolProperty(name="Thin Walled")
    caustics: BoolProperty(name="Caustics")
    internal_reflections: BoolProperty(name="Internal Reflections", default=True)
    exit_to_background: BoolProperty(name="Exit to Background")
    subsurface_type: EnumProperty(
        name="Subsurface Type",
        items=[
            ("0", "Diffusion", "Diffusion"),
            ("1", "Randomwalk", "Randomwalk"),
            ("2", "Randomwalk v2", "Randomwalk v2"),
        ],
        default="1"
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Weight", identifier="base").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Base Color", identifier="base_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Diffuse Roughness", identifier="diffuse_roughness")
        self.inputs.new('AiNodeSocketFloatNormalized', "Metalness", identifier="metalness")

        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Weight", identifier="specular").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Specular Color", identifier="specular_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Anisotropy", identifier="specular_anisotropy")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Rotation", identifier="specular_rotation")

        self.inputs.new('AiNodeSocketFloatNormalized', "Transmission Weight", identifier="transmission")
        self.inputs.new('AiNodeSocketRGB', "Transmission Color", identifier="transmission_color").default_value = (1, 1, 1)

        trans_depth = self.inputs.new('AiNodeSocketFloatPositive', "Transmission Depth", identifier="transmission_depth")
        trans_depth.real_world = True

        self.inputs.new('AiNodeSocketRGB', "Transmission Scatter", identifier="transmission_scatter").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatUnbounded', "Transmission Scatter Anisotropy", identifier="transmission_scatter_anisotropy")
        self.inputs.new('AiNodeSocketFloatPositive', "Transmission Dispersion", identifier="transmission_dispersion")
        self.inputs.new('AiNodeSocketFloatNormalizedAlt', "Transmission Extra Roughness", identifier="transmission_extra_roughness")
        self.inputs.new('AiNodeSocketIntUnbounded', "Dielectric Priority", identifier="dielectric_priority")

        self.inputs.new('AiNodeSocketFloatNormalized', "SSS Weight", identifier="subsurface")
        self.inputs.new('AiNodeSocketRGB', "SSS Color", identifier="subsurface_color").default_value = (1, 1, 1)
        
        sss_radius = self.inputs.new('AiNodeSocketRGB', "SSS Radius", identifier="subsurface_radius")
        sss_radius.default_value = (1, 1, 1)
        sss_radius.real_world = True
        
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Scale", identifier="subsurface_scale").default_value = 1
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Anisotropy", identifier="subsurface_anisotropy")

        self.inputs.new('AiNodeSocketFloatNormalized', "Coat", identifier="coat")
        self.inputs.new('AiNodeSocketRGB', "Coat Color", identifier="coat_color").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Roughness", identifier="coat_roughness").default_value = 0.1
        self.inputs.new('AiNodeSocketFloatAboveOne', "Coat IOR", identifier="coat_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketFloatUnbounded', "Coat Anisotropy", identifier="coat_anisotropy")
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Rotation", identifier="coat_rotation")
        self.inputs.new('AiNodeSocketVector', "Coat Normal", identifier="coat_normal")
        self.inputs.new('AiNodeSocketFloatUnbounded', "Coat Affect Color", identifier="coat_affect_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Affect Roughness", identifier="coat_affect_roughness")

        self.inputs.new('AiNodeSocketFloatPositive', "Sheen", identifier="sheen")
        self.inputs.new('AiNodeSocketRGB', "Sheen Color", identifier="sheen_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatNormalized', "Sheen Roughness", identifier="sheen_roughness").default_value = 0.3

        self.inputs.new('AiNodeSocketFloatPositive', "Emission", identifier="emission")
        self.inputs.new('AiNodeSocketRGB', "Emission Color", identifier="emission_color").default_value = (1, 1, 1)

        self.inputs.new('AiNodeSocketFloatPositive', "Thin Film Thickness", identifier="thin_film_thickness")
        self.inputs.new('AiNodeSocketFloatAboveOne', "Thin Film IOR", identifier="thin_film_IOR").default_value = 1.5

        self.inputs.new('AiNodeSocketRGB', "Opacity", identifier="opacity").default_value = (1, 1, 1)

        self.inputs.new('AiNodeSocketVector', "Normal", identifier="normal")
        self.inputs.new('AiNodeSocketVector', "Tangent", identifier="tangent")

        self.outputs.new('AiNodeSocketSurface', name="RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "transmit_aovs")
        layout.prop(self, "thin_walled")
        layout.prop(self, "caustics")
        layout.prop(self, "internal_reflections")
        layout.prop(self, "exit_to_background")
        layout.prop(self, "subsurface_type")

    def sub_export(self, node):
        node.set_bool("transmit_aovs", self.transmit_aovs)
        node.set_bool("thin_walled", self.thin_walled)
        node.set_bool("caustics", self.caustics)
        node.set_bool("internal_reflections", self.internal_reflections)
        node.set_bool("exit_to_background", self.exit_to_background)
        node.set_int("subsurface_type", int(self.subsurface_type))

'''
AiTwoSided

Applies two shaders on either side of a double sided surface.
'''
class AiTwoSided(bpy.types.Node, core.ArnoldNode):
    bl_label = "Two Sided"
    ai_name = "two_sided"

    def init(self, context):
        self.inputs.new('AiNodeSocketSurface', "Front", identifier="front")
        self.inputs.new('AiNodeSocketSurface', "Back", identifier="back")
        
        self.outputs.new('AiNodeSocketSurface', name="Closure")

'''
AiWireframe

Color shader which produces a wire-frame style output (as RGB).
'''
class AiWireframe(bpy.types.Node, core.ArnoldNode):
    bl_label = "Wireframe"
    ai_name = "wireframe"

    edge_type: EnumProperty(
        name="Edge Type",
        items=[
            ('0', 'Triangles', 'Triangles'),
            ('1', 'Polygons', 'Polygons')
        ],
        default='0'
        )

    raster_space: BoolProperty(name="Raster Space", default=True)

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Fill Color", identifier="fill_color")
        self.inputs.new('AiNodeSocketRGB', "Line Color", identifier="line_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatPositive', "Line Width", identifier="line_width").default_value = 1

        self.outputs.new('AiNodeSocketSurface', name="RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "edge_type")
        layout.prop(self, "raster_space")

    def sub_export(self, node):
        node.set_int("edge_type", int(self.edge_type))
        node.set_bool("raster_space", self.raster_space)

classes = (
    AiAmbientOcclusion,
    AiCarPaint,
    AiCurvature,
    AiDisplacement,
    AiFlat,
    AiLambert,
    AiMatte,
    AiMixShader,
    AiNormalMap,
    AiRaySwitchRGBA,
    AiRaySwitchShader,
    AiShadowMatte,
    AiStandardHair,
    AiStandardSurface,
    AiTwoSided,
    AiWireframe,
)

def register():
    register_utils.register_classes(classes)

def unregister():
    register_utils.unregister_classes(classes)