import bpy
import mathutils

from .. import utils

'''
Evaluates camera data for a single frame.
'''

@dataclass(init=False)
class CameraData:
    # Basic settings
    angle: float = 0.610865 # 35deg
    sensor_fit: str = 'AUTO'
    clip_start: float = 0.01
    clip_end: float = 1000
    ortho_scale: float = 1
    
    # DOF settings
    focus_distance: float = 0

    # Arnold settings
    camera_type: str = 'persp_camera'
    exposure: float = 0
    enable_dof: bool = False
    aperture_size: float = 0
    aperture_blades: int = 0
    aperture_rotation: float = 0
    aperture_blade_curvature: float = 0
    aperture_aspect_ratio: float = 1
    flat_field_focus: bool = False

    # IPR settings
    zoom: float = 0
    offset: tuple = (0, 0)
    is_render_view: bool = False

    @staticmethod
    def init_from_viewport():
        pass

    @staticmethod
    def init_from_object(ob: bpy.types.Object, scene: bpy.types.Scene):
        data = CameraData()

        data.angle = ob.data.angle
        data.sensor_fit = ob.data.sensor_fit
        data.clip_start = ob.data.clip_start
        data.clip_end = ob.data.clip_end
        data.ortho_scale = ob.data.ortho_scale

        focus_object = ob.data.dof.focus_object
        if focus_object:
            focus_distance = mathutils.geometry.distance_point_to_plane(
                ob.matrix_world.to_translation(),
                focus_object.matrix_world.to_translation(),
                ob.matrix_world.col[2][:3]
            )
        else:
            focus_distance = ob.data.dof.focus_distance
        
        aiparams = ob.data.arnold

        data.camera_type = aiparams.camera_type
        data.exposure = aiparams.exposure
        data.enable_dof = aiparams.enable_dof
        data.aperture_size = aiparams.aperture_size
        data.aperture_blades = aiparams.aperture_blades
        data.aperture_rotation = aiparams.aperture_rotation
        data.aperture_blade_curvature = aiparams.aperture_blade_curvature
        data.aperture_aspect_ratio = aiparams.aperture_aspect_ratio
        data.flat_field_focus = aiparams.flat_field_focus

    @staticmethod
    def to_arnold():
        node = arnold.AiNode(ob.data.arnold.camera_type)

        arnold.AiNodeSetStr(node, 'name', ob.name)
        # set uuid

        # Export 

        steps = utils.get_motion_blur_params(scene)