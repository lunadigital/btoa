import bpy
from bpy.props import *
from .. import core
from ...utils import register_utils

'''
AiBump2d

Provides bump mapping cored on a 2d texture map.
'''
class AiBump2d(bpy.types.Node, core.ArnoldNode):
    bl_label = "Bump 2D"
    ai_name = "bump2d"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Bump Map", identifier="bump_map").hide_value = True
        self.inputs.new('AiNodeSocketFloatUnbounded', name="Bump Height", identifier="bump_height").default_value = 1
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector")
        self.outputs.new('AiNodeSocketFloatUnbounded', name="X")
        self.outputs.new('AiNodeSocketFloatUnbounded', name="Y")

'''
AiBump3d

Provides bump mapping cored on a 3d input.
'''
class AiBump3d(bpy.types.Node, core.ArnoldNode):
    bl_label = "Bump 3D"
    bl_width_default = 160
    ai_name = "bump3d"

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatUnbounded', name="Bump Map", identifier="bump_map")
        self.inputs.new('AiNodeSocketFloatPositive', name="Bump Height", identifier="bump_height").default_value = 0.01
        self.inputs.new('AiNodeSocketFloatPositiveSmall', name="Epsilon", identifier="epsilon").default_value = 0.001
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector")
        self.outputs.new('AiNodeSocketFloatUnbounded', name="X")
        self.outputs.new('AiNodeSocketFloatUnbounded', name="Y")
        self.outputs.new('AiNodeSocketFloatUnbounded', name="Z")

'''
AiCoordSpace

A dummy node for passing coordinate space data to another shader.
'''
class AiCoordSpace(bpy.types.Node, core.ArnoldNode):
    bl_label = "Coordinate Space"

    def init(self, context):
        self.outputs.new("AiNodeSocketCoord", "Object")
        self.outputs.new("AiNodeSocketCoord", "World").default_value = "world"
        self.outputs.new("AiNodeSocketCoord", "Pref").default_value = "pref"
        self.outputs.new("AiNodeSocketCoord", "UV").default_value = "uv"

'''
AiFacingRatio

This shader returns the absolute value of the dot product between
the shading normal and the incoming ray direction. It is also named
incidence in other renderers. 
'''
class AiFacingRatio(bpy.types.Node, core.ArnoldNode):
    bl_label = "Facing Ratio"
    ai_name = "facing_ratio"

    linear: BoolProperty(name="Linear")
    invert: BoolProperty(name="Invert")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Bias", identifier="bias").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Gain", identifier="gain").default_value = 0.5

        self.outputs.new('AiNodeSocketFloatUnbounded', name="Float", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "linear")
        layout.prop(self, "invert")

    def sub_export(self, node):
        node.set_bool("linear", self.linear)
        node.set_bool("invert", self.invert)

'''
AiUVProjection

Turns any 2D texture into a 3D texture that you can place on the
surface using one of the available projection types. Use to adjust
the texture placement on the surface.
'''
class AiUVProjection(bpy.types.Node, core.ArnoldNode):
    bl_label = "UV Projection"
    ai_name = "uv_projection"

    projection_type: EnumProperty(
        name="Projection Type",
        items=[
            ('planar', "Planar", "Planar"),
            ('spherical', "Spherical", "Spherical"),
            ('cylindrical', "Cylindrical", "Cylindrical"),
            ('ball', "Ball", "Ball"),
            ('cubic', "Cubic", "Cubic"),
            ('shrinkwrap', "Shrinkwrap", "Shrinkwrap")
        ],
        default='planar'
    )

    def init(self, context):
        self.inputs.new("AiNodeSocketRGBA", "Color", identifier="projection_color")
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")

        self.outputs.new("AiNodeSocketRGBA", "RGBA")

    def draw_buttons(self, context, layout):
        layout.prop(self, "projection_type")

    def sub_export(self, node):
        node.set_string("projection_type", self.projection_type)

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
        return self.value, self.outputs[0].default_type

classes = (
    AiBump2d,
    AiBump3d,
    AiCoordSpace,
    AiFacingRatio,
    AiUVProjection,
    AiFloat
)

def register():
    register_utils.register_classes(classes)

def unregister():
    register_utils.unregister_classes(classes)