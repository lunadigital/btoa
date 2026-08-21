import bpy
import ctypes
import numpy

from .array import ArnoldArray
from .constants import BTOA_VISIBILITY
from .exportable import ArnoldNodeExportable
from . import utils as bridge_utils
from . import types as bridge_types


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
                materials.append(slot.material)

        if not materials:
            shader = bridge_utils.get_node_by_name("BTOA_MISSING_SHADER")
            self.set_pointer("shader", shader)
            return

        if materials:
            midxs = numpy.ndarray(len(self.mesh.polygons), dtype=numpy.uint8)
            self.mesh.polygons.foreach_get("material_index", midxs)

            shaders = ArnoldArray()
            shaders.allocate(len(materials), 1, "POINTER")

            for i, mat in enumerate(materials):
                shader = bridge_utils.get_node_by_uuid(mat.uuid)
                shaders.set_pointer(i, shader)

            shidxs = ArnoldArray()
            shidxs.convert_from_buffer(len(midxs), 1, "BYTE", ctypes.c_void_p(midxs.ctypes.data))

            self.set_array("shader", shaders)
            self.set_array("shidxs", shidxs)

            # Apply displacement from first material with displacement
            for mat in materials:
                if mat.arnold.node_tree and mat.arnold.node_tree.has_displacement():
                    disp_data = mat.arnold.node_tree.export_active_displacement()
                    if disp_data and disp_data.type == bridge_types.ExportDataType.GROUP:
                        # disp_data.value is a tuple: (input, padding, height, zero_value, autobump)
                        disp_input, disp_padding, disp_height, disp_zero, disp_autobump = disp_data.value

                        # Set displacement shader
                        if disp_input.type == bridge_types.ExportDataType.NODE:
                            self.set_pointer("disp_map", disp_input.value)

                        # Set displacement parameters
                        if disp_padding.type == bridge_types.ExportDataType.FLOAT:
                            self.set_float("disp_padding", disp_padding.value)
                        if disp_height.type == bridge_types.ExportDataType.FLOAT:
                            self.set_float("disp_height", disp_height.value)
                        if disp_zero.type == bridge_types.ExportDataType.FLOAT:
                            self.set_float("disp_zero_value", disp_zero.value)

                        self.set_bool("disp_autobump", disp_autobump)

                        print(f"[DISPLACEMENT] Applied to {self.datablock.name}")
                        break

    def __bake_mesh(self):
        if self.mesh:
            self.datablock.to_mesh_clear()

        mesh = self.datablock.to_mesh()

        # Ensure UV map exists
        if not mesh.uv_layers:
            mesh.uv_layers.new(name='UVMap')

        # Compute split normals for per-loop normal export.
        # Arnold handles quads and n-gons natively via the nsides array,
        # so we skip bmesh triangulation entirely — this is the single
        # biggest performance win for heavy geometry in IPR.
        #
        # Blender 4.0+ removed calc_normals_split() — normals are available
        # directly via corner_normals or loops[].normal after to_mesh().
        if hasattr(mesh, 'calc_normals_split'):
            try:
                mesh.calc_normals_split()
            except RuntimeError:
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
                ndata = self.__get_loop_normals()

                result[0] = vdata if result[0] is None else numpy.concatenate((result[0], vdata))
                result[1] = ndata if result[1] is None else numpy.concatenate((result[1], ndata))

            self.frame_set(frame_current, subframe=0)
            self.__bake_mesh()
        else:
            result[0] = self.__get_nonkeyed_float_data(self.mesh.vertices, 3, "co")
            result[1] = self.__get_loop_normals()

        return result

    def __get_loop_normals(self):
        """Get per-loop normals, compatible with Blender 3.x and 4.0+."""
        num_loops = len(self.mesh.loops)

        # Blender 4.0+: use corner_normals attribute if available
        if hasattr(self.mesh, 'corner_normals') and len(self.mesh.corner_normals) > 0:
            ndata = numpy.zeros(num_loops * 3, dtype=numpy.float32)
            self.mesh.corner_normals.foreach_get("vector", ndata)
            return ndata

        # Blender 3.x: read from loops after calc_normals_split()
        ndata = numpy.zeros(num_loops * 3, dtype=numpy.float32)
        self.mesh.loops.foreach_get("normal", ndata)
        return ndata

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

    def __export_custom_attributes(self):
        """Export Blender custom mesh attributes as Arnold user data.

        This makes attributes like color attributes and custom float/int/vector
        attributes available to user_data_* shader nodes in Arnold.
        Uses self.mesh which is the evaluated mesh (native topology, no triangulation).
        """
        if not self.mesh:
            return

        # Built-in attributes to skip (already handled by geometry export)
        SKIP_ATTRS = {'position', 'sharp_face', 'sharp_edge', 'material_index',
                      'shade_smooth', '.edge_verts', '.corner_vert', '.corner_edge',
                      'crease_vert', 'crease_edge', 'UVMap'}

        try:
            for attr in self.mesh.attributes:
                if attr.name in SKIP_ATTRS or attr.name.startswith('.'):
                    continue

                domain = attr.domain      # 'POINT', 'FACE', 'CORNER', 'EDGE'
                data_type = attr.data_type # 'FLOAT', 'INT', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'BYTE_COLOR', etc.
                attr_len = len(attr.data)

                if attr_len == 0:
                    continue

                # Map Blender domain to Arnold declaration scope
                if domain == 'FACE':
                    scope = 'uniform'
                elif domain == 'POINT':
                    scope = 'varying'
                elif domain == 'CORNER':
                    scope = 'varying'
                else:
                    continue  # Skip EDGE domain, not useful for shading

                try:
                    if data_type == 'FLOAT':
                        values = numpy.zeros(attr_len, dtype=numpy.float32)
                        attr.data.foreach_get('value', values)
                        self.declare(attr.name, f"{scope} FLOAT")
                        arr = ArnoldArray()
                        arr.convert_from_buffer(attr_len, 1, 'FLOAT',
                                                ctypes.c_void_p(values.ctypes.data))
                        self.set_array(attr.name, arr)

                    elif data_type == 'INT':
                        values = numpy.zeros(attr_len, dtype=numpy.int32)
                        attr.data.foreach_get('value', values)
                        self.declare(attr.name, f"{scope} INT")
                        arr = ArnoldArray()
                        arr.convert_from_buffer(attr_len, 1, 'UINT',
                                                ctypes.c_void_p(values.ctypes.data))
                        self.set_array(attr.name, arr)

                    elif data_type in ('FLOAT_COLOR', 'BYTE_COLOR'):
                        values = numpy.zeros(attr_len * 4, dtype=numpy.float32)
                        attr.data.foreach_get('color', values)
                        self.declare(attr.name, f"{scope} RGBA")
                        arr = ArnoldArray()
                        arr.convert_from_buffer(attr_len, 1, 'RGBA',
                                                ctypes.c_void_p(values.ctypes.data))
                        self.set_array(attr.name, arr)

                    elif data_type == 'FLOAT_VECTOR':
                        values = numpy.zeros(attr_len * 3, dtype=numpy.float32)
                        attr.data.foreach_get('vector', values)
                        self.declare(attr.name, f"{scope} VECTOR")
                        arr = ArnoldArray()
                        arr.convert_from_buffer(attr_len, 1, 'VECTOR',
                                                ctypes.c_void_p(values.ctypes.data))
                        self.set_array(attr.name, arr)

                    elif data_type == 'FLOAT2':
                        values = numpy.zeros(attr_len * 2, dtype=numpy.float32)
                        attr.data.foreach_get('vector', values)
                        self.declare(attr.name, f"{scope} VECTOR2")
                        arr = ArnoldArray()
                        arr.convert_from_buffer(attr_len, 1, 'VECTOR2',
                                                ctypes.c_void_p(values.ctypes.data))
                        self.set_array(attr.name, arr)

                    else:
                        continue

                    print(f"[POLYMESH] Exported attribute '{attr.name}': domain={domain}, type={data_type}, count={attr_len}")

                except Exception as e:
                    print(f"[POLYMESH] Could not export attribute '{attr.name}': {e}")

        except Exception as e:
            print(f"[POLYMESH] Error exporting custom attributes: {e}")

    def __set_visibility(self):
        data = self.datablock.arnold
        visibility = 0

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

        for i in range(0, len(visibility_options)):
            if visibility_options[i]:
                visibility += BTOA_VISIBILITY[i]

        # Remove camera visibility if object is indirect only
        if (self.datablock.indirect_only_get(view_layer=self.depsgraph.view_layer_eval)
            or self.is_instance
            and self.parent.indirect_only_get(view_layer=self.depsgraph.view_layer_eval)
            ):
            visibility -= 1

        self.set_byte("visibility", visibility)

        self.set_bool(
            "matte",
            (self.datablock.holdout_get(view_layer=self.depsgraph.view_layer_eval)
            or self.is_instance
            and self.parent is not None
            and self.parent.holdout_get(view_layer=self.depsgraph.view_layer_eval)
            )
        )

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
        self.set_uuid(self.parent.uuid if self.is_instance else self.datablock.uuid)
        self.set_string("name", self.datablock.name)
        self.set_bool("smoothing", True)
        self.set_float("motion_start", sdata.shutter_start)
        self.set_float("motion_end", sdata.shutter_end)

        # Subdivision surface settings
        data = self.datablock.arnold

        # Debug subdivision
        print(f"[SUBDIV DEBUG] Object: {self.datablock.name}")
        print(f"[SUBDIV DEBUG] Type: {data.subdiv_type}")
        print(f"[SUBDIV DEBUG] Iterations: {data.subdiv_iterations}")

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
        self.__apply_geometry_data()
        self.__apply_uv_map_data()
        self.__export_custom_attributes()
        self.__assign_shaders()
        self.__set_visibility()

        self.datablock.to_mesh_clear()

        return self
