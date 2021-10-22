import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiMixRGBA(Node, ArnoldNode):
    '''
    The mix_RGBA is used to blend or add two colors or textures. It
    returns a linear interpolation of input1 and input2 according to
    the mix_weight attribute. A mix_weight value of 0 outputs input1,
    a value of 1 outputs input2, and a value of 0.5 mixes evenly
    between input1 and input2.
    '''
    bl_label = "Mix RGBA"

    ai_name = "mix_rgba"

    def init(self, context):
        self.inputs.new("AiNodeSocketFloatNormalized", "Mix", identifier="mix").default_value = 0.5
        self.inputs.new("AiNodeSocketRGBA", "Input 1", identifier="input1")
        self.inputs.new("AiNodeSocketRGBA", "Input 2", identifier="input2").default_value = (0, 0, 0, 1)

        self.outputs.new('AiNodeSocketRGBA', name="RGBA", identifier="output")
            
def register():
    bpy.utils.register_class(AiMixRGBA)

def unregister():
    bpy.utils.unregister_class(AiMixRGBA)