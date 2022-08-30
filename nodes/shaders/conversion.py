import bpy
from bpy.props import *
from .. import base
from ..sockets import utils as socket_utils
from ... import utils

'''
AiFloatToInteger
https://docs.arnoldrenderer.com/display/A5NodeRef/float_to_int

Converts float to an integer value.
'''
class AiFloatToInteger(bpy.types.Node, base.ArnoldNode):
    bl_label = "Float to Integer"
    ai_name = "float_to_int"

    mode: EnumProperty(
        name="Mode",
        items=[
            ('round', "Round", "Round to nearest"),
            ('truncate', "Truncate", "Drop the fractional part"),
            ('floor', "Floor", "Round down"),
            ('ceil', "Ceiling", "Round up")
        ]
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, 'mode', text="")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatUnbounded', "Value", identifier="input")
        self.outputs.new('AiNodeSocketIntUnbounded', "Integer")

    def sub_export(self, node):
        node.set_string('mode', self.mode)

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
AiRGBToVector
https://docs.arnoldrenderer.com/display/A5NodeRef/rgb_to_vector

Converts RGB color to vector.
'''
class AiRGBToVector(bpy.types.Node, base.ArnoldNode):
    bl_label = "RGB to Vector"
    ai_name = "rgb_to_vector"

    mode: EnumProperty(
        name="Mode",
        items=[
            ('raw', "Raw", "Map XYZ values to RGB channels directly"),
            ('canonical', "Canonical", "Map -1..1 XYZ values to 0..1 RGB channels")
        ]
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, 'mode', text="")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="input").default_value = (0, 0, 0)
        self.outputs.new('AiNodeSocketVector', "Vector")

    def sub_export(self, node):
        node.set_string('mode', self.mode)

'''
AiSeparateRGBA

This is a dummy node to separate RGBA inputs into their component R/G/B/A outputs.
'''
class AiSeparateRGBA(bpy.types.Node, base.ArnoldNode):
    bl_label = "Separate RGBA"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Color").default_value = (1, 1, 1, 1)
        
        # The first socket is always the default output. For the other sockets
        # to return the proper values, we'll create an RGBA output but hide it
        # in the UI.
        self.outputs.new('AiNodeSocketRGBA', "RGBA").hide = True
        self.outputs.new('AiNodeSocketFloatUnbounded', "R")
        self.outputs.new('AiNodeSocketFloatUnbounded', "G")
        self.outputs.new('AiNodeSocketFloatUnbounded', "B")
        self.outputs.new('AiNodeSocketFloatUnbounded', "A")

    def export(self):
        socket_value, value_type, output_type = self.inputs[0].export()

        if socket_value is not None and value_type is not None:
            if value_type == 'BTNODE':
                return socket_value, value_type
            else:
                btoa.BTOA_SET_LAMBDA[value_type](node, i.identifier, socket_value)
                return socket_value, value_type

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
    AiFloatToInteger,
    AiFloatToRGB,
    AiFloatToRGBA,
    AiRGBToVector,
    AiSeparateRGBA,
    AiVectorToRGB,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)