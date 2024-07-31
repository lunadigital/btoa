import mathutils

from .matrix import ArnoldMatrix
from .node import ArnoldNode
from . import utils as bridge_utils

class ArnoldWorld(ArnoldNode):
    def from_datablock(self, datablock):
        surface, volume, displ = datablock.arnold.node_tree.export()
        self.data = surface.value.data
        self.set_uuid(datablock.uuid)

        # Flip image textures in the U direction
        image = self.get_link("color")

        if image.is_valid and image.type_is("image"):
            sflip = image.get_bool("sflip")
            image.set_bool("sflip", not sflip)

        # Rotate skydome with rotation controller object
        if datablock.arnold.rotation_controller:
            rot = datablock.arnold.rotation_controller.rotation_euler

            rx = mathutils.Matrix.Rotation(rot.x, 4, 'X')
            ry = mathutils.Matrix.Rotation(rot.y, 4, 'Y')
            rz = mathutils.Matrix.Rotation(rot.z, 4, 'Z')
            
            rot_matrix = rx @ ry @ rz
            rot_matrix = bridge_utils.flatten_matrix(rot_matrix)

            rotation = ArnoldMatrix()
            rotation.convert_from_buffer(rot_matrix)

            matrix = self.get_matrix("matrix")
            matrix.multiply(rotation)

            self.set_matrix("matrix", matrix)
        
        # Set general attributes
        data = datablock.arnold.data

        self.set_int("samples", data.samples)
        self.set_bool("normalize", data.normalize)

        self.set_bool("cast_shadows", data.cast_shadows)
        self.set_bool("cast_volumetric_shadows", data.cast_volumetric_shadows)
        self.set_rgb("shadow_color", *data.shadow_color)
        self.set_float("shadow_density", data.shadow_density)

        self.set_float("camera", data.camera)
        self.set_float("diffuse", data.diffuse)
        self.set_float("specular", data.specular)
        self.set_float("transmission", data.transmission)
        self.set_float("sss", data.sss)
        self.set_float("indirect", data.indirect)
        self.set_float("volume", data.volume)
        self.set_int("max_bounces", data.max_bounces)

        return self