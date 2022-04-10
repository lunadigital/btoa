import bpy
import mathutils

from .object_exporter import ObjectExporter
from .instance_exporter import InstanceExporter

from ..node import ArnoldNode
from ..constants import BTOA_LIGHT_CONVERSIONS, BTOA_LIGHT_SHAPE_CONVERSIONS
from .. import utils as export_utils

class LightExporter(ObjectExporter):
    def export(self, instance):
        super().export(instance)
        
        if isinstance(instance, bpy.types.DepsgraphObjectInstance):
            self.datablock_eval = export_utils.get_object_data_from_instance(instance)
        else:
            self.datablock_eval = instance

        data = self.datablock_eval.data

        # If self.node already exists, it will sync all new
        # data with the existing BtoA node
        if not self.node.is_valid():
            name = export_utils.get_unique_name(self.datablock_eval)
            existing_node = self.session.get_node_by_name(name)

            if existing_node.is_valid():
                instancer = InstanceExporter(self.session)
                instancer.set_transform(self.get_transform_matrix())
                return instancer.export(existing_node)
            else:
                ntype = BTOA_LIGHT_SHAPE_CONVERSIONS[data.shape] if data.type == 'AREA' else BTOA_LIGHT_CONVERSIONS[data.type]
                self.node = ArnoldNode(ntype)
                self.node.set_string("name", name)

        # Set matrix for everything except cylinder lights
        if not hasattr(data, "shape") or data.shape != 'RECTANGLE':
            self.node.set_matrix(
                "matrix",
                export_utils.flatten_matrix(self.datablock.matrix_world)
            )

        self.node.set_rgb("color", *data.color)
        self.node.set_float("intensity", data.arnold.intensity)
        self.node.set_float("exposure", data.arnold.exposure)
        self.node.set_int("samples", data.arnold.samples)
        self.node.set_bool("normalize", data.arnold.normalize)

        self.node.set_bool("cast_shadows", data.arnold.cast_shadows)
        self.node.set_bool("cast_volumetric_shadows", data.arnold.cast_volumetric_shadows)
        self.node.set_rgb("shadow_color", *data.arnold.shadow_color)
        self.node.set_float("shadow_density", data.arnold.shadow_density)

        self.node.set_float("camera", data.arnold.camera)
        self.node.set_float("diffuse", data.arnold.diffuse)
        self.node.set_float("specular", data.arnold.specular)
        self.node.set_float("transmission", data.arnold.transmission)
        self.node.set_float("sss", data.arnold.sss)
        self.node.set_float("indirect", data.arnold.indirect)
        self.node.set_float("volume", data.arnold.volume)
        self.node.set_int("max_bounces", data.arnold.max_bounces)

        if data.type in ('POINT', 'SPOT'):
            self.node.set_float("radius", data.shadow_soft_size)

            if data.type == 'SPOT':
                self.node.set_float("cone_angle", math.degrees(data.spot_size))
                self.node.set_float("penumbra_angle", math.degrees(data.arnold.penumbra_angle))
                self.node.set_float("roundness", data.arnold.spot_roundness)
                self.node.set_float("aspect_ratio", data.arnold.aspect_ratio)
                self.node.set_float("lens_radius", data.arnold.lens_radius)

        elif data.type == 'SUN':
            self.node.set_float("angle", data.arnold.angle)

        elif data.type == 'AREA':
            self.node.set_float("roundness", data.arnold.area_roundness)
            self.node.set_float("spread", data.arnold.spread)
            self.node.set_int("resolution", data.arnold.resolution)
            self.node.set_float("soft_edge", data.arnold.soft_edge)

            if data.shape == 'SQUARE':
                tmatrix = self.datablock.matrix_world @ \
                          mathutils.Matrix.Scale(0.5, 4) @ \
                          mathutils.Matrix.Scale(data.size, 4)

                self.node.set_matrix(
                    "matrix",
                    export_utils.flatten_matrix(tmatrix)
                )
            elif data.shape == 'DISK':
                s = self.datablock.scale.x if self.datablock.scale.x > 0 else self.datablock.scale.y
                self.node.set_float("radius", 0.5 * data.size * s)
            elif data.shape == 'RECTANGLE':
                d = 0.5 * data.size_y * self.datablock.scale.y
                top = export_utils.get_position_along_local_vector(self.datablock, d, 'Y')
                bottom = export_utils.get_position_along_local_vector(self.datablock, -d, 'Y')

                self.node.set_vector("top", *top)
                self.node.set_vector("bottom", *bottom)

                s = self.datablock.scale.x if self.datablock.scale.x > self.datablock.scale.z else self.datablock.scale.z
                self.node.set_float("radius", 0.5 * data.size * s)

        return self.node