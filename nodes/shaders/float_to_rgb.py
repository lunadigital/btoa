import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiFloatToRGB(Node, ArnoldNode):
    ''' Creates RGB color from individual R, G, B float values. '''
    bl_label = "Float To RGB"
    bl_icon = 'NONE'

    ai_name = "float_to_rgb"

    def init(self, context):
        # I don't know if the output RGB values are normalized or not
        # Arnold Node Reference doesn't say one way or another
        # Leaving unnormalized for now just in case
        self.inputs.new('AiNodeSocketFloatPositive', "R", identifier="r")
        self.inputs.new('AiNodeSocketFloatPositive', "G", identifier="g")
        self.inputs.new('AiNodeSocketFloatPositive', "B", identifier="b")

        self.outputs.new('AiNodeSocketRGB', name="RGB", identifier="output")

def register():
    bpy.utils.register_class(AiFloatToRGB)

def unregister():
    bpy.utils.unregister_class(AiFloatToRGB)