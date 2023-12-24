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
    
'''
Shading State Shaders

The state shaders allow access to ray and geometric properties such as the surface normal,
the UV surface parameters, ray depth, etc. The shaders are separated into float, int, and
vector data types.
'''
class AiStateFloat(bpy.types.Node, core.ArnoldNode):
    bl_label = "State Float"
    ai_name = "state_float"

    variable: EnumProperty(
        name="State Type",
        items=[
            ('sx', 'Screen X', "X image-space coordinate, in range [-1,1)."),
            ('sy', 'Screen Y', "Y image-space coordinate, in range [-1, 1]."),
            ('time', 'Shutter Time', "For motion blur, the absolute time at which the current sample is being shaded. A value between shutter-open and shutter-close times."),
            ('R1', 'Ray Length', "For surface shaders, the ray length from the camera or previous bounce to the shading point. For volume shaders, the length of the volume segment being shaded."),
            ('bu', 'Barycentric U', "For triangles, barycentric coordinate within the triangle. For curves, parametric coordinate along the curve length and width respectively."),
            ('bv', 'Barycentric V', "For triangles, barycentric coordinate within the triangle. For curves, parametric coordinate along the curve length and width respectively."),
            ('u', 'Surface U', "U coordinates typically used as texture coordinates. Same as bu in case no uvlist or uvs parameter was provided."),
            ('v', 'Surface V', "V coordinates typically used as texture coordinates. Same as bv in case no uvlist or uvs parameter was provided."),
            ('area', 'Shaded Area', "The differential area covered by the current shading point, typically used for texture filtering. For surface shaders this the area spanned by ray differentials, for displacement shaders it is the average area of triangles surrounding the vertex."),
            ('dudx', 'U Derivative wrt Screen X', "UV derivative with respect to the XY pixel coordinates. This contains the rate of change of the UV from the current pixel to the neighboring pixels to the right and top, typically used for texture filtering."),
            ('dudy', 'U Derivative wrt Screen Y', "UV derivative with respect to the XY pixel coordinates. This contains the rate of change of the UV from the current pixel to the neighboring pixels to the right and top, typically used for texture filtering."),
            ('dvdx', 'V Derivative wrt Screen X', "UV derivative with respect to the XY pixel coordinates. This contains the rate of change of the UV from the current pixel to the neighboring pixels to the right and top, typically used for texture filtering."),
            ('dvdy', 'V Derivative wrt Screen Y', "UV derivative with respect to the XY pixel coordinates. This contains the rate of change of the UV from the current pixel to the neighboring pixels to the right and top, typically used for texture filtering."),
            ('shutter_start', 'Shutter Start', "Absolute start time of the motion blur range."),
            ('shutter_end', 'Shutter End', "Absolute end time of the motion blur range.")
        ]
    )

    def init(self, context):
        self.outputs.new('AiNodeSocketStateFloat', "SX", identifier="sx")
        self.outputs.new('AiNodeSocketStateFloat', "SY", identifier="sy")
        self.outputs.new('AiNodeSocketStateFloat', "Time", identifier="time")
        self.outputs.new('AiNodeSocketStateFloat', "R1", identifier="R1")
        self.outputs.new('AiNodeSocketStateFloat', "BU", identifier="bu")
        self.outputs.new('AiNodeSocketStateFloat', "BV", identifier="bv")
        self.outputs.new('AiNodeSocketStateFloat', "U", identifier="u")
        self.outputs.new('AiNodeSocketStateFloat', "V", identifier="v")
        self.outputs.new('AiNodeSocketStateFloat', "Area", identifier="area")
        self.outputs.new('AiNodeSocketStateFloat', "dudx", identifier="dudx")
        self.outputs.new('AiNodeSocketStateFloat', "dudy", identifier="dudy")
        self.outputs.new('AiNodeSocketStateFloat', "dvdx", identifier="dvdx")
        self.outputs.new('AiNodeSocketStateFloat', "dvdy", identifier="dvdy")
        self.outputs.new('AiNodeSocketStateFloat', "shutter_start", identifier="shutter_start")
        self.outputs.new('AiNodeSocketStateFloat', "shutter_end", identifier="shutter_end")

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable")

    def sub_export(self, node):
        value = node.get_enum_value("variable", self.variable)
        node.set_float("out_variable", float(value))

classes = (
    AiBump2d,
    AiBump3d,
    AiCoordSpace,
    AiFacingRatio,
    AiUVProjection,
    AiFloat,
    AiStateFloat
)

def register():
    register_utils.register_classes(classes)

def unregister():
    register_utils.unregister_classes(classes)