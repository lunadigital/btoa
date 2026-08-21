import bpy
from bpy.types import PropertyGroup, Curves
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty


class ArnoldCurves(PropertyGroup):
    camera: BoolProperty(
        name="Camera",
        description="",
        default=True
    )

    shadow: BoolProperty(
        name="Shadow",
        description="",
        default=True
    )

    diffuse_transmission: BoolProperty(
        name="Diffuse Transmission",
        description="",
        default=True
    )

    specular_transmission: BoolProperty(
        name="Specular Transmission",
        description="",
        default=True
    )

    volume: BoolProperty(
        name="Volume",
        description="",
        default=True
    )

    diffuse_reflection: BoolProperty(
        name="Diffuse Reflection",
        description="",
        default=True
    )

    specular_reflection: BoolProperty(
        name="Specular Reflection",
        description="",
        default=True
    )

    sss: BoolProperty(
        name="SSS",
        description="",
        default=True
    )

    mode: EnumProperty(
        name="Mode",
        description="Curve rendering mode",
        items=[
            ('ribbon', "Ribbon", "Render curves as ribbons"),
            ('thick', "Thick", "Render curves as thick tubes"),
            ('oriented', "Oriented", "Render curves with custom orientation")
        ],
        default='ribbon'
    )

    basis: EnumProperty(
        name="Basis",
        description="Curve basis type",
        items=[
            ('bezier', "Bezier", "Bezier curves"),
            ('b-spline', "B-Spline", "B-spline curves"),
            ('catmull-rom', "Catmull-Rom", "Catmull-Rom curves"),
            ('linear', "Linear", "Linear curves")
        ],
        default='catmull-rom'
    )

    min_pixel_width: FloatProperty(
        name="Min Pixel Width",
        description="Minimum width of curves in pixels",
        default=0.0,
        min=0.0,
        soft_max=10.0
    )

    export_uvs: BoolProperty(
        name="Export UVs",
        description="Export UV coordinates for curves",
        default=True
    )

    attach_to_surface: BoolProperty(
        name="Attach to Surface",
        description="Attach curves to parent mesh using barycentric coordinates so they follow displacement",
        default=True
    )

    subdivide_curves: IntProperty(
        name="Subdivide",
        description="Subdivide each curve span for export. Uses catmull-rom evaluation for smooth positions but linear interpolation for radius, preserving exact taper/width variation. Set to 1 to disable",
        default=3,
        min=1,
        max=8
    )


def register():
    bpy.utils.register_class(ArnoldCurves)
    Curves.arnold_curves = PointerProperty(type=ArnoldCurves)


def unregister():
    bpy.utils.unregister_class(ArnoldCurves)
    del Curves.arnold_curves
