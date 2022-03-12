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

def get_unique_name(datablock):
    db = datablock

    if isinstance(datablock, bpy.types.DepsgraphObjectInstance):
        db = datablock.instance_object

    if hasattr(db, "data"):
        if isinstance(db.data, bpy.types.Light):
            t = db.data.type
            n = db.data.name
        else:
            t = db.type
            n = db.name
    elif isinstance(db, bpy.types.Material):
        t = db.arnold.node_tree.type
        n = db.arnold.node_tree.name
        _type = db.type
    elif isinstance(db, (bpy.types.Material, bpy.types.World)):
        _type = db.arnold.node_tree.type

    return "{}_{}".format(_type, db.name)

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
    DEFAULT_SENSOR_WIDTH = 36

    region_3d = space_data.region_3d
    
    options = UniverseOptions()
    width, height = options.get_int("xres"), options.get_int("yres")

    camera = BlenderCamera()
    camera.name = "BTOA_VIEWPORT_CAMERA"

    view_matrix = region_3d.view_matrix.inverted()
    camera.matrix_world = view_matrix

    # FOV
    sensor_width = DEFAULT_SENSOR_WIDTH
    lens = space_data.lens

    if region_3d.view_perspective == 'CAMERA':
        sensor_width = space_data.camera.data.sensor_width
        lens = space_data.camera.data.lens

        camera.data.is_render_view = True

    camera.data.angle = 2 * math.atan(sensor_width / lens)

    # Clipping
    camera.data.clip_start = space_data.clip_start
    camera.data.clip_end = space_data.clip_end

    camera.data.view_camera_zoom = region_3d.view_camera_zoom
    camera.data.view_camera_offset = region_3d.view_camera_offset

    if region_3d.view_perspective == 'ORTHO':
        camera.data.arnold.camera_type = "ortho_camera"

        if height > width:
            # This was just a lucky guess, I'm not entirely sure why this works
            sensor = DEFAULT_SENSOR_WIDTH * (width / height)
        else:
            sensor = DEFAULT_SENSOR_WIDTH

        camera.data.ortho_scale = 2 * region_3d.view_distance * sensor / space_data.lens

    return camera

def get_parent_material_from_nodetree(ntree):
    for mat in bpy.data.materials:
        if mat.arnold.node_tree and mat.arnold.node_tree.name == ntree.name:
            return mat