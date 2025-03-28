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
    bl_width_default = 160
    ai_name = "bump2d"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Bump Map", identifier="bump_map").hide_value = True
        self.inputs.new('AiNodeSocketFloatUnbounded', name="Bump Height", identifier="bump_height").default_value = 1
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector")

'''
AiBump3d

Provides bump mapping cored on a 3d input.
'''
class AiBump3d(bpy.types.Node, core.ArnoldNode):
    bl_label = "Bump 3D"
    bl_width_default = 160
    ai_name = "bump3d"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Bump Map", identifier="bump_map").hide_value = True
        self.inputs.new('AiNodeSocketFloatPositive', name="Bump Height", identifier="bump_height").default_value = 0.01
        self.inputs.new('AiNodeSocketFloatPositiveSmall', name="Epsilon", identifier="epsilon").default_value = 0.001
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector")

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

        self.outputs.new('AiNodeSocketFloatUnbounded', name="Float")

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
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float", identifier="out_variable")

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable", text="")

    def sub_export(self, node):
        node.set_string("variable", self.variable)

class AiStateInt(bpy.types.Node, core.ArnoldNode):
    bl_label = "State Int"
    ai_name = "state_int"

    variable: EnumProperty(
        name="State Type",
        items=[
            ('x', 'Raster X', "Raster-space x pixel coordinate the camera ray started from."),
            ('y', 'Raster Y', "Raster-space y pixel coordinate the camera ray started from."),
            ('si', 'Subpixel Sample Index', "AA sample index, in range [0, AA_samples]."),
            ('Rt', 'Ray Type', "Ray type of the incoming ray."),
            ('transp_index', 'Transparency Index', "The number of transparent surfaces shaded before the current shading point."),
            ('tid', 'Thread ID', "Unique thread ID."),
            ('bounces', 'Bounces', "The number of bounces up to the current shading point."),
            ('bounces_diffuse', 'Diffuse Bounces', "The number of diffuse bounces."),
            ('bounces_specular', 'Specular Bounces', "The number of specular bounces."),
            ('bounces_reflect', 'Reflection Bounces', "The number of reflection bounces."),
            ('bounces_transmit', 'Transmission Bounces', "The number of transmission bounces."),
            ('bounces_volume', 'Volume Bounces', "The number of volume bounces."),
            ('fhemi', 'Force Hemispherical Lighting', "Force hemispherical lighting."),
            ('fi', 'Primitive ID', "Primitive ID (triangle, curve segment, etc)."),
            ('nlights', 'Number of Active Lights', "The number of active lights affecting shading point."),
            ('inclusive_traceset', 'Inclusive Traceset', "If a traceset is used, is it inclusive or exclusive?"),
            ('skip_shadow', 'Skip Shadow Rays', "If true, don't trace shadow rays for lighting."),
            ('sc', 'Shading Context', "Type of shading context (surface, displacement, volume, background, importance)."),
        ]
    )

    def init(self, context):
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float", identifier="out_variable")

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable", text="")

    def sub_export(self, node):
        node.set_string("variable", self.variable)

class AiStateVector(bpy.types.Node, core.ArnoldNode):
    bl_label = "State Vector"
    ai_name = "state_vector"

    variable: EnumProperty(
        name="State Type",
        items=[
            ('Ro', 'Ray Origin', "For surfaces, ray origin (camera or previous bounce position). For volumes, the start of the volume segment being shaded."),
            ('Rd', 'Ray Direction', "Ray direction from ray origin to shading point. For volumes, the direction of the volume segment being shaded."),
            ('Po', 'Shading Point in Object-Space', "Shading position in object-space."),
            ('P', 'Shading Point in World-Space', "Shading position in world-space."),
            ('dPdx', 'Surface Derivative wrt Screen X', "Surface derivative with respect to X pixel coordinate."),
            ('dPdy', 'Surface Derivative wrt Screen Y', "Surface derivative with respect to Y pixel coordinate."),
            ('N', 'Shading Normal', "Shading normal, including smooth normals and bump mapping."),
            ('Nf', 'Face-Forward Shading Normal', "Face-forward shading normal."),
            ('Ng', 'Geometric Normal', "Normal of the actual geometry, without smoothing or bump."),
            ('Ngf', 'Face-Forward Geometric Normal', "Face-forward geometric normal."),
            ('Ns', 'Smoothed Normal without Bump', "Smoothed normal (same as N but without bump)."),
            ('dPdu', 'Surface Derivative wrt U', "Surface derivative with respect to U coordinate (not normalized). May be used as tangent for anisotropic shading or vector displacement."),
            ('dPdv', 'Surface Derivative wrt V', "Surface derivative with respect to V coordinate (not normalized). May be used as tangent for anisotropic shading or vector displacement."),
            ('dDdx', 'Ray Direction Derivative wrt Screen X', "Ray direction derivative wrt X pixel coordinate."),
            ('dDdy', 'Ray Direction Derivative wrt Screen Y', "Ray direction derivative wrt Y pixel coordinate."),
            ('dNdx', 'Surface Normal Derivative wrt Screen X', "The derivative of the surface normal with respect to X pixel coordinate."),
            ('dNdy', 'Surface Normal Derivative wrt Screen Y', "The derivative of the surface normal with respect to Y pixel coordinate."),
        ]
    )

    def init(self, context):
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float", identifier="out_variable")

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable", text="")

    def sub_export(self, node):
        node.set_string("variable", self.variable)

classes = (
    AiBump2d,
    AiBump3d,
    AiCoordSpace,
    AiFacingRatio,
    AiUVProjection,
    AiStateFloat,
    AiStateInt,
    AiStateVector
)

def register():
    register_utils.register_classes(classes)

def unregister():
    register_utils.unregister_classes(classes)