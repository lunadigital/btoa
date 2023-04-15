import bpy
import os

BTOA_PACKAGE_NAME = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

BTOA_POLYMESH_COMPATIBLE = (
    bpy.types.Curve,
    bpy.types.Mesh,
    bpy.types.TextCurve
)