import bpy
import bmesh
import ctypes
import numpy

from .array import ArnoldArray
from .exportable import ArnoldNodeExportable
from . import utils as bridge_utils

class ArnoldPolymesh(ArnoldNodeExportable):
    def __init__(self, node=None, frame_set=None):
        if node:
            super().__init__(node, frame_set)
        else:
            super().__init__("polymesh", frame_set)
        
        self.mesh = None

    def __assign_shaders(self):
        materials = []

        for slot in self.datablock.material_slots:
            if slot.material:
                shader = bridge_utils.get_node_by_uuid(slot.material.uuid)
                materials.append(shader)
        
        if not materials:
            shader = bridge_utils.get_node_by_name("BTOA_MISSING_SHADER")
            materials.append(shader)
        
        if materials:
            midxs = numpy.ndarray(len(self.mesh.polygons), dtype=numpy.uint8)
            self.mesh.polygons.foreach_get("material_index", midxs)

            shaders = ArnoldArray()
            shaders.allocate(len(materials), 1, "POINTER")

            for i, mat in enumerate(materials):
                shaders.set_pointer(i, mat)
            
            shidxs = ArnoldArray()
            shidxs.convert_from_buffer(len(midxs), 1, "BYTE", ctypes.c_void_p(midxs.ctypes.data))

            self.set_array("shader", shaders)
            self.set_array("shidxs", shidxs)

    def __bake_mesh(self):
        if self.mesh:
            self.datablock.to_mesh_clear()

        mesh = self.datablock.to_mesh()

        # Ensure UV map exists
        if not mesh.uv_layers:
            mesh.uv_layers.new(name='UVMap')

        # Triangulate to remove ngons
        bm = bmesh.new()
        bm.from_mesh(mesh)

        bmesh.ops.triangulate(bm, faces=bm.faces[:])

        bm.to_mesh(mesh)
        bm.free()

        # Calculate normals
        try:
            mesh.calc_tangents()
        except:
            self.mesh = None
            return

        self.mesh = mesh

    def __get_keyed_data(self):
        sdata = self.depsgraph.scene.arnold
        frame_current = self.depsgraph.scene.frame_current
        result = [None, None] # vlist, nlist

        if sdata.enable_motion_blur and sdata.deformation_motion_blur:
            steps = numpy.linspace(sdata.shutter_start, sdata.shutter_end, sdata.motion_keys)

            for i in range(0, steps.size):
                frame, subframe = self.get_target_frame(frame_current, steps[i])
                self.frame_set(frame, subframe=subframe)
                self.__bake_mesh()

                vdata = self.__get_nonkeyed_float_data(self.mesh.vertices, 3, "co")
                ndata = self.__get_nonkeyed_float_data(self.mesh.loops, 3, "normal")

                result[0] = vdata if result[0] is None else numpy.concatenate((result[0], vdata))
                result[1] = ndata if result[1] is None else numpy.concatenate((result[1], ndata))
            
            self.frame_set(frame_current, subframe=0)
            self.__bake_mesh()
        else:
            result[0] = self.__get_nonkeyed_float_data(self.mesh.vertices, 3, "co")
            result[1] = self.__get_nonkeyed_float_data(self.mesh.loops, 3, "normal")

        return result

    def __get_nonkeyed_uint_data(self, data, size, param):
        result = numpy.ndarray(size, dtype=numpy.uint32)
        data.foreach_get(param, result)
        return result
    
    def __get_nonkeyed_float_data(self, data, size, param):
        result = numpy.ndarray(len(data) * size, dtype=numpy.float32)
        data.foreach_get(param, result)
        return result

    def __format_data(self, size, keys, dtype, data):
        result = ArnoldArray()
        result.convert_from_buffer(size, keys, dtype, ctypes.c_void_p(data.ctypes.data))
        return result

    def __apply_matrix_data(self):
        matrix = self.get_transform_matrix()

        sdata = self.depsgraph.scene.arnold
        if sdata.enable_motion_blur:
            self.set_array("matrix", matrix)
        else:
            self.set_matrix("matrix", matrix)
    
    def __apply_geometry_data(self):
        sdata = self.depsgraph.scene.arnold
        keys = sdata.motion_keys if sdata.enable_motion_blur and sdata.deformation_motion_blur else 1

        vdata, ndata = self.__get_keyed_data()
        nsdata = self.__get_nonkeyed_uint_data(self.mesh.polygons, len(self.mesh.polygons), "loop_total")
        vidata = self.__get_nonkeyed_uint_data(self.mesh.polygons, len(self.mesh.loops), "vertices")
        nidata = numpy.arange(len(self.mesh.loops), dtype=numpy.uint32)

        vlist = self.__format_data(len(self.mesh.vertices), keys, 'VECTOR', vdata)
        nlist = self.__format_data(len(self.mesh.loops), keys, 'VECTOR', ndata)
        nsides = self.__format_data(len(self.mesh.polygons), 1, 'UINT', nsdata)
        vidxs = self.__format_data(len(self.mesh.loops), 1, 'UINT', vidata)
        nidxs = self.__format_data(len(self.mesh.loops), 1, 'UINT', nidata)

        self.set_array("vlist", vlist)
        self.set_array("nlist", nlist)
        self.set_array("nsides", nsides)
        self.set_array("vidxs", vidxs)
        self.set_array("nidxs", nidxs)

    def __apply_uv_map_data(self):
        for i, uvt in enumerate(self.mesh.uv_layers):
            if uvt.active_render:
                uv_data = self.mesh.uv_layers[i].data
                size = len(uv_data)

                data = numpy.arange(size, dtype=numpy.uint32)
                uvidxs = ArnoldArray()
                uvidxs.convert_from_buffer(size, 1, 'UINT', data.ctypes.data)

                data = self.__get_nonkeyed_float_data(uv_data, 2, "uv")
                uvlist = ArnoldArray()
                uvlist.convert_from_buffer(size, 1, 'VECTOR2', data.ctypes.data)

                self.set_array("uvidxs", uvidxs)
                self.set_array("uvlist", uvlist)

                break

    def from_datablock(self, depsgraph, datablock):
        self.depsgraph = depsgraph

        self.evaluate_datablock(datablock)
        if not self.datablock:
            return None
        
        self.__bake_mesh()
        if not self.mesh:
            return None
        
        # General settings
        sdata = depsgraph.scene.arnold
        self.set_uuid(self.datablock.uuid)
        self.set_string("name", self.datablock.name)
        self.set_bool("smoothing", True)
        self.set_float("motion_start", sdata.shutter_start)
        self.set_float("motion_end", sdata.shutter_end)

        # Subdivision surface settings
        data = self.datablock.arnold
        self.set_string("subdiv_type", data.subdiv_type)
        self.set_byte("subdiv_iterations", data.subdiv_iterations)
        self.set_float("subdiv_adaptive_error", data.subdiv_adaptive_error)
        self.set_string("subdiv_adaptive_metric", data.subdiv_adaptive_metric)
        self.set_string("subdiv_adaptive_space", data.subdiv_adaptive_space)
        self.set_bool("subdiv_frustum_ignore", data.subdiv_frustum_ignore)
        self.set_string("subdiv_uv_smoothing", data.subdiv_uv_smoothing)
        self.set_bool("subdiv_smooth_derivs", data.subdiv_smooth_derivs)

        # Everything else
        self.__apply_matrix_data()
        self.__bake_mesh()
        self.__apply_geometry_data()
        self.__apply_uv_map_data()
        self.__assign_shaders()
        # TODO
        #self.__set_visibility()

        self.datablock.to_mesh_clear()

        return self