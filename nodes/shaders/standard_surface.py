import bpy
from bpy.types import Node
from bpy.props import BoolProperty, EnumProperty

from ..base import ArnoldNode

from arnold import *

class AiStandardSurface(Node, ArnoldNode):
    '''A physically-based shader. Outputs a simple color (RGB).'''
    bl_label = "Standard Surface"
    bl_icon = 'MATERIAL'

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
        self.inputs.new('AiNodeSocketRGB', "Specular Color", identifier="specular_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Anisotropy", identifier="specular_anisotropy")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Rotation", identifier="specular_rotation")

        self.inputs.new('AiNodeSocketFloatNormalized', "Transmission Weight", identifier="transmission")
        self.inputs.new('AiNodeSocketRGB', "Transmission Color", identifier="transmission_color")
        self.inputs.new('AiNodeSocketFloatPositive', "Transmission Depth", identifier="transmission_depth")
        self.inputs.new('AiNodeSocketRGB', "Transmission Scatter", identifier="transmission_scatter").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatUnbounded', "Transmission Scatter Anisotropy", identifier="transmission_scatter_anisotropy")
        self.inputs.new('AiNodeSocketFloatPositive', "Transmission Dispersion", identifier="transmission_dispersion")
        self.inputs.new('AiNodeSocketFloatNormalizedAlt', "Transmission Extra Roughness", identifier="transmission_extra_roughness")

        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Weight", identifier="subsurface")
        self.inputs.new('AiNodeSocketRGB', "SSS Color", identifier="subsurface_color")
        self.inputs.new('AiNodeSocketRGB', "SSS Radius", identifier="subsurface_radius").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Scale", identifier="subsurface_scale")
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Anisotropy", identifier="subsurface_anisotropy")

        # normal map
        # tangent map

        self.inputs.new('AiNodeSocketFloatNormalized', "Coat", identifier="coat")
        self.inputs.new('AiNodeSocketRGB', "Coat Color", identifier="coat_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Roughness", identifier="coat_roughness").default_value = 0.1
        self.inputs.new('AiNodeSocketFloatAboveOne', "Coat IOR", identifier="coat_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketFloatUnbounded', "Coat Anisotropy", identifier="coat_anisotropy")
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Rotation", identifier="coat_rotation")
        # coat_normal
        self.inputs.new('AiNodeSocketFloatUnbounded', "Coat Affect Color", identifier="coat_affect_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Affect Roughness", identifier="coat_affect_roughness")

        self.inputs.new('AiNodeSocketFloatPositive', "Emission", identifier="emission")
        self.inputs.new('AiNodeSocketRGB', "Emission Color", identifier="emission_color")

        self.inputs.new('AiNodeSocketRGB', "Opacity", identifier="opacity").default_value = (1, 1, 1)

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "transmit_aovs")
        layout.prop(self, "thin_walled")
        layout.prop(self, "caustics")
        layout.prop(self, "internal_reflections")
        layout.prop(self, "exit_to_background")
        layout.prop(self, "subsurface_type")

    def sub_export(self, ainode):
        AiNodeSetBool(ainode, "transmit_aovs", self.transmit_aovs)
        AiNodeSetBool(ainode, "thin_walled", self.thin_walled)
        AiNodeSetBool(ainode, "caustics", self.caustics)
        AiNodeSetBool(ainode, "internal_reflections", self.internal_reflections)
        AiNodeSetBool(ainode, "exit_to_background", self.exit_to_background)
        AiNodeSetInt(ainode, "subsurface_type", int(self.subsurface_type))

def register():
    bpy.utils.register_class(AiStandardSurface)

def unregister():
    bpy.utils.unregister_class(AiStandardSurface)