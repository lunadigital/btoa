import bpy
from bpy.types import Scene, PropertyGroup, Camera
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty, EnumProperty

class ArnoldCamera(PropertyGroup):
    # Basic lens settings
    def toggle_blender_camera_type(self, context):
        if self.camera_type == 'ortho_camera':
            bpy.context.object.data.type = 'ORTHO'
        elif self.camera_type == 'persp_camera':
            bpy.context.object.data.type = 'PERSP'
        elif self.camera_type == 'spherical_camera':
            bpy.context.object.data.type = 'PANO'

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
        default='persp_camera',
        update=toggle_blender_camera_type
    )

    exposure: FloatProperty(name="Exposure")

    # DOF
    enable_dof: BoolProperty(name="Enable DOF")
    aperture_size: FloatProperty(name="Size", min=0, soft_max=0.1, unit='LENGTH')
    aperture_blades: IntProperty(name="Blades", min=0)
    aperture_rotation: FloatProperty(name="Rotation", unit='ROTATION')
    aperture_blade_curvature: FloatProperty(name="Curvature", min=-1, max=1)
    aperture_aspect_ratio: FloatProperty(name="Aspect Ratio", min=0, default=1)
    flat_field_focus: BoolProperty(name="Flat Field Focus")

def register():
    bpy.utils.register_class(ArnoldCamera)
    Camera.arnold = PointerProperty(type=ArnoldCamera)

def unregister():
    bpy.utils.unregister_class(ArnoldCamera)
    del Camera.arnold