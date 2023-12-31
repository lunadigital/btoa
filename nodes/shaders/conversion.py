import bpy
from bpy.props import *
from .. import core
from ..sockets import utils as socket_utils
from ...utils import register_utils
from ...bridge import ExportDataType

'''
AiFloatToInteger

Converts float to an integer value.
'''
class AiFloatToInteger(bpy.types.Node, core.ArnoldNode):
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
        self.inputs.new('AiNodeSocketFloatNoSlider', "Value", identifier="input")
        self.outputs.new('AiNodeSocketIntUnbounded', "Integer")

    def sub_export(self, node):
        node.set_string('mode', self.mode)

'''
AiFloatToRGB

Creates RGB color from individual R, G, B float values.
'''
class AiFloatToRGB(bpy.types.Node, core.ArnoldNode):
    bl_label = "Float To RGB"
    ai_name = "float_to_rgb"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositive', "R", identifier="r")
        self.inputs.new('AiNodeSocketFloatPositive', "G", identifier="g")
        self.inputs.new('AiNodeSocketFloatPositive', "B", identifier="b")

        self.outputs.new('AiNodeSocketRGB', name="RGB", identifier="output")

'''
AiFloatToRGBA

Creates RGBA color from R, G, B, A float values.
'''
class AiFloatToRGBA(bpy.types.Node, core.ArnoldNode):
    bl_label = "Float to RGBA"
    ai_name = "float_to_rgba"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositive', "R", identifier="r")
        self.inputs.new('AiNodeSocketFloatPositive', "G", identifier="g")
        self.inputs.new('AiNodeSocketFloatPositive', "B", identifier="b")
        self.inputs.new('AiNodeSocketFloatPositive', "A", identifier="a")
        
        self.outputs.new('AiNodeSocketRGB', name="RGBA", identifier="output")

'''
AiRGBToFloat

Converts RGB color to float value.
'''
class AiRGBToFloat(bpy.types.Node, core.ArnoldNode):
    bl_label = "RGB to Float"
    ai_name = "rgb_to_float"

    mode: EnumProperty(
        name="Mode",
        items=[
            ('min', "Min", "Minimum of the color and alpha channels"),
            ('max', "Max", "Maximum of the color and alpha channels"),
            ('average', "Average", "Average of the color and alpha channels"),
            ('sum', "Sum", "Sum of the color and alpha channels"),
            ('luminance', "Luminance", "sRGB luminance mix, multiplied by alpha"),
            ('r', "R", "Red channel only"),
            ('g', "G", "Green channel only"),
            ('b', "B", "Blue channel only")
        ],
        default="average"
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode", text="")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="input").default_value = (0, 0, 0)
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float")

    def sub_export(self, node):
        node.set_string("mode", self.mode)

'''
AiRGBToVector

Converts RGB color to vector.
'''
class AiRGBToVector(bpy.types.Node, core.ArnoldNode):
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
AiRGBAToFloat

Converts RGB color and alpha value to float.
'''
class AiRGBAToFloat(bpy.types.Node, core.ArnoldNode):
    bl_label = "RGBA to Float"
    ai_name = "rgba_to_float"

    mode: EnumProperty(
        name="Mode",
        items=[
            ('min', "Min", "Minimum of the color and alpha channels"),
            ('max', "Max", "Maximum of the color and alpha channels"),
            ('average', "Average", "Average of the color and alpha channels"),
            ('sum', "Sum", "Sum of the color and alpha channels"),
            ('luminance', "Luminance", "sRGB luminance mix, multiplied by alpha"),
            ('r', "R", "Red channel only"),
            ('g', "G", "Green channel only"),
            ('b', "B", "Blue channel only"),
            ('a', "A", "Alpha channel only")
        ],
        default="average"
    )

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode", text="")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Color", identifier="input").default_value = (0, 0, 0, 1)
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float")

    def sub_export(self, node):
        node.set_string("mode", self.mode)

'''
AiSeparateRGBA

This is a dummy node to separate RGBA inputs into their component R/G/B/A outputs.
'''
class AiSeparateRGBA(bpy.types.Node, core.ArnoldNode):
    bl_label = "Separate RGBA"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Color").default_value = (1, 1, 1, 1)
        
        self.outputs.new('AiNodeSocketFloatUnbounded', "R", identifier="r")
        self.outputs.new('AiNodeSocketFloatUnbounded', "G", identifier="g")
        self.outputs.new('AiNodeSocketFloatUnbounded', "B", identifier="b")
        self.outputs.new('AiNodeSocketFloatUnbounded', "A", identifier="a")

    def export(self):
        socket_data = self.inputs[0].export()
            
        if socket_data.type is ExportDataType.NODE:
            return socket_data
        else:
            key = socket_data.type
            if socket_data.type is ExportDataType.COLOR:
                key = ExportDataType.RGBA if socket_data.has_alpha() else ExportDataType.RGB
                
            bridge.BTOA_SET_LAMBDA[key](node, i.identifier, socket_data.value)

            return socket_data

'''
AiVectorToRGB

Converts vector to RGB color.
'''
class AiVectorToRGB(bpy.types.Node, core.ArnoldNode):
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
        self.inputs.new('AiNodeSocketVector', "Vector", identifier="input").show_value = True
        self.outputs.new('AiNodeSocketRGB', "RGB")

    def sub_export(self, node):
        node.set_string('mode', self.mode)

classes = (
    AiFloatToInteger,
    AiFloatToRGB,
    AiFloatToRGBA,
    AiRGBToFloat,
    AiRGBToVector,
    AiRGBAToFloat,
    AiSeparateRGBA,
    AiVectorToRGB,
)

def register():
    register_utils.register_classes(classes)

def unregister():
    register_utils.unregister_classes(classes)