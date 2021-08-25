from .array import ArnoldArray
from .colormanager import ArnoldColorManager
from .node import ArnoldNode
from .polymesh import ArnoldPolymesh
from .universe_options import UniverseOptions
from .constants import BTOA_CONVERTIBLE_TYPES, BTOA_LIGHT_SHAPE_CONVERSIONS, BTOA_LIGHT_CONVERSIONS
from . import utils as export_utils

import bmesh
import ctypes
import os
import math
import numpy
import mathutils

class Exporter:
    def __init__(self, session):
        self.session = session

    def __get_target_frame(self, motion_step):
        frame_flt = frame_current + motion_step
        frame_int = math.floor(frame_flt)
        subframe = frame_flt - frame_int

        return frame_int, subframe

    def __evaluate_mesh(self, ob):
        mesh = ob.to_mesh()

        # Create a blank UV map if none exist

        if len(mesh.uv_layers) == 0:
            mesh.uv_layers.new(name='UVMap')

        # Triangulate mesh to remove ngons
        
        bm = bmesh.new()
        bm.from_mesh(mesh)

        bmesh.ops.triangulate(bm, faces=bm.faces[:])

        bm.to_mesh(mesh)
        bm.free()

        # Calculate normals and return
        
        try:
            mesh.calc_tangents()
            return mesh
        except:
            return None

    def __get_static_mesh_data(self, mesh):
        vlist_data = numpy.ndarray(len(mesh.vertices) * 3, dtype=numpy.float32)
        mesh.vertices.foreach_get("co", vlist_data)

        nlist_data = numpy.ndarray(len(mesh.loops) * 3, dtype=numpy.float32)
        mesh.loops.foreach_get("normal", nlist_data)

        return vlist_data, nlist_data

    def create_polymesh(self, object_instance):
        scene = self.session.depsgraph.scene
        data = scene.arnold

        # Evaluate geometry at current frame

        ob = export_utils.get_object_data_from_instance(object_instance)
        mesh = self.__evaluate_mesh(ob)

        if not mesh:
            return None

        # Calculate matrix data
        matrix = None
        vlist_data = None
        nlist_data = None

        if data.enable_motion_blur:
            motion_steps = numpy.linspace(data.shutter_start, data.shutter_end, data.motion_keys)
            frame_current = scene.frame_current

            # Transform motion blur
            # TODO: I think this needs to be `transform_motion_blur`

            if data.camera_motion_blur:
                matrix = self.get_transform_blur_matrix(object_instance)
            else:
                matrix = export_utils.flatten_matrix(object_instance.matrix_world)

            # Deformation motion blur

            if data.deformation_motion_blur:
                for i in range(0, motion_steps.size):
                    frame, subframe = self.__get_target_frame(motion_step[i])

                    self.session.engine.frame_set(frame, subframe=subframe)
                    _mesh = self.__evaluate_mesh(ob)

                    # vlist data

                    a = numpy.ndarray(len(mesh.vertices) * 3, dtype=numpy.float32)
                    _mesh.vertices.foreach_get("co", a)

                    vlist_data = a if vlist_data is None else numpy.concatenate((vlist_data, a))

                    # nlist data

                    a = numpy.ndarray(len(mesh.loops) * 3, dtype=numpy.float32)
                    _mesh.loops.foreach_get("normal", a)

                    nlist_data = a if nlist_data is None else numpy.concatenate((nlist_data, a))
            else:
                vlist_data, nlist_data = self.__get_static_mesh_data(mesh)

            # Compile vlist and nlist

            vlist = ArnoldArray()
            vlist.convert_from_buffer(
                len(mesh.vertices),
                data.motion_keys,
                'VECTOR',
                ctypes.c_void_p(vlist_data.ctypes.data)
            )

            nlist = ArnoldArray()
            nlist.convert_from_buffer(
                len(mesh.loops),
                data.motion_keys,
                'VECTOR',
                ctypes.c_void_p(nlist_data.ctypes.data)
            )

        # Calculate without motion blur

        else:
            matrix = export_utils.flatten_matrix(object_instance.matrix_world)

            vlist_data, nlist_data = self.__get_static_mesh_data(mesh)

            vlist = ArnoldArray()
            vlist.convert_from_buffer(
                len(mesh.vertices),
                1,
                'VECTOR',
                ctypes.c_void_p(vlist_data.ctypes.data)
            )

            nlist = ArnoldArray()
            nlist.convert_from_buffer(
                len(mesh.loops),
                1,
                'VECTOR',
                ctypes.c_void_p(nlist_data.ctypes.data)
            )

        # Polygons

        nsides_data = numpy.ndarray(len(mesh.polygons), dtype=numpy.uint32)
        mesh.polygons.foreach_get("loop_total", nsides_data)

        nsides = ArnoldArray()
        nsides.convert_from_buffer(
            len(mesh.polygons),
            1,
            'UINT',
            ctypes.c_void_p(nsides_data.ctypes.data)
        )

        vidxs_data = numpy.ndarray(len(mesh.loops), dtype=numpy.uint32)
        mesh.polygons.foreach_get("vertices", vidxs_data)

        vidxs = ArnoldArray()
        vidxs.convert_from_buffer(
            len(mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(vidxs_data.ctypes.data)
        )

        nidxs_data = numpy.arange(len(mesh.loops), dtype=numpy.uint32)
        
        nidxs = ArnoldArray()
        nidxs.convert_from_buffer(
            len(mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(nidxs_data.ctypes.data)
        )

        # Create polymesh object
        
        name = export_utils.get_unique_name(object_instance)
        node = ArnoldPolymesh(name)

        if data.enable_motion_blur and data.camera_motion_blur:
            node.set_array("matrix", matrix)
        else:
            node.set_matrix("matrix", matrix)
        
        node.set_bool("smoothing", True)
        node.set_array("vlist", vlist)
        node.set_array("nlist", nlist)
        node.set_array("nsides", nsides)
        node.set_array("vidxs", vidxs)
        node.set_array("nidxs", nidxs)
        node.set_float("motion_start", data.shutter_start)
        node.set_float("motion_end", data.shutter_end)

        # UV's
        for i, uvt in enumerate(mesh.uv_layers):
            if uvt.active_render:
                uv_data = mesh.uv_layers[i].data
                
                uvidxs_data = numpy.arange(len(uv_data), dtype=numpy.uint32)
                uvidxs = ArnoldArray()
                uvidxs.convert_from_buffer(
                    len(uv_data),
                    1,
                    'UINT',
                    ctypes.c_void_p(uvidxs_data.ctypes.data)
                )

                uvlist_data = numpy.ndarray(len(uv_data) * 2, dtype=numpy.float32)
                uv_data.foreach_get("uv", uvlist_data)

                uvlist = ArnoldArray()
                uvlist.convert_from_buffer(
                    len(uv_data),
                    1,
                    'VECTOR2',
                    ctypes.c_void_p(uvlist_data.ctypes.data)
                )

                node.set_array("uvidxs", uvidxs)
                node.set_array("uvlist", uvlist)

                break

        # Materials

        materials = []

        for slot in ob.material_slots:
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

        material_indices = numpy.ndarray(len(mesh.polygons), dtype=numpy.uint8)
        mesh.polygons.foreach_get("material_index", material_indices)

        shader_array = ArnoldArray()
        shader_array.allocate(len(materials), 1, "POINTER")

        for i, mat in enumerate(materials):
            shader_array.set_pointer(i, mat)

        shidxs = ArnoldArray()
        shidxs.convert_from_buffer(
            len(material_indices),
            1,
            "BYTE",
            ctypes.c_void_p(material_indices.ctypes.data)
        )

        node.set_array("shader", shader_array)
        node.set_array("shidxs", shidxs)

        return node

    def create_world(self, world):
        data = world.arnold.data
        
        surface, volume, displacement = world.arnold.node_tree.export()
        node = surface[0]
        
        unique_name = export_utils.get_unique_name(world)
        node.set_string("name", unique_name)

        # Flip image textures in the U direction
        image = node.get_link("color")
        if image.is_valid() and image.type_is("image"):
            sflip = image.get_bool("sflip")
            image.set_bool("sflip", not sflip)

        node.set_int("samples", data.samples)
        node.set_bool("normalize", data.normalize)

        node.set_bool("cast_shadows", data.cast_shadows)
        node.set_bool("cast_volumetric_shadows", data.cast_volumetric_shadows)
        node.set_rgb("shadow_color", *data.shadow_color)
        node.set_float("shadow_density", data.shadow_density)

        node.set_float("camera", data.camera)
        node.set_float("diffuse", data.diffuse)
        node.set_float("specular", data.specular)
        node.set_float("transmission", data.transmission)
        node.set_float("sss", data.sss)
        node.set_float("indirect", data.indirect)
        node.set_float("volume", data.volume)
        node.set_int("max_bounces", data.max_bounces)

        return node

    def create_camera(self, object_instance):
        node = ArnoldNode("persp_camera")
        self.sync_camera(node, object_instance)

        return node

    def create_light(self, object_instance):
        ob = export_utils.get_object_data_from_instance(object_instance)

        ntype = BTOA_LIGHT_SHAPE_CONVERSIONS[ob.data.shape] if ob.data.type == 'AREA' else BTOA_LIGHT_CONVERSIONS[ob.data.type]
        node = ArnoldNode(ntype)
        self.sync_light(node, object_instance)

        return node

    def sync_camera(self, node, object_instance):
        ob = export_utils.get_object_data_from_instance(object_instance)
        scene_data = self.session.depsgraph.scene.arnold
        camera_data = ob.data

        node.set_string("name", export_utils.get_unique_name(object_instance))

        if scene_data.enable_motion_blur and scene_data.camera_motion_blur:
            matrix = self.get_transform_blur_matrix(object_instance)
            node.set_array("matrix", matrix)
        else:
            matrix = export_utils.flatten_matrix(object_instance.matrix_world)
            node.set_matrix("matrix", matrix)

        fov = export_utils.calc_horizontal_fov(ob)
        node.set_float("fov", math.degrees(fov))
        node.set_float("exposure", camera_data.arnold.exposure)

        if camera_data.dof.focus_object:
            distance = mathutils.geometry.distance_point_to_plane(
                ob.matrix_world.to_translation(),
                camera_data.dof.focus_object.matrix_world.to_translation(),
                ob.matrix_world.col[2][:3]
            )
        else:
            distance = camera_data.dof.focus_distance

        aperture_size = camera_data.arnold.aperture_size if camera_data.arnold.enable_dof else 0

        node.set_float("focus_distance", distance)
        node.set_float("aperture_size", aperture_size)
        node.set_int("aperture_blades", camera_data.arnold.aperture_blades)
        node.set_float("aperture_rotation", camera_data.arnold.aperture_rotation)
        node.set_float("aperture_blade_curvature", camera_data.arnold.aperture_blade_curvature)
        node.set_float("aperture_aspect_ratio", camera_data.arnold.aperture_aspect_ratio)

        node.set_float("near_clip", camera_data.clip_start)
        node.set_float("far_clip", camera_data.clip_end)

        if scene_data.enable_motion_blur:
            node.set_float("shutter_start", scene_data.shutter_start)
            node.set_float("shutter_end", scene_data.shutter_end)
            #node.set_string("shutter_type", scene_data.shutter_type)
            #node.set_string("rolling_shutter", scene_data.rolling_shutter)
            #node.set_float("rolling_shutter_duration", scene_data.rolling_shutter_duration)

    def sync_light(self, node, object_instance):    
        ob = export_utils.get_object_data_from_instance(object_instance)
        data = ob.data

        node.set_string("name", export_utils.get_unique_name(object_instance))

        # Set matrix for everything except cylinder lights
        if not hasattr(data, "shape") or data.shape != 'RECTANGLE':
            node.set_matrix(
                "matrix",
                export_utils.flatten_matrix(ob.matrix_world)
            )
        
        node.set_rgb("color", *data.color)
        node.set_float("intensity", data.arnold.intensity)
        node.set_float("exposure", data.arnold.exposure)
        node.set_int("samples", data.arnold.samples)
        node.set_bool("normalize", data.arnold.normalize)

        node.set_bool("cast_shadows", data.arnold.cast_shadows)
        node.set_bool("cast_volumetric_shadows", data.arnold.cast_volumetric_shadows)
        node.set_rgb("shadow_color", *data.arnold.shadow_color)
        node.set_float("shadow_density", data.arnold.shadow_density)

        node.set_float("camera", data.arnold.camera)
        node.set_float("diffuse", data.arnold.diffuse)
        node.set_float("specular", data.arnold.specular)
        node.set_float("transmission", data.arnold.transmission)
        node.set_float("sss", data.arnold.sss)
        node.set_float("indirect", data.arnold.indirect)
        node.set_float("volume", data.arnold.volume)
        node.set_int("max_bounces", data.arnold.max_bounces)

        if data.type in ('POINT', 'SPOT'):
            node.set_float("radius", data.shadow_soft_size)

        if data.type == 'SUN':
            node.set_float("angle", data.arnold.angle)

        if data.type == 'SPOT':
            node.set_float("cone_angle", math.degrees(data.spot_size))
            node.set_float("penumbra_angle", math.degrees(data.arnold.penumbra_angle))
            node.set_float("roundness", data.arnold.spot_roundness)
            node.set_float("aspect_ratio", data.arnold.aspect_ratio)
            node.set_float("lens_radius", data.arnold.lens_radius)

        if data.type == 'AREA':
            node.set_float("roundness", data.arnold.area_roundness)
            node.set_float("spread", data.arnold.spread)
            node.set_int("resolution", data.arnold.resolution)
            node.set_float("soft_edge", data.arnold.soft_edge)
            
            if data.shape == 'SQUARE':
                smatrix = mathutils.Matrix.Diagonal((
                    data.size / 2,
                    data.size / 2,
                    data.size / 2
                )).to_4x4()
                
                tmatrix = ob.matrix_world @ smatrix
            
                node.set_matrix(
                    "matrix",
                    export_utils.flatten_matrix(tmatrix)
                )
            elif data.shape == 'DISK':
                s = ob.scale.x if ob.scale.x > ob.scale.y else ob.scale.y
                node.set_float("radius", 0.5 * data.size * s)
            elif data.shape == 'RECTANGLE':
                d = 0.5 * data.size_y * ob.scale.y
                top = export_utils.get_position_along_local_vector(ob, d, 'Y')
                bottom = export_utils.get_position_along_local_vector(ob, -d, 'Y')

                node.set_vector("top", *top)
                node.set_vector("bottom", *bottom)

                s = ob.scale.x if ob.scale.x > ob.scale.z else ob.scale.z
                node.set_float("radius", 0.5 * data.size * s)

    def export(self):
        scene = self.session.depsgraph.scene
        options = UniverseOptions()

        # Set resolution settings

        options.set_render_resolution(*export_utils.get_render_resolution(scene))

        if scene.render.use_border:
            min_x = int(x * render.border_min_x)
            min_y = int(math.ceil(y * (1 - render.border_max_y)))
            max_x = int(x * render.border_max_x) - 1 # I don't know why, but subtracting 1px here avoids weird render artifacts
            max_y = int(math.ceil(y * (1 - render.border_min_y)))

            options.set_render_region(min_x, min_y, max_x, max_y)
        
        # Set global render settings

        options.set_int("render_device", int(scene.arnold.render_device))

        options.set_int("AA_samples", scene.arnold.aa_samples)
        options.set_int("GI_diffuse_samples", scene.arnold.diffuse_samples)
        options.set_int("GI_specular_samples", scene.arnold.specular_samples)
        options.set_int("GI_transmission_samples", scene.arnold.transmission_samples)
        options.set_int("GI_sss_samples", scene.arnold.sss_samples)
        options.set_int("GI_volume_samples", scene.arnold.volume_samples)
        options.set_float("AA_sample_clamp", scene.arnold.sample_clamp)
        options.set_bool("AA_sample_clamp_affects_aovs", scene.arnold.clamp_aovs)
        options.set_float("indirect_sample_clamp", scene.arnold.indirect_sample_clamp)
        options.set_float("low_light_threshold", scene.arnold.low_light_threshold)

        options.set_bool("enable_adaptive_sampling", scene.arnold.use_adaptive_sampling)
        options.set_int("AA_samples_max", scene.arnold.adaptive_aa_samples_max)
        options.set_float("adaptive_threshold", scene.arnold.adaptive_threshold)

        if scene.arnold.aa_seed > 0:
            options.set_int("AA_seed", scene.arnold.aa_seed)

        options.set_int("GI_total_depth", scene.arnold.total_depth)
        options.set_int("GI_diffuse_depth", scene.arnold.diffuse_depth)
        options.set_int("GI_specular_depth", scene.arnold.specular_depth)
        options.set_int("GI_transmission_depth", scene.arnold.transmission_depth)
        options.set_int("GI_volume_depth", scene.arnold.volume_depth)
        options.set_int("auto_transparency_depth", scene.arnold.transparency_depth)

        options.set_int("bucket_size", scene.arnold.bucket_size)
        options.set_string("bucket_scanning", scene.arnold.bucket_scanning)
        options.set_bool("parallel_node_init", scene.arnold.parallel_node_init)
        options.set_int("threads", scene.arnold.threads)

        # Export scene objects

        for object_instance in self.session.depsgraph.object_instances:
            ob = export_utils.get_object_data_from_instance(object_instance)
            ob_unique_name = export_utils.get_unique_name(object_instance)

            node = self.session.get_node_by_name(ob_unique_name)

            if not node.is_valid():
                if ob.type in BTOA_CONVERTIBLE_TYPES:
                    node = self.create_polymesh(object_instance)
                elif ob.name == scene.camera.name:
                    node = self.create_camera(object_instance)
                    options.set_pointer("camera", node)
                
                if ob.type == 'LIGHT':
                    node = self.create_light(object_instance)

        # Export world settings

        if scene.world.arnold.node_tree:
            self.create_world(scene.world)        

        # Add final required nodes

        default_filter = ArnoldNode("gaussian_filter")
        default_filter.set_string("name", "gaussianFilter")

        outputs = ArnoldArray()
        outputs.allocate(1, 1, 'STRING')
        outputs.set_string(0, "RGBA RGBA gaussianFilter __display_driver")
        options.set_array("outputs", outputs)

        color_manager = ArnoldColorManager()
        color_manager.set_string("config", os.getenv("OCIO"))
        options.set_pointer("color_manager", color_manager)

    def get_transform_blur_matrix(self, object_instance):
        matrix = ArnoldArray()
        matrix.allocate(1, data.motion_keys, 'MATRIX')
        
        for i in range(0, motion_steps.size):
            frame, subframe = self.__get_target_frame(motion_step[i])

            self.session.engine.frame_set(frame, subframe=subframe)
            
            m = export_utils.flatten_matrix(object_instance.matrix_world)
            matrix.set_matrix(i, m)

        self.session.engine.frame_set(frame_current, subframe=0)

        return matrix