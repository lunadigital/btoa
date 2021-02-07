import bpy
from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

from arnold import *

class AiStandardSurface(Node, ArnoldNode):
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
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Weight", identifier="base").default_value = 1
        self.inputs.new('AiNodeSocketColorRGB', "Base Color", identifier="base_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Diffuse Roughness", identifier="diffuse_roughness")

        self.inputs.new('AiNodeSocketFloatNormalized', "Metalness", identifier="metalness")

        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Weight", identifier="specular").default_value = 1
        self.inputs.new('AiNodeSocketColorRGB', "Specular Color", identifier="specular_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Anisotropy", identifier="specular_anisotropy")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Rotation", identifier="specular_rotation")

        self.inputs.new('AiNodeSocketFloatNormalized', "Transmission Weight", identifier="transmission")
        self.inputs.new('AiNodeSocketColorRGB', "Transmission Color", identifier="transmission_color")
        self.inputs.new('AiNodeSocketColorRGB', "Transmission Scatter", identifier="transmission_scatter").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatUnbounded', "Transmission Scatter Anisotropy", identifier="transmission_scatter_anisotropy")
        self.inputs.new('AiNodeSocketFloatPositive', "Transmission Dispersion", identifier="transmission_dispersion")
        #self.inputs.new('AiNodeSocketFloatNormalizedAlt', "Transmission Extra Roughness", identifier="transmission_extra_roughness")

        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Weight", identifier="subsurface")
        self.inputs.new('AiNodeSocketColorRGB', "SSS Color", identifier="subsurface_color")
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Radius", identifier="subsurface_radius")
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Scale", identifier="subsurface_scale")
        self.inputs.new('AiNodeSocketFloatUnbounded', "SSS Anisotropy", identifier="subsurface_anisotropy")
        # subsurface_type needs to be enum - is this even possible in a socket?

        # normal map
        # tangent map

        coat = self.inputs.new('AiNodeSocketFloatNormalized', "Coat", identifier="coat")
        coat_color = self.inputs.new('AiNodeSocketColorRGB', "Coat Color", identifier="coat_color")
        coat_roughness = self.inputs.new('AiNodeSocketFloatNormalized', "Coat Roughness", identifier="coat_roughness").default_value = 0.1
        coat_ior = self.inputs.new('AiNodeSocketFloatAboveOne', "Coat IOR", identifier="coat_IOR").default_value = 1.5
        coat_anisotropy = self.inputs.new('AiNodeSocketFloatUnbounded', "Coat Anisotropy", identifier="coat_anisotropy")
        coat_rotation = self.inputs.new('AiNodeSocketFloatNormalized', "Coat Rotation", identifier="coat_rotation")
        # coat_normal
        coat_affect_color = self.inputs.new('AiNodeSocketFloatUnbounded', "Coat Affect Color", identifier="coat_affect_color")
        coat_affect_roughness = self.inputs.new('AiNodeSocketFloatNormalized', "Coat Affect Roughness", identifier="coat_affect_roughness")

        emission = self.inputs.new('AiNodeSocketFloatPositive', "Emission", identifier="emission")
        emission_color = self.inputs.new('AiNodeSocketColorRGB', "Emission Color", identifier="emission_color")

        opacity = self.inputs.new('AiNodeSocketFloatNormalized', "Opacity", identifier="opacity").default_value = 1

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

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
    bpy.utils.register_class(AiStandardSurface)

def unregister():
    bpy.utils.unregister_class(AiStandardSurface)