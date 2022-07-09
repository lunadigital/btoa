import bpy
from bpy.props import *
from .. import base
from ... import utils

'''
AiCoordSpace

A dummy node for passing coordinate space data to another shader.
'''
class AiCoordSpace(bpy.types.Node, base.ArnoldNode):
    bl_label = "Coordinate Space"

    def init(self, context):
        self.outputs.new("AiNodeSocketCoord", "Object")
        self.outputs.new("AiNodeSocketCoord", "World").default_value = "world"
        self.outputs.new("AiNodeSocketCoord", "Pref").default_value = "pref"
        self.outputs.new("AiNodeSocketCoord", "UV").default_value = "uv"

'''
AiFacingRatio
https://docs.arnoldrenderer.com/display/A5NodeRef/facing_ratio

This shader returns the absolute value of the dot product between
the shading normal and the incoming ray direction. It is also named
incidence in other renderers. 
'''
class AiFacingRatio(bpy.types.Node, base.ArnoldNode):
    bl_label = "Facing Ratio"
    ai_name = "facing_ratio"

    linear: BoolProperty(name="Linear")
    invert: BoolProperty(name="Invert")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Bias", identifier="bias").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Gain", identifier="gain").default_value = 0.5

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "linear")
        layout.prop(self, "invert")

    def sub_export(self, node, socket_index=0):
        node.set_bool("linear", self.linear)
        node.set_bool("invert", self.invert)

'''
AiUVProjection
https://docs.arnoldrenderer.com/display/A5NodeRef/uv_projection

Turns any 2D texture into a 3D texture that you can place on the
surface using one of the available projection types. Use to adjust
the texture placement on the surface.
'''
class AiUVProjection(bpy.types.Node, base.ArnoldNode):
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

    def sub_export(self, node, socket_index=0):
        node.set_string("projection_type", self.projection_type)

classes = (
    AiCoordSpace,
    AiFacingRatio,
    AiUVProjection,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)