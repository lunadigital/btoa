import bpy
from bpy.types import Node
from bpy.props import FloatProperty, FloatVectorProperty

from ..base import ArnoldNode
from .. import constants

class AiLambert(Node, ArnoldNode):
    '''Simple Lambertian reflectance model. Outputs a simple color (RGB).'''
    bl_label = "Lambert"
    bl_width_default = constants.BL_NODE_WIDTH_DEFAULT
    bl_icon = 'MATERIAL'

    ai_name = "lambert"

    def init(self, context):
        color = self.inputs.new('AiNodeSocketRGB', "Color", identifier="Kd_color")
        weight = self.inputs.new('AiNodeSocketFloatNormalized', "Weight", identifier="Kd").default_value = 0.8
        #normal = self.inputs.new('NodeSocketVector', "Normal")

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

def register():
    bpy.utils.register_class(AiLambert)

def unregister():
    bpy.utils.unregister_class(AiLambert)