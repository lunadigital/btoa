import bpy
from bpy.props import *
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

'''
AiVectorToRGB
https://docs.arnoldrenderer.com/display/A5NodeRef/vector_to_rgb

Converts vector to RGB color.
'''
class AiVectorToRGB(bpy.types.Node, base.ArnoldNode):
    bl_label = "Vector to RGB"
    ai_name = "vector_to_rgb"

    mode: EnumProperty(
        name="Mode",
        items=[
            ('raw', "Raw", "Map XYZ values to RGB channels directly"),
            ('normalized', "Normalized", "Normalize vector, then map XYZ values to RGB channels"),
            ('canonical', "Canonical", "Map -1..1 XYZ values to 0..1 RGB channels")
        ]
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, 'mode', text="")

    def init(self, context):
        self.inputs.new('AiNodeSocketVector', "Vector", identifier="input").show_socket_value = True
        self.outputs.new('AiNodeSocketRGB', "RGB")

    def sub_export(self, node):
        node.set_string('mode', self.mode)

classes = (
    AiFloatToRGB,
    AiFloatToRGBA,
    AiVectorToRGB,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)