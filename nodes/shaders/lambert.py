import bpy
from bpy.types import Node
from bpy.props import FloatProperty, FloatVectorProperty

from ..base import ArnoldNode

from arnold import *

class AiLambertShader(Node, ArnoldNode):
    '''Simple Lambertian reflectance model. Outputs a simple color (RGB).'''
    bl_label = "Lambert"
    bl_icon = 'MATERIAL'

    ai_name = "lambert"

    def init(self, context):
        color = self.inputs.new('ArnoldNodeSocketColor', "Color", identifier="Kd_color")
        weight = self.inputs.new('NodeSocketFloat', "Weight", identifier="Kd").default_value = 0.8
        #normal = self.inputs.new('NodeSocketVector', "Normal")

        self.outputs.new('ArnoldNodeSocketSurface', name="RGB", identifier="output")
    
    def sub_export(self, node):
        # TODO: Figure out how to replace with btoa.AiNodeSet
        color, value_type = self.inputs["Color"].export()
        weight = self.inputs["Weight"].default_value

        AiNodeSetRGB(
            node,
            "Kd_color",
            *color
        )

        AiNodeSetFlt(node, "Kd", weight)

        return node

def register():
    bpy.utils.register_class(AiLambertShader)

def unregister():
    bpy.utils.unregister_class(AiLambertShader)