import mathutils

from .exporter import Exporter

from ..matrix import ArnoldMatrix
from .. import utils as export_utils

class WorldExporter(Exporter):
    def export(self, world):
        super().export(world)

        # Because of how we're manipulating the rotation of the skydome, we have to create a new
        # one every time and replace the node. Otherwise, things get weird.
        surface, volume, displacement = self.datablock.arnold.node_tree.export()
        self.node = surface[0]
        self.node.set_uuid(world.uuid)

        # Flip image textures in the U direction
        image = self.node.get_link("color")

        if image.is_valid() and image.type_is("image"):
            sflip = image.get_bool("sflip")
            image.set_bool("sflip", not sflip)

        # Rotate skydome with rotation controller object
        if self.datablock.arnold.rotation_controller:
            rot = self.datablock.arnold.rotation_controller.rotation_euler

            rx = mathutils.Matrix.Rotation(rot.x, 4, 'X')
            ry = mathutils.Matrix.Rotation(rot.y, 4, 'Y')
            rz = mathutils.Matrix.Rotation(rot.z, 4, 'Z')
            
            rot_matrix = rx @ ry @ rz
            rot_matrix = export_utils.flatten_matrix(rot_matrix)

            rotation = ArnoldMatrix()
            rotation.convert_from_buffer(rot_matrix)

            matrix = self.node.get_matrix("matrix")
            matrix.multiply(rotation)

            self.node.set_matrix("matrix", matrix)

        data = self.datablock.arnold.data

        self.node.set_int("samples", data.samples)
        self.node.set_bool("normalize", data.normalize)

        self.node.set_bool("cast_shadows", data.cast_shadows)
        self.node.set_bool("cast_volumetric_shadows", data.cast_volumetric_shadows)
        self.node.set_rgb("shadow_color", *data.shadow_color)
        self.node.set_float("shadow_density", data.shadow_density)

        self.node.set_float("camera", data.camera)
        self.node.set_float("diffuse", data.diffuse)
        self.node.set_float("specular", data.specular)
        self.node.set_float("transmission", data.transmission)
        self.node.set_float("sss", data.sss)
        self.node.set_float("indirect", data.indirect)
        self.node.set_float("volume", data.volume)
        self.node.set_int("max_bounces", data.max_bounces)

        return self.node