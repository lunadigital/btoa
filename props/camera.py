import bpy
from bpy.types import Scene, PropertyGroup, Camera
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty, EnumProperty

class ArnoldCamera(PropertyGroup):
    # Basic lens settings
    camera_type: EnumProperty(
        name="Type",
        items=[
            ('cyl_camera', "Cylindrical ", "Cylindrical "),
            ('fisheye_camera', "Fisheye", "Fisheye"),
            ('ortho_camera', "Orthographic", "Orthographic"),
            ('persp_camera', "Perspective", "Perspective"),
            ('spherical_camera', "Spherical", "Spherical"),
            ('vr_camera', "VR", "VR"),
            ('uv_camera', "UV", "UV"),
        ],
        default='persp_camera'
    )

    exposure: FloatProperty(name="Exposure")

    # DOF
    enable_dof: BoolProperty(name="Enable DOF")
    focus_distance: FloatProperty(name="Focus Distance")
    aperture_size: FloatProperty(name="Size", min=0, soft_max=0.1, unit='LENGTH')
    aperture_blades: IntProperty(name="Blades", min=0)
    aperture_rotation: FloatProperty(name="Rotation")
    aperture_blade_curvature: FloatProperty(name="Curvature", min=-1, max=1)
    aperture_aspect_ratio: FloatProperty(name="Aspect Ratio", min=0, default=1)
    flat_field_focus: BoolProperty(name="Flat Field Focus")

    # Shutter
    shutter_start: FloatProperty(name="Shutter: Start")
    shutter_end: FloatProperty(name="Shutter: Stop")

    shutter_type: EnumProperty(
        name="Shutter Type",
        items=[
            ('box', "Box", "Box"),
            ('triangle', "Triangle", "Triangle"),
            #('curve', "Curve", "Curve")
        ],
        default='box'
    )

    rolling_shutter: EnumProperty(
        name="Rolling Shutter",
        items=[
            ('off', "Off", "Off"),
            ('top', "Top", "Top"),
            ('bottom', "Bottom", "Bottom"),
            ('left', "Left", "Left"),
            ('right', "Right", "Right")
        ],
        default='off'
    )
    rolling_shutter_duration: FloatProperty(name="Rolling Shutter: Duration")

def register():
    bpy.utils.register_class(ArnoldCamera)
    Camera.arnold = PointerProperty(type=ArnoldCamera)

def unregister():
    bpy.utils.unregister_class(ArnoldCamera)
    del Camera.arnold