import bpy
import math
import mathutils

from .exportable import ArnoldNodeExportable
from . import utils as bridge_utils

class ArnoldCamera(ArnoldNodeExportable):
    def __init__(self, node=None):
        super().__init__(node)

    def from_datablock(self, depsgraph, datablock):
        self.depsgraph = depsgraph

        # Evaluate datablock
        self.evaluate_datablock(datablock)
        if not self.datablock:
            return None
        
        # Create Arnold data if needed
        sdata = depsgraph.scene.arnold
        cdata = self.datablock.data
        
        if not self.is_valid:
            self.initialize(cdata.arnold.camera_type)

        # Set general attributes
        self.set_string("name", self.datablock.name)
        self.set_float("near_clip", cdata.clip_start)
        self.set_float("far_clip", cdata.clip_end)
        self.set_float("exposure", cdata.arnold.exposure)

        # Set transformation matrix
        if sdata.enable_motion_blur and sdata.camera_motion_blur:
            matrix = self.get_blur_matrices()
            self.set_array("matrix", matrix)
        else:
            matrix = bridge_utils.flatten_matrix(self.datablock.matrix_world)
            self.set_matrix("matrix", matrix)
        
        # Set zoom, offset, and FOV
        zoom = 1
        xo, yo = 0, 0

        if cdata.arnold.camera_type == 'ortho_camera':
            zoom = cdata.ortho_scale / 2.0
            
            if hasattr(cdata, "is_render_view") and cdata.is_render_view:
                zoom = zoom * cdata.zoom
                xo, yo = cdata.offset[0] * cdata.ortho_scale, cdata.offset[1] * cdata.ortho_scale

        elif cdata.arnold.camera_type == 'persp_camera':
            fov = bridge_utils.calc_horizontal_fov(self.datablock)
            self.set_float("fov", math.degrees(fov))

            if hasattr(cdata, "is_render_view") and cdata.is_render_view:
                zoom = cdata.zoom / 2.0
                xo, yo = cdata.offset

        self.set_vector2("screen_window_min", -zoom + xo, -zoom + yo)
        self.set_vector2("screen_window_max", zoom + xo, zoom + yo)

        # Set DOF attributes
        if cdata.dof.focus_object:
            distance = mathutils.geometry.distance_point_to_plane(
                self.datablock.matrix_world.to_translation(),
                cdata.dof.focus_object.matrix_world.to_translation(),
                self.datablock.matrix_world.col[2][:3]
            )
        else:
            distance = cdata.dof.focus_distance

        aperture_size = cdata.arnold.aperture_size if cdata.arnold.enable_dof else 0

        self.set_float("focus_distance", distance)
        self.set_float("aperture_size", aperture_size)
        self.set_int("aperture_blades", cdata.arnold.aperture_blades)
        self.set_float("aperture_rotation", cdata.arnold.aperture_rotation)
        self.set_float("aperture_blade_curvature", cdata.arnold.aperture_blade_curvature)
        self.set_float("aperture_aspect_ratio", cdata.arnold.aperture_aspect_ratio)

        # Set motion blur attributes
        if sdata.enable_motion_blur:
            self.set_float("shutter_start", sdata.shutter_start)
            self.set_float("shutter_end", sdata.shutter_end)
            #self.set_string("shutter_type", scene_data.shutter_type)
            #self.set_string("rolling_shutter", scene_data.rolling_shutter)
            #self.set_float("rolling_shutter_duration", scene_data.rolling_shutter_duration)

        return self