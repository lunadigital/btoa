import bpy
from bpy.types import Node

from ..base import ArnoldNodeOutput

class AiShaderOutput(Node, ArnoldNodeOutput):
    '''Output node for Arnold shaders.'''
    bl_icon = 'MATERIAL'
    bl_label = "Shader Output"

    def init(self, context):
        super().init(context)

        self.inputs.new(type="ArnoldNodeSocketSurface", name="Surface", identifier="surface")
        #self.inputs.new(type="NodeSocketShader", name="Volume", identifier="volume")
        #self.inputs.new(type="NodeSocketShader", name="Displacement", identifier="displacement")

    def export(self):
        # Will replace these Nones with volume and displacement later
        return self.inputs["Surface"].export(), None, None

def register():
    bpy.utils.register_class(AiShaderOutput)

def unregister():
    bpy.utils.unregister_class(AiShaderOutput)