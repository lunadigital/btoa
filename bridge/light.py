import bpy
import arnold
import math
import mathutils

from .constants import BTOA_LIGHT_CONVERSIONS, BTOA_LIGHT_SHAPE_CONVERSIONS
from .exportable import ArnoldNodeExportable
from .node import ArnoldNode
from . import utils as bridge_utils

class ArnoldLight(ArnoldNodeExportable):
    def __init__(self, node=None, frame_set=None):
        super().__init__(node, frame_set)

    def from_datablock(self, depsgraph, datablock):
        self.depsgraph = depsgraph

        # Evaluate object data
        self.evaluate_datablock(datablock)
        if not self.datablock:
            return None
        
        # Determine light type and set up AiNode data
        data = self.datablock.data
        ntype = BTOA_LIGHT_SHAPE_CONVERSIONS[data.shape] if data.type == 'AREA' else BTOA_LIGHT_CONVERSIONS[data.type]

        if ntype != self.get_string("btoa_light_type"):
            self.destroy()
            
        if not self.is_valid:
            self.data = arnold.AiNode(None, ntype)
            self.set_string("name", self.datablock.name)
            self.set_uuid(self.datablock.uuid)

            self.declare("btoa_light_type", "constant STRING")
            self.set_string("btoa_light_type", ntype)
        
        # Set transform matrix for everything but cylinder lights
        if not hasattr(data, "shape") or data.shape != 'RECTANGLE':
            self.set_matrix(
                "matrix",
                bridge_utils.flatten_matrix(self.datablock.matrix_world)
            )

        # Set common attributes
        self.set_rgb("color", *data.color)
        self.set_float("intensity", data.arnold.intensity)
        self.set_float("exposure", data.arnold.exposure)
        self.set_int("samples", data.arnold.samples)
        self.set_bool("normalize", data.arnold.normalize)

        self.set_bool("cast_shadows", data.arnold.cast_shadows)
        self.set_bool("cast_volumetric_shadows", data.arnold.cast_volumetric_shadows)
        self.set_rgb("shadow_color", *data.arnold.shadow_color)
        self.set_float("shadow_density", data.arnold.shadow_density)

        self.set_float("camera", data.arnold.camera)
        self.set_float("diffuse", data.arnold.diffuse)
        self.set_float("specular", data.arnold.specular)
        self.set_float("transmission", data.arnold.transmission)
        self.set_float("sss", data.arnold.sss)
        self.set_float("indirect", data.arnold.indirect)
        self.set_float("volume", data.arnold.volume)
        self.set_int("max_bounces", data.arnold.max_bounces)

        # Set light-specific attributes
        if data.type in ('POINT', 'SPOT'):
            self.set_float("radius", data.shadow_soft_size)

            if data.type == 'SPOT':
                self.set_float("cone_angle", math.degrees(data.spot_size))
                self.set_float("penumbra_angle", math.degrees(data.arnold.penumbra_angle))
                self.set_float("roundness", data.arnold.spot_roundness)
                self.set_float("aspect_ratio", data.arnold.aspect_ratio)
                self.set_float("lens_radius", data.arnold.lens_radius)

        elif data.type == 'SUN':
            self.set_float("angle", data.arnold.angle)

        elif data.type == 'AREA':
            self.set_float("roundness", data.arnold.area_roundness)
            self.set_float("spread", data.arnold.spread)
            self.set_int("resolution", data.arnold.resolution)
            self.set_float("soft_edge", data.arnold.soft_edge)

            if data.shape == 'SQUARE':
                tmatrix = self.datablock.matrix_world @ \
                          mathutils.Matrix.Scale(0.5, 4) @ \
                          mathutils.Matrix.Scale(data.size, 4)

                self.set_matrix(
                    "matrix",
                    bridge_utils.flatten_matrix(tmatrix)
                )

                self.set_bool("portal", data.arnold.portal)
                
            elif data.shape == 'DISK':
                s = self.datablock.scale.x if self.datablock.scale.x > 0 else self.datablock.scale.y
                self.set_float("radius", 0.5 * data.size * s)

            elif data.shape == 'RECTANGLE':
                d = 0.5 * data.size_y * self.datablock.scale.y
                top = bridge_utils.get_position_along_local_vector(self.datablock, d, 'Y')
                bottom = bridge_utils.get_position_along_local_vector(self.datablock, -d, 'Y')

                self.set_vector("top", *top)
                self.set_vector("bottom", *bottom)

                s = self.datablock.scale.x if self.datablock.scale.x > self.datablock.scale.z else self.datablock.scale.z
                self.set_float("radius", 0.5 * data.size * s)

        return self