import bpy
from bpy.props import *
from .. import core
from ...bridge import FloatData, VectorData
from ...utils import register_utils

'''
AiFloat

This is a dummy node that mimics the Cycles/EEVEE "Value" node for outputing a single float value.
'''


class AiFloat(bpy.types.Node):
    bl_label = "Float"

    value: FloatProperty(name="Float")

    def init(self, context):
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float")

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")

    # Overriding export() because this isn't a native Arnold struct
    def export(self):
        return FloatData(self.value)


'''
AiVector

This is a dummy node that outputs a 3D vector value.
'''


class AiVector(bpy.types.Node):
    bl_label = "Vector"

    value: FloatVectorProperty(name="Vector")

    def init(self, context):
        self.outputs.new('AiNodeSocketVector', "Vector")

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "value", text="")

    # Overriding export() because this isn't a native Arnold struct
    def export(self):
        return VectorData(self.value)


'''
AiUserDataFloat

Reads a named float attribute from geometry at shade time.
Used to access custom per-object or per-primitive attributes exported as Arnold user data.
'''


class AiUserDataFloat(bpy.types.Node, core.ArnoldNode):
    bl_label = "User Data Float"
    ai_name = "user_data_float"

    attribute: StringProperty(name="Attribute", description="Name of the float attribute to read")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatUnbounded', "Default", identifier="default")
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float")

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text="")

    def sub_export(self, node):
        node.set_string("attribute", self.attribute)


'''
AiUserDataInt

Reads a named integer attribute from geometry at shade time.
'''


class AiUserDataInt(bpy.types.Node, core.ArnoldNode):
    bl_label = "User Data Int"
    ai_name = "user_data_int"

    attribute: StringProperty(name="Attribute", description="Name of the integer attribute to read")

    def init(self, context):
        self.inputs.new('AiNodeSocketIntUnbounded', "Default", identifier="default")
        self.outputs.new('AiNodeSocketIntUnbounded', "Int")

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text="")

    def sub_export(self, node):
        node.set_string("attribute", self.attribute)


'''
AiUserDataRGB

Reads a named RGB color attribute from geometry at shade time.
'''


class AiUserDataRGB(bpy.types.Node, core.ArnoldNode):
    bl_label = "User Data RGB"
    ai_name = "user_data_rgb"

    attribute: StringProperty(name="Attribute", description="Name of the RGB attribute to read")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Default", identifier="default")
        self.outputs.new('AiNodeSocketRGB', "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text="")

    def sub_export(self, node):
        node.set_string("attribute", self.attribute)


'''
AiUserDataRGBA

Reads a named RGBA color attribute from geometry at shade time.
'''


class AiUserDataRGBA(bpy.types.Node, core.ArnoldNode):
    bl_label = "User Data RGBA"
    ai_name = "user_data_rgba"

    attribute: StringProperty(name="Attribute", description="Name of the RGBA attribute to read")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Default", identifier="default")
        self.outputs.new('AiNodeSocketRGBA', "RGBA")

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text="")

    def sub_export(self, node):
        node.set_string("attribute", self.attribute)


'''
AiUserDataString

Reads a named string attribute from geometry at shade time.
'''


class AiUserDataString(bpy.types.Node, core.ArnoldNode):
    bl_label = "User Data String"
    ai_name = "user_data_string"

    attribute: StringProperty(name="Attribute", description="Name of the string attribute to read")

    def init(self, context):
        self.outputs.new('AiNodeSocketFloatUnbounded', "String")

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text="")

    def sub_export(self, node):
        node.set_string("attribute", self.attribute)


classes = (
    AiFloat,
    AiVector,
    AiUserDataFloat,
    AiUserDataInt,
    AiUserDataRGB,
    AiUserDataRGBA,
    AiUserDataString,
)


def register():
    register_utils.register_classes(classes)


def unregister():
    register_utils.unregister_classes(classes)
