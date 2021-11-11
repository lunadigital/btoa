import bmesh
import ctypes
import math
import numpy

from .object_exporter import ObjectExporter

from ..array import ArnoldArray
from ..constants import BTOA_VISIBILITY
from ..polymesh import ArnoldPolymesh
from .. import utils as export_utils

class PolymeshExporter(ObjectExporter):
    def build_shaders(self):
        material_override = self.cache.view_layer.material_override

        if material_override:
            unique_name = export_utils.get_unique_name(material_override)

            if material_override.arnold.node_tree:
                shader = self.session.get_node_by_name(unique_name)

                if shader.is_valid():
                    self.node.set_pointer("shader", shader)
                else:
                    surface, volume, displacement = material_override.arnold.node_tree.export()
                    surface[0].set_string("name", unique_name)
                    self.node.set_pointer("shader", surface[0])
        
        else:
            materials = []

            for slot in self.datablock_eval.material_slots:
                if slot.material:
                    unique_name = export_utils.get_unique_name(slot.material)

                    if slot.material.arnold.node_tree:
                        shader = self.session.get_node_by_name(unique_name)

                        if shader.is_valid():
                            materials.append(shader)
                        else:
                            surface, volume, displacement = slot.material.arnold.node_tree.export()
                            shader = surface[0]

                            shader.set_string("name", unique_name)
                            materials.append(shader)
            
            if len(materials) > 0:
                material_indices = numpy.ndarray(
                    len(self.mesh.polygons),
                    dtype=numpy.uint8
                )
                self.mesh.polygons.foreach_get("material_index", material_indices)

                shader_array = ArnoldArray()
                shader_array.allocate(
                    len(materials),
                    1,
                    'POINTER'
                )

                for i, mat in enumerate(materials):
                    shader_array.set_pointer(i, mat)

                shidxs = ArnoldArray()
                shidxs.convert_from_buffer(
                    len(material_indices),
                    1,
                    'BYTE',
                    ctypes.c_void_p(material_indices.ctypes.data)
                )

                self.node.set_array("shader", shader_array)
                self.node.set_array("shidxs", shidxs)

    def get_static_mesh_data(self):
        vlist_data = numpy.ndarray(
            len(self.mesh.vertices) * 3,
            dtype=numpy.float32
        )
        self.mesh.vertices.foreach_get("co", vlist_data)

        nlist_data = numpy.ndarray(
            len(self.mesh.loops) * 3,
            dtype=numpy.float32
        )
        self.mesh.loops.foreach_get("normal", nlist_data)

        return vlist_data, nlist_data

    def generate_matrices(self):
        matrix = None
        vlist_data = None
        nlist_data = None

        if self.cache.scene["enable_motion_blur"]:
            matrix = self.get_blur_matrices()
            self.evaluate_mesh()

            if self.cache.scene["deformation_motion_blur"]:
                motion_steps = numpy.linspace(
                    self.cache.scene["shutter_start"],
                    self.cache.scene["shutter_end"],
                    self.cache.scene["motion_keys"]
                )

                for i in range(0, motion_steps.size):
                    frame, subframe = self.get_target_frame(motion_steps[i])
                    self.cache.frame_set(frame, subframe=subframe)

                    self.evaluate_mesh()

                    v, n = self.get_static_mesh_data()

                    vlist_data = v if vlist_data is None else numpy.concatenate((vlist_data, v))
                    nlist_data = n if nlist_data is None else numpy.concatenate((nlist_data, n))

                self.cache.frame_set(self.cache.scene["frame_current"], subframe=0)
                self.evaluate_mesh()

            else:
                vlist_data, nlist_data = self.get_static_mesh_data()
        
        else:
            matrix = export_utils.flatten_matrix(self.datablock.matrix_world)
            vlist_data, nlist_data = self.get_static_mesh_data()
        
        return matrix, vlist_data, nlist_data
    
    def extract_mesh_data(self, vlist_data, nlist_data):
        sdata = self.cache.scene

        keys = sdata["motion_keys"] if sdata["enable_motion_blur"] and sdata["deformation_motion_blur"] else 1

        vlist = ArnoldArray()
        vlist.convert_from_buffer(
            len(self.mesh.vertices),
            keys,
            'VECTOR',
            ctypes.c_void_p(vlist_data.ctypes.data)
        )

        nlist = ArnoldArray()
        nlist.convert_from_buffer(
            len(self.mesh.loops),
            keys,
            'VECTOR',
            ctypes.c_void_p(nlist_data.ctypes.data)
        )

        nsides_data = numpy.ndarray(
            len(self.mesh.polygons),
            dtype=numpy.uint32
        )
        self.mesh.polygons.foreach_get("loop_total", nsides_data)

        nsides = ArnoldArray()
        nsides.convert_from_buffer(
            len(self.mesh.polygons),
            1,
            'UINT',
            ctypes.c_void_p(nsides_data.ctypes.data)
        )

        vidxs_data = numpy.ndarray(
            len(self.mesh.loops),
            dtype=numpy.uint32
        )
        self.mesh.polygons.foreach_get("vertices", vidxs_data)

        vidxs = ArnoldArray()
        vidxs.convert_from_buffer(
            len(self.mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(vidxs_data.ctypes.data)
        )

        nidxs_data = numpy.arange(
            len(self.mesh.loops),
            dtype=numpy.uint32
        )
        
        nidxs = ArnoldArray()
        nidxs.convert_from_buffer(
            len(self.mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(nidxs_data.ctypes.data)
        )

        return vlist, nlist, nsides, vidxs, nidxs

    def export(self, instance, interactive=False):
        super().export(instance)
        self.datablock_eval = export_utils.get_object_data_from_instance(instance)

        self.evaluate_mesh()

        if not self.mesh:
            return None

        # If self.node already exists, it will sync all new
        # data with the existing BtoA node
        if not self.node.is_valid():
            name = export_utils.get_unique_name(self.datablock_eval)
            self.node = ArnoldPolymesh(name)

        # General settings
        self.node.set_bool("smoothing", True)
        self.node.set_float("motion_start", self.cache.scene["shutter_start"])
        self.node.set_float("motion_end", self.cache.scene["shutter_end"])

        self.generate_polymesh_data()
        self.generate_uv_map_data()
        self.build_shaders()

        self.set_visibility_options()

        return self.node

    def evaluate_mesh(self):
        m = self.datablock_eval.to_mesh()

        # Make sure mesh has a UV map
        if len(m.uv_layers) == 0:
            m.uv_layers.new(name='UVMap')

        # Triangulate mesh to remove ngons
        bm = bmesh.new()
        bm.from_mesh(m)

        bmesh.ops.triangulate(bm, faces=bm.faces[:])

        bm.to_mesh(m)
        bm.free()

        # Calculate normals
        try:
            m.calc_tangents()
            self.mesh = m
        except:
            self.mesh = None

    def generate_polymesh_data(self):
        matrix, vlist_data, nlist_data = self.generate_matrices()
        vlist, nlist, nsides, vidxs, nidxs = self.extract_mesh_data(vlist_data, nlist_data)

        if self.cache.scene["enable_motion_blur"]:
            self.node.set_array("matrix", matrix)
        else:
            self.node.set_matrix("matrix", matrix)

        self.node.set_array("vlist", vlist)
        self.node.set_array("nlist", nlist)
        self.node.set_array("nsides", nsides)
        self.node.set_array("vidxs", vidxs)
        self.node.set_array("nidxs", nidxs)

    def generate_uv_map_data(self):
        for i, uvt in enumerate(self.mesh.uv_layers):
            if uvt.active_render:
                uv_data = self.mesh.uv_layers[i].data

                uvidxs_data = numpy.arange(
                    len(uv_data),
                    dtype=numpy.uint32
                )

                uvidxs = ArnoldArray()
                uvidxs.convert_from_buffer(
                    len(uv_data),
                    1,
                    'UINT',
                    ctypes.c_void_p(uvidxs_data.ctypes.data)
                )

                uvlist_data = numpy.ndarray(
                    len(uv_data) * 2,
                    dtype=numpy.float32
                )
                uv_data.foreach_get("uv", uvlist_data)

                uvlist = ArnoldArray()
                uvlist.convert_from_buffer(
                    len(uv_data),
                    1,
                    'VECTOR2',
                    ctypes.c_void_p(uvlist_data.ctypes.data)
                )

                self.node.set_array("uvidxs", uvidxs)
                self.node.set_array("uvlist", uvlist)

                break

    def set_visibility_options(self):
        data = self.datablock_eval.arnold
        visibility_options = [
            data.camera,
            data.shadow,
            data.diffuse_transmission,
            data.specular_transmission,
            data.volume,
            data.diffuse_reflection,
            data.specular_reflection,
            data.sss
        ]

        visibility = 0
        for i in range(0, len(visibility_options)):
            if visibility_options[i]:
                visibility += BTOA_VISIBILITY[i]

        # Remove camera visibility if object is indirect only
        if self.datablock_eval.indirect_only_get(view_layer=self.cache.view_layer):
            visibility -= 1

        self.node.set_int("visibility", visibility)