import bpy
from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

from arnold import *

class AiStandardSurfaceShader(Node, ArnoldNode):
    '''A physically-based shader. Outputs a simple color (RGB).'''
    bl_label = "Standard Surface"
    bl_icon = 'MATERIAL'

    ai_name = "standard_surface"

    transmit_aovs: BoolProperty(name="Transmit AOVs")
    thin_walled: BoolProperty(name="Thin Walled")
    thin_walled_translucency: BoolProperty(name="Thin Walled Translucency")
    caustics: BoolProperty(name="Caustics")
    internal_reflections: BoolProperty(name="Internal Reflections", default=True)

    def init(self, context):
        # Initialize sockets
        base = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Base Weight", identifier="base").default_value = 1
        base_color = self.inputs.new('ArnoldNodeSocketColor', "Base Color", identifier="base_color")
        diffuse_roughness = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Diffuse Roughness", identifier="diffuse_roughness")

        metalness = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Metalness", identifier="metalness")

        specular = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Specular Weight", identifier="specular").default_value = 1
        specular_color = self.inputs.new('ArnoldNodeSocketColor', "Specular Color", identifier="specular_color")
        specular_roughness = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.2
        specular_ior = self.inputs.new('ArnoldNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_ior").default_value = 1.5
        specular_anisotropy = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Specular Anisotropy", identifier="specular_anisotropy")
        specular_rotation = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Specular Rotation", identifier="specular_rotation")

        transmission = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Transmission Weight", identifier="transmission")
        transmission_color = self.inputs.new('ArnoldNodeSocketColor', "Transmission Color", identifier="transmission_color")
        transmission_scatter = self.inputs.new('ArnoldNodeSocketColor', "Transmission Scatter", identifier="transmission_scatter").default_value = (0, 0, 0)
        transmission_scatter_anisotropy = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "Transmission Scatter Anisotropy", identifier="transmission_scatter_anisotropy")
        transmission_dispersion = self.inputs.new('ArnoldNodeSocketFloatPositive', "Transmission Dispersion", identifier="transmission_dispersion")
        transmission_extra_roughness = self.inputs.new('ArnoldNodeSocketFloatNormalizedAlt', "Transmission Extra Roughness", identifier="transmission_extra_roughness")

        subsurface = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "SSS Weight", identifier="subsurface")
        subsurface_color = self.inputs.new('ArnoldNodeSocketColor', "SSS Color", identifier="subsurface_color")
        subsurface_radius = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "SSS Radius", identifier="subsurface_radius")
        subsurface_scale = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "SSS Scale", identifier="subsurface_scale")
        subsurface_anisotropy = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "SSS Anisotropy", identifier="subsurface_anisotropy")
        # subsurface_type needs to be enum - is this even possible in a socket?

        # normal map
        # tangent map

        coat = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Coat", identifier="coat")
        coat_color = self.inputs.new('ArnoldNodeSocketColor', "Coat Color", identifier="coat_color")
        coat_roughness = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Coat Roughness", identifier="coat_roughness").default_value = 0.1
        coat_ior = self.inputs.new('ArnoldNodeSocketFloatAboveOne', "Coat IOR", identifier="coat_IOR")
        coat_anisotropy = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "Coat Anisotropy", identifier="coat_anisotropy")
        coat_rotation = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Coat Rotation", identifier="coat_rotation")
        # coat_normal
        coat_affect_color = self.inputs.new('ArnoldNodeSocketFloatUnbounded', "Coat Affect Color", identifier="coat_affect_color")
        coat_affect_roughness = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Coat Affect Roughness", identifier="coat_affect_roughness")

        emission = self.inputs.new('ArnoldNodeSocketFloatPositive', "Emission", identifier="emission")
        emission_color = self.inputs.new('ArnoldNodeSocketColor', "Emission Color", identifier="emission_color")

        opacity = self.inputs.new('ArnoldNodeSocketFloatNormalized', "Opacity", identifier="opacity").default_value = 1

        self.outputs.new('ArnoldNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "transmit_aovs")
        layout.prop(self, "thin_walled")
        layout.prop(self, "thin_walled_translucency")
        layout.prop(self, "caustics")
        layout.prop(self, "internal_reflections")

    def sub_export(self, ainode):
        AiNodeSetBool(ainode, "transmit_aovs", self.transmit_aovs)
        AiNodeSetBool(ainode, "thin_walled", self.thin_walled)
        AiNodeSetBool(ainode, "thin_walled_translucency", self.thin_walled_translucency)
        AiNodeSetBool(ainode, "caustics", self.caustics)
        AiNodeSetBool(ainode, "internal_reflections", self.internal_reflections)

def register():
    bpy.utils.register_class(AiStandardSurfaceShader)

def unregister():
    bpy.utils.unregister_class(AiStandardSurfaceShader)