import bpy
import numpy
import math
import ctypes
from contextlib import contextmanager
from mathutils import geometry

from . import types

from arnold import *

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
    AiNodeSetBool(node, "smoothing", True) # THIS SHOULD PULL FROM BLENDER'S SETTINGS
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
    AiNodeSetBool(ainode, "enable_dof", data.arnold.enable_dof)

    if data.dof.focus_object:
        distance = geometry.distance_point_to_plane(
            camera.matrix_world.to_translation(),
            data.dof_object.matrix_world.to_translation(),
            camera.matrix_world.col[2][:3]
        )
    else:
        distance = data.dof.focus_distance

    AiNodeSetFlt(ainode, "aperture_size", data.arnold.aperture_size)
    AiNodeSetFlt(ainode, "aperture_blades", data.arnold.aperture_blades)
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

