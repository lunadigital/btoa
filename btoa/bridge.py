import bpy
import numpy
import math
import ctypes
from contextlib import contextmanager
from mathutils import geometry

from . import types

from arnold import *

AiNodeSet = {
    "STRING": lambda n, i, v: arnold.AiNodeSetStr(n, i, v),
    #'ARRAY': _AiNodeSetArray,
    "BOOL": lambda n, i, v: arnold.AiNodeSetBool(n, i, v),
    "BYTE": lambda n, i, v: arnold.AiNodeSetByte(n, i, v),
    "INT": lambda n, i, v: arnold.AiNodeSetInt(n, i, v),
    "FLOAT": lambda n, i, v: arnold.AiNodeSetFlt(n, i , v),
    "VECTOR2": lambda n, i, v: arnold.AiNodeSetVec2(n, i, *v),
    "RGB": lambda n, i, v: arnold.AiNodeSetRGB(n, i, *v),
    "RGBA": lambda n, i, v: arnold.AiNodeSetRGBA(n, i, *v),
    "VECTOR": lambda n, i, v: arnold.AiNodeSetVec(n, i, *v),
    "MATRIX": lambda n, i, v: arnold.AiNodeSetMatrix(n, i, _AiMatrix(v))
}

def calc_sensor_size(camera):
    options = AiUniverseGetOptions()

    xres = AiNodeGetInt(options, "xres")
    yres = AiNodeGetInt(options, "yres")
    aspect_x = bpy.context.scene.render.pixel_aspect_x
    aspect_y = bpy.context.scene.render.pixel_aspect_y

    data = camera.data

    result = None

    if data.sensor_fit == 'VERTICAL':
        result = data.sensor_height * xres / yres * aspect_x / aspect_y
    else:
        result = data.sensor_width
        if data.sensor_fit == 'AUTO':
            x = xres * aspect_x
            y = xres * aspect_y
            if x < y:
                result *= x / y

    return result 

@contextmanager
def bake_geometry(depsgraph, bmesh):
    # Refer to _Mesh() in engine/__init__.py, line 630
    pass

def generate_aimatrix(matrix):
    return AtMatrix(*numpy.reshape(matrix.transposed(), -1))

def generate_aipolymesh(mesh):
    verts = mesh.data.vertices
    loops = mesh.data.loops
    polygons = mesh.data.polygons

    # Vertices
    a = numpy.ndarray(len(verts) * 3, dtype=numpy.float32)
    verts.foreach_get("co", a)
    vlist = AiArrayConvert(len(verts), 1, AI_TYPE_VECTOR, ctypes.c_void_p(a.ctypes.data))

    # Normals
    mesh.data.calc_tangents()

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
    AiNodeSetMatrix(node, "matrix", generate_aimatrix(mesh.matrix_world))
    AiNodeSetBool(node, "smoothing", True)
    AiNodeSetArray(node, "vlist", vlist)
    AiNodeSetArray(node, "nlist", nlist)
    AiNodeSetArray(node, "nsides", nsides)
    AiNodeSetArray(node, "vidxs", vidxs)
    AiNodeSetArray(node, "nidxs", nidxs)

    return node

def generate_aicamera(camera):
    node = AiNode("persp_camera")
    sync_cameras(node, camera)    
    return node

def sync_cameras(ainode, camera):
    data = camera.data

    # Basic stuff
    AiNodeSetStr(ainode, "name", camera.name)
    AiNodeSetMatrix(ainode, "matrix", generate_aimatrix(camera.matrix_world))
    
    # Lens data
    AiNodeSetFlt(ainode, "fov", math.degrees(data.angle))
    AiNodeSetFlt(ainode, "exposure", data.arnold.exposure)

    # DOF
    if data.dof.focus_object:
        distance = geometry.distance_point_to_plane(
            camera.matrix_world.to_translation(),
            data.dof_object.matrix_world.to_translation(),
            camera.matrix_world.col[2][:3]
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
    node = AiNode(types.AI_LIGHT_TYPE[light.data.type])
    sync_light(node, light)
    return node

def sync_light(ainode, light):
    data = light.data
    _type = types.AI_LIGHT_TYPE[data.type]

    # Common properties
    AiNodeSetStr(ainode, "name", light.name)
    AiNodeSetMatrix(ainode, "matrix", generate_aimatrix(light.matrix_world))

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
        AiNodeSetFlt(ainode, "radius", data.arnold.radius)
    
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