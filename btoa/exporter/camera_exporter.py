import math
import mathutils

from .object_exporter import ObjectExporter

from ..node import ArnoldNode
from .. import utils as export_utils

class CameraExporter(ObjectExporter):
    def export(self, ob):
        super().export(ob)

        # If self.node already exists, it will sync all new
        # data with the existing BtoA node
        if not self.node.is_valid():
            name = export_utils.get_unique_name(ob)
            self.node = ArnoldNode("persp_camera")

        self.node.set_string("name", self.datablock.name)

        sdata = self.cache.scene
        cdata = self.datablock.data

        if sdata["enable_motion_blur"] and sdata["camera_motion_blur"]:
            matrix = self.get_blur_matrices()
            self.node.set_array("matrix", matrix)
        else:
            matrix = export_utils.flatten_matrix(self.datablock.matrix_world)
            self.node.set_matrix("matrix", matrix)

        fov = export_utils.calc_horizontal_fov(self.datablock)
        self.node.set_float("fov", math.degrees(fov))

        self.node.set_float("exposure", cdata.arnold.exposure)

        if cdata.dof.focus_object:
            distance = mathutils.geometry.distance_point_to_plane(
                self.datablock.matrix_world.to_translation(),
                cdata.dof.focus_object.matrix_world.to_translation(),
                self.datablock.matrix_world.col[2][:3]
            )
        else:
            distance = cdata.dof.focus_distance

        aperture_size = cdata.arnold.aperture_size if cdata.arnold.enable_dof else 0

        self.node.set_float("focus_distance", distance)
        self.node.set_float("aperture_size", aperture_size)
        self.node.set_int("aperture_blades", cdata.arnold.aperture_blades)
        self.node.set_float("aperture_rotation", cdata.arnold.aperture_rotation)
        self.node.set_float("aperture_blade_curvature", cdata.arnold.aperture_blade_curvature)
        self.node.set_float("aperture_aspect_ratio", cdata.arnold.aperture_aspect_ratio)

        self.node.set_float("near_clip", cdata.clip_start)
        self.node.set_float("far_clip", cdata.clip_end)

        if sdata["enable_motion_blur"]:
            self.node.set_float("shutter_start", sdata["shutter_start"])
            self.node.set_float("shutter_end", sdata["shutter_end"])
            #self.node.set_string("shutter_type", scene_data.shutter_type)
            #self.node.set_string("rolling_shutter", scene_data.rolling_shutter)
            #self.node.set_float("rolling_shutter_duration", scene_data.rolling_shutter_duration)
        
        return self.node