import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiLambertShader(Node, ArnoldNode):
    '''Simple Lambertian reflectance model. Outputs a simple color (RGB).'''
    bl_label = "Lambert"
    bl_icon = 'MATERIAL'

    ai_name = "lambert"

    def init(self, context):
        self.inputs.new('NodeSocketColor', name="Color", identifier="kd_color")
        self.inputs.new('NodeSocketFloat', name="Weight", identifier="kd")
        self.inputs.new('NodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('NodeSocketShader', name="RGB", identifier="output")

def register():
    bpy.utils.register_class(AiLambertShader)

def unregister():
    bpy.utils.unregister_class(AiLambertShader)