import bpy
from .. import base
from ... import utils

'''
AiFloatToRGB
https://docs.arnoldrenderer.com/display/A5NodeRef/float_to_rgb

Creates RGB color from individual R, G, B float values.
'''
class AiFloatToRGB(bpy.types.Node, base.ArnoldNode):
    bl_label = "Float To RGB"
    ai_name = "float_to_rgb"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositive', "R", identifier="r")
        self.inputs.new('AiNodeSocketFloatPositive', "G", identifier="g")
        self.inputs.new('AiNodeSocketFloatPositive', "B", identifier="b")

        self.outputs.new('AiNodeSocketRGB', name="RGB", identifier="output")

'''
AiFloatToRGBA
https://docs.arnoldrenderer.com/display/A5NodeRef/float_to_rgba

Creates RGBA color from R, G, B, A float values.
'''
class AiFloatToRGBA(bpy.types.Node, base.ArnoldNode):
    bl_label = "Float to RGBA"
    ai_name = "float_to_rgba"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositive', "R", identifier="r")
        self.inputs.new('AiNodeSocketFloatPositive', "G", identifier="g")
        self.inputs.new('AiNodeSocketFloatPositive', "B", identifier="b")
        self.inputs.new('AiNodeSocketFloatPositive', "A", identifier="a")
        
        self.outputs.new('AiNodeSocketRGB', name="RGBA", identifier="output")

classes = (
    AiFloatToRGB,
    AiFloatToRGBA,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)