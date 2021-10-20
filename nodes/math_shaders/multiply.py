import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiMultiply(Node, ArnoldNode):
    ''' '''
    bl_label = "Multiply"
    bl_icon = 'NONE'
    
    ai_name = "multiply"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Input 1", identifier="input1").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Input 2", identifier="input2").default_value = (1, 1, 1)

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

def register():
    bpy.utils.register_class(AiMultiply)

def unregister():
    bpy.utils.unregister_class(AiMultiply)