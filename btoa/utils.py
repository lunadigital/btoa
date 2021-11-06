import bpy
import bmesh
import math
import numpy
from bpy_extras import view3d_utils

from mathutils import Vector, Matrix

from .universe_options import UniverseOptions
from .bl_intern import BlenderCamera

def calc_horizontal_fov(ob):
    data = ob.data

    options = UniverseOptions()
    xres = options.get_int("xres")
    yres = options.get_int("yres")

    if data.sensor_fit == 'VERTICAL' or yres > xres:
        # https://blender.stackexchange.com/questions/23431/how-to-set-camera-horizontal-and-vertical-fov
        return 2 * math.atan((0.5 * xres) / (0.5 * yres / math.tan(data.angle / 2)))
    else:
        return data.angle

def flatten_matrix(matrix):
    return numpy.reshape(matrix.transposed(), -1)

def get_object_data_from_instance(object_instance):
    return object_instance.instance_object if object_instance.is_instance else object_instance.object

def get_position_along_local_vector(ob, distance, axis):
    # Determine movement vector
    if axis == 'X':
        mv = Vector([distance, 0, 0])
    elif axis == 'Y':
        mv = Vector([0, distance, 0])
    elif axis == 'Z':
        mv = Vector([0, 0, distance])
    
    # Construct rotation matrix
    rot = ob.matrix_world.to_euler()
    rx = Matrix.Rotation(rot.x, 4, 'X')
    ry = Matrix.Rotation(rot.y, 4, 'Y')
    rz = Matrix.Rotation(rot.z, 4, 'Z')
    rot_matrix = rx @ ry @ rz

    # Rotate movement vector by rotation matrix
    rotated_vector = rot_matrix @ mv

    # Create and apply transformation matrix
    translation_matrix = Matrix.Translation(rotated_vector)

    result = translation_matrix @ ob.matrix_world
    return result.to_translation()

'''
TODO: This is a righteous mess and needs to be cleaned up.
'''
def get_unique_name(datablock):
    prefix = ""
    name = ""

    if hasattr(datablock, "is_instance"):
        if datablock.is_instance:
            prefix = datablock.parent.name + "_"
        
        ob = get_object_data_from_instance(datablock)
        name = ob.name + "_MESH"

    elif hasattr(datablock, "data") and isinstance(datablock.data, bpy.types.Mesh):
        name = datablock.name + "_MESH"

    else:
        # Assume it's a material
        if datablock.library:
            prefix = datablock.library.name + "_"
        
        name = datablock.name + "_MATERIAL"

    return prefix + name

def get_render_resolution(session_cache, interactive=False):
    if interactive:
        region = session_cache.region

        x = region["width"]
        y = region["height"]
    else:
        render = session_cache.render
        scale = render["resolution_percentage"] / 100

        x = int(render["resolution_x"] * scale)
        y = int(render["resolution_y"] * scale)

    return x, y

def get_viewport_camera_object(space_data):
    region_3d = space_data.region_3d
    options = UniverseOptions()

    camera = BlenderCamera()

    camera.name = "BTOA_VIEWPORT_CAMERA"

    view_matrix = region_3d.view_matrix.inverted()
    camera.matrix_world = view_matrix

    fov = 2 * math.atan(36 / space_data.lens)
    camera.data.angle = fov

    camera.data.clip_start = space_data.clip_start
    camera.data.clip_end = space_data.clip_end

    return camera