import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import BoolProperty, PointerProperty

class ArnoldShape(PropertyGroup):
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

def register():
    bpy.utils.register_class(ArnoldShape)
    Object.arnold = PointerProperty(type=ArnoldShape)

def unregister():
    bpy.utils.unregister_class(ArnoldShape)
    del Object.arnold