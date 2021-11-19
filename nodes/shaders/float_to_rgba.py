import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiFloatToRGBA(Node, ArnoldNode):
    ''' Creates RGBA color from R, G, B, A float values. '''
    bl_label = "Float To RGBA"
    bl_icon = 'NONE'

    ai_name = "float_to_rgba"

    def init(self, context):
        # I don't know if the output RGB values are normalized or not
        # Arnold Node Reference doesn't say one way or another
        # Leaving unnormalized for now just in case
        self.inputs.new('AiNodeSocketFloatPositive', "R", identifier="r")
        self.inputs.new('AiNodeSocketFloatPositive', "G", identifier="g")
        self.inputs.new('AiNodeSocketFloatPositive', "B", identifier="b")
        self.inputs.new('AiNodeSocketFloatPositive', "A", identifier="a")

        self.outputs.new('AiNodeSocketRGB', name="RGBA", identifier="output")

def register():
    bpy.utils.register_class(AiFloatToRGBA)

def unregister():
    bpy.utils.unregister_class(AiFloatToRGBA)