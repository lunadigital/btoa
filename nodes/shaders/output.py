import bpy
from bpy.types import Node

from ..base import ArnoldNodeOutput

class AiShaderOutput(Node, ArnoldNodeOutput):
    '''Output node for Arnold shaders.'''
    bl_icon = 'MATERIAL'

    def init(self, context):
        super().init(context)

        self.inputs.new(type="NodeSocketShader", name="Surface", identifier="surface")
        self.inputs.new(type="NodeSocketShader", name="Volume", identifier="volume")
        self.inputs.new(type="NodeSocketShader", name="Displacement", identifier="displacement")

def register():
    bpy.utils.register_class(AiShaderOutput)

def unregister():
    bpy.utils.unregister_class(AiShaderOutput)