import ctypes
import math
import mathutils
import numpy

from .. import btoa
from . import camera_utils, matrix_utils, mesh_utils, depsgraph_utils

def create_polymesh(object_instance):
    ob = depsgraph_utils.get_object_data_from_instance(object_instance)
    mesh = mesh_utils.bake_mesh(ob)

    if mesh is None:
        return None

    # Vertices
    a = numpy.ndarray(
        len(mesh.vertices) * 3,
        dtype=numpy.float32
    )
    mesh.vertices.foreach_get("co", a)

    vlist = btoa.BtArray()
    vlist.convert_from_buffer(
        len(mesh.vertices),
        'VECTOR',
        ctypes.c_void_p(a.ctypes.data)
    )

    # Normals
    a = numpy.ndarray(
        len(mesh.loops) * 3,
        dtype=numpy.float32
    )
    mesh.loops.foreach_get("normal", a)

    nlist = btoa.BtArray()
    nlist.convert_from_buffer(
        len(mesh.loops),
        'VECTOR',
        ctypes.c_void_p(a.ctypes.data)
    )

    # Polygons
    a = numpy.ndarray(
        len(mesh.polygons),
        dtype=numpy.uint32
    )
    mesh.polygons.foreach_get("loop_total", a)

    nsides = btoa.BtArray()
    nsides.convert_from_buffer(
        len(mesh.polygons),
        'UINT',
        ctypes.c_void_p(a.ctypes.data)
    )

    a = numpy.ndarray(
        len(mesh.loops),
        dtype=numpy.uint32
    )
    mesh.polygons.foreach_get("vertices", a)

    vidxs = btoa.BtArray()
    vidxs.convert_from_buffer(
        len(mesh.loops),
        'UINT',
        ctypes.c_void_p(a.ctypes.data)
    )

    a = numpy.arange(
        len(mesh.loops),
        dtype=numpy.uint32
    )
    
    nidxs = btoa.BtArray()
    nidxs.convert_from_buffer(
        len(mesh.loops),
        'UINT',
        ctypes.c_void_p(a.ctypes.data)
    )

    # Create polymesh object
    name = depsgraph_utils.get_unique_name(object_instance)
    node = btoa.BtPolymesh(name)
    node.set_matrix(
        "matrix",
        matrix_utils.flatten_matrix(object_instance.matrix_world)
    )
    node.set_bool("smoothing", True)
    node.set_array("vlist", vlist)
    node.set_array("nlist", nlist)
    node.set_array("nsides", nsides)
    node.set_array("vidxs", vidxs)
    node.set_array("nidxs", nidxs)

    # UV's
    for i, uvt in enumerate(mesh.uv_layers):
        if uvt.active_render:
            data = mesh.uv_layers[i].data
            
            a = numpy.arange(len(data), dtype=numpy.uint32)
            uvidxs = btoa.BtArray()
            uvidxs.convert_from_buffer(
                len(data),
                'UINT',
                ctypes.c_void_p(a.ctypes.data)
            )

            a = numpy.ndarray(
                len(data) * 2,
                dtype=numpy.float32
            )
            data.foreach_get("uv", a)

            uvlist = btoa.BtArray()
            uvlist.convert_from_buffer(
                len(data),
                'VECTOR2',
                ctypes.c_void_p(a.ctypes.data)
            )

            node.set_array("uvidxs", uvidxs)
            node.set_array("uvlist", uvlist)

            break

    # Materials
    # This should really be in a for loop, but for now we're only
    # looking for the material in the first slot.
    # for material in ob.data.materials:
    if len(ob.data.materials) > 0 and ob.data.materials[0] is not None:
        material = ob.data.materials[0]
        mat_unique_name = depsgraph_utils.get_unique_name(material)

        if material.arnold.node_tree is not None:
            shader_node = btoa.get_node_by_name(mat_unique_name)

            if shader_node.is_valid():
                node.set_pointer("shader", shader_node)
            else:
                surface, volume, displacement = material.arnold.node_tree.export()
                surface[0].set_string("name", material.name)

                node.set_pointer("shader", surface[0])

    return node

def create_light(object_instance):
    ob = depsgraph_utils.get_object_data_from_instance(object_instance)

    ntype = btoa.BT_LIGHT_SHAPE_CONVERSIONS[ob.data.shape] if ob.data.type == 'AREA' else btoa.BT_LIGHT_CONVERSIONS[ob.data.type]
    node = btoa.BtNode(ntype)
    sync_light(node, object_instance)

    return node

def sync_light(btnode, object_instance):
    ob = depsgraph_utils.get_object_data_from_instance(object_instance)

    data = ob.data
    arnold = data.arnold

    btnode.set_string("name", depsgraph_utils.get_unique_name(object_instance))

    # Set matrix for everything except cylinder lights
    if not hasattr(data, "shape") or data.shape != 'RECTANGLE':
        btnode.set_matrix(
            "matrix",
            matrix_utils.flatten_matrix(ob.matrix_world)
        )
    
    btnode.set_rgb("color", *data.color)
    btnode.set_float("intensity", arnold.intensity)
    btnode.set_float("exposure", arnold.exposure)
    btnode.set_int("samples", arnold.samples)
    btnode.set_bool("normalize", arnold.normalize)

    btnode.set_bool("cast_shadows", arnold.cast_shadows)
    btnode.set_bool("cast_volumetric_shadows", arnold.cast_volumetric_shadows)
    btnode.set_rgb("shadow_color", *arnold.shadow_color)
    btnode.set_float("shadow_density", arnold.shadow_density)

    btnode.set_float("camera", arnold.camera)
    btnode.set_float("diffuse", arnold.diffuse)
    btnode.set_float("specular", arnold.specular)
    btnode.set_float("transmission", arnold.transmission)
    btnode.set_float("sss", arnold.sss)
    btnode.set_float("indirect", arnold.indirect)
    btnode.set_float("volume", arnold.volume)
    btnode.set_int("max_bounces", arnold.max_bounces)

    if data.type in ('POINT', 'SPOT'):
        btnode.set_float("radius", data.shadow_soft_size)

    if data.type == 'SUN':
        btnode.set_float("angle", arnold.angle)

    if data.type == 'SPOT':
        btnode.set_float("cone_angle", math.degrees(data.spot_size))
        btnode.set_float("penumbra_angle", math.degrees(arnold.penumbra_angle))
        btnode.set_float("roundness", arnold.spot_roundness)
        btnode.set_float("aspect_ratio", arnold.aspect_ratio)
        btnode.set_float("lens_radius", arnold.lens_radius)

    if data.type == 'AREA':
        btnode.set_float("roundness", arnold.area_roundness)
        btnode.set_float("spread", arnold.spread)
        btnode.set_int("resolution", arnold.resolution)
        btnode.set_float("soft_edge", arnold.soft_edge)
        
        if data.shape == 'SQUARE':
            smatrix = mathutils.Matrix.Diagonal((
                data.size / 2,
                data.size / 2,
                data.size / 2
            )).to_4x4()
            
            tmatrix = ob.matrix_world @ smatrix
        
            btnode.set_matrix(
                "matrix",
                matrix_utils.flatten_matrix(tmatrix)
            )
        elif data.shape == 'DISK':
            s = ob.scale.x if ob.scale.x > ob.scale.y else ob.scale.y
            btnode.set_float("radius", 0.5 * data.size * s)
        elif data.shape == 'RECTANGLE':
            d = 0.5 * data.size_y * ob.scale.y
            top = matrix_utils.get_position_along_local_vector(data, d, 'Y')
            bottom = matrix_utils.get_position_along_local_vector(data, -d, 'Y')

            btnode.set_vector("top", *top)
            btnode.set_vector("bottom", *bottom)

            s = ob.scale.x if ob.scale.x > ob.scale.z else ob.scale.z
            btnode.set_float("radius", 0.5 * data.size * s)

def create_camera(object_instance):
    node = btoa.BtNode("persp_camera")
    sync_camera(node, object_instance)
    return node

def sync_camera(btnode, object_instance):
    ob = depsgraph_utils.get_object_data_from_instance(object_instance)

    data = ob.data
    arnold = data.arnold

    btnode.set_string("name", depsgraph_utils.get_unique_name(object_instance))
    btnode.set_matrix(
        "matrix",
        matrix_utils.flatten_matrix(ob.matrix_world)
    )

    fov = camera_utils.calc_horizontal_fov(ob)
    btnode.set_float("fov", math.degrees(fov))
    btnode.set_float("exposure", arnold.exposure)

    if data.dof.focus_object:
        distance = mathutils.geometry.distance_point_to_plane(
            ob.matrix_world.to_translation(),
            data.dof.focus_object.matrix_world.to_translation(),
            ob.matrix_world.col[2][:3]
        )
    else:
        distance = data.dof.focus_distance

    aperture_size = arnold.aperture_size if arnold.enable_dof else 0

    btnode.set_float("focus_distance", distance)
    btnode.set_float("aperture_size", aperture_size)
    btnode.set_int("aperture_blades", arnold.aperture_blades)
    btnode.set_float("aperture_rotation", arnold.aperture_rotation)
    btnode.set_float("aperture_blade_curvature", arnold.aperture_blade_curvature)
    btnode.set_float("aperture_aspect_ratio", arnold.aperture_aspect_ratio)

    btnode.set_float("near_clip", data.clip_start)
    btnode.set_float("far_clip", data.clip_end)

    btnode.set_float("shutter_start", arnold.shutter_start)
    btnode.set_float("shutter_end", arnold.shutter_end)
    btnode.set_string("shutter_type", arnold.shutter_type)
    btnode.set_string("rolling_shutter", arnold.rolling_shutter)
    btnode.set_float("rolling_shutter_duration", arnold.rolling_shutter_duration)
