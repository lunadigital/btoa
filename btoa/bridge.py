import bpy
import numpy
import math
import ctypes
import bmesh
from contextlib import contextmanager
from mathutils import geometry

from . import types

from arnold import *

AiNodeSet = {
    "STRING": lambda n, i, v: AiNodeSetStr(n, i, v),
    #'ARRAY': _AiNodeSetArray,
    "BOOL": lambda n, i, v: AiNodeSetBool(n, i, v),
    "BYTE": lambda n, i, v: AiNodeSetByte(n, i, v),
    "INT": lambda n, i, v: AiNodeSetInt(n, i, v),
    "FLOAT": lambda n, i, v: AiNodeSetFlt(n, i , v),
    "VECTOR2": lambda n, i, v: AiNodeSetVec2(n, i, *v),
    "RGB": lambda n, i, v: AiNodeSetRGB(n, i, *v),
    "RGBA": lambda n, i, v: AiNodeSetRGBA(n, i, *v),
    "VECTOR": lambda n, i, v: AiNodeSetVec(n, i, *v),
    #"MATRIX": lambda n, i, v: AiNodeSetMatrix(n, i, _AiMatrix(v))
}

def calc_horizontal_fov(camera):
    options = AiUniverseGetOptions()

    xres = AiNodeGetInt(options, "xres")
    yres = AiNodeGetInt(options, "yres")

    data = camera.data

    if data.sensor_fit == 'VERTICAL' or yres > xres:
        # https://blender.stackexchange.com/questions/23431/how-to-set-camera-horizontal-and-vertical-fov
        return 2 * math.atan((0.5 * xres) / (0.5 * yres / math.tan(data.angle / 2)))
    else:
        return data.angle

def bake_geometry(ob):
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
    mesh.calc_tangents()
                
    return mesh

def generate_aimatrix(matrix):
    return AtMatrix(*numpy.reshape(matrix.transposed(), -1))

def generate_aipolymesh(ob):
    mesh = bake_geometry(ob)
    verts = mesh.vertices
    loops = mesh.loops
    polygons = mesh.polygons
    uv_layers = mesh.uv_layers

    # Vertices
    a = numpy.ndarray(len(verts) * 3, dtype=numpy.float32)
    verts.foreach_get("co", a)
    vlist = AiArrayConvert(len(verts), 1, AI_TYPE_VECTOR, ctypes.c_void_p(a.ctypes.data))

    a = numpy.ndarray(len(loops) * 3, dtype=numpy.float32)
    loops.foreach_get("normal", a)
    nlist = AiArrayConvert(len(loops), 1, AI_TYPE_VECTOR, ctypes.c_void_p(a.ctypes.data))

    # Polygons
    a = numpy.ndarray(len(polygons), dtype=numpy.uint32)
    polygons.foreach_get("loop_total", a)
    nsides = AiArrayConvert(len(polygons), 1, AI_TYPE_UINT, ctypes.c_void_p(a.ctypes.data))

    a = numpy.ndarray(len(loops), dtype=numpy.uint32)
    polygons.foreach_get("vertices", a)
    vidxs = AiArrayConvert(len(loops), 1, AI_TYPE_UINT, ctypes.c_void_p(a.ctypes.data))

    a = numpy.arange(len(loops), dtype=numpy.uint32)
    nidxs = AiArrayConvert(len(loops), 1, AI_TYPE_UINT, ctypes.c_void_p(a.ctypes.data))

    # Create Arnold node
    node = AiNode('polymesh')
    AiNodeSetMatrix(node, "matrix", generate_aimatrix(ob.matrix_world))
    AiNodeSetBool(node, "smoothing", True)
    AiNodeSetArray(node, "vlist", vlist)
    AiNodeSetArray(node, "nlist", nlist)
    AiNodeSetArray(node, "nsides", nsides)
    AiNodeSetArray(node, "vidxs", vidxs)
    AiNodeSetArray(node, "nidxs", nidxs)

    # UV's    
    for i, uvt in enumerate(uv_layers):
        if uvt.active_render:
            uvd = uv_layers[i].data
            nuvs = len(uvd)

            a = numpy.arange(nuvs, dtype=numpy.uint32)
            uvidxs = AiArrayConvert(nuvs, 1, AI_TYPE_UINT, ctypes.c_void_p(a.ctypes.data))

            a = numpy.ndarray(nuvs*2, dtype=numpy.float32)
            uvd.foreach_get("uv", a)

            uvlist = AiArrayConvert(nuvs, 1, AI_TYPE_VECTOR2, ctypes.c_void_p(a.ctypes.data))

            AiNodeSetArray(node, "uvidxs", uvidxs)
            AiNodeSetArray(node, "uvlist", uvlist)
            break

    return node

def generate_aicamera(camera, depsgraph):
    node = AiNode("persp_camera")
    sync_cameras(node, camera, depsgraph)    
    return node

def sync_cameras(ainode, camera, depsgraph):
    ob_eval = camera.evaluated_get(depsgraph)
    data = ob_eval.data

    # Basic stuff
    AiNodeSetStr(ainode, "name", ob_eval.name)
    AiNodeSetMatrix(ainode, "matrix", generate_aimatrix(ob_eval.matrix_world))
    
    # Lens data
    fov = calc_horizontal_fov(ob_eval)
    AiNodeSetFlt(ainode, "fov", math.degrees(fov))
    AiNodeSetFlt(ainode, "exposure", data.arnold.exposure)

    # DOF
    if data.dof.focus_object:
        distance = geometry.distance_point_to_plane(
            ob_eval.matrix_world.to_translation(),
            data.dof_object.matrix_world.to_translation(),
            ob_eval.matrix_world.col[2][:3]
        )
    else:
        distance = data.dof.focus_distance

    AiNodeSetFlt(ainode, "aperture_size", data.arnold.aperture_size)
    AiNodeSetInt(ainode, "aperture_blades", data.arnold.aperture_blades)
    AiNodeSetFlt(ainode, "aperture_rotation", data.arnold.aperture_rotation)
    AiNodeSetFlt(ainode, "aperture_blade_curvature", data.arnold.aperture_blade_curvature)
    AiNodeSetFlt(ainode, "aperture_aspect_ratio", data.arnold.aperture_aspect_ratio)

    # Clipping
    AiNodeSetFlt(ainode, "near_clip", data.clip_start)
    AiNodeSetFlt(ainode, "far_clip", data.clip_end)

    # Shutter
    AiNodeSetFlt(ainode, "shutter_start", data.arnold.shutter_start)
    AiNodeSetFlt(ainode, "shutter_end", data.arnold.shutter_end)
    AiNodeSetStr(ainode, "shutter_type", data.arnold.shutter_type)
    AiNodeSetStr(ainode, "rolling_shutter", data.arnold.rolling_shutter)
    AiNodeSetFlt(ainode, "rolling_shutter_duration", data.arnold.rolling_shutter_duration)

def generate_ailight(light):
    if light.data.type == 'AREA':
        node = AiNode(types.AI_AREALIGHT_TYPE[light.data.shape])
    else:
        node = AiNode(types.AI_LIGHT_TYPE[light.data.type])
    
    sync_light(node, light)
    return node

def sync_light(ainode, light):
    data = light.data
    _type = types.AI_LIGHT_TYPE[data.type]

    # Common properties
    AiNodeSetStr(ainode, "name", light.name)
    AiNodeSetMatrix(ainode, "matrix", generate_aimatrix(light.matrix_world))

    AiNodeSetRGB(ainode, "color", *data.color)
    AiNodeSetFlt(ainode, "intensity", data.arnold.intensity)
    AiNodeSetFlt(ainode, "exposure", data.arnold.exposure)
    AiNodeSetInt(ainode, "samples", data.arnold.samples)
    AiNodeSetBool(ainode, "normalize", data.arnold.normalize)

    AiNodeSetBool(ainode, "cast_shadows", data.arnold.cast_shadows)
    AiNodeSetBool(ainode, "cast_volumetric_shadows", data.arnold.cast_volumetric_shadows)
    AiNodeSetFlt(ainode, "shadow_density", data.arnold.shadow_density)
    # shadow_color

    # Light data
    if _type in ('point_light', 'spot_light'):
        AiNodeSetFlt(ainode, "radius", data.shadow_soft_size)
    
    if _type == 'distant_light':
        AiNodeSetFlt(ainode, "angle", data.arnold.angle)

    if _type == 'spot_light':
        AiNodeSetFlt(ainode, "roundness", data.arnold.spot_roundness)
        AiNodeSetFlt(ainode, "aspect_ratio", data.arnold.aspect_ratio)
        AiNodeSetFlt(ainode, "lens_radius", data.arnold.lens_radius)

    if _type == 'area_light':
        AiNodeSetFlt(ainode, "roundness", data.arnold.area_roundness)
        AiNodeSetFlt(ainode, "spread", data.arnold.spread)
        AiNodeSetInt(ainode, "resolution", data.arnold.resolution)
        AiNodeSetFlt(ainode, "soft_edge", data.arnold.soft_edge)