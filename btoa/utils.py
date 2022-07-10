import bpy
import bmesh
import math
import mathutils
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
    elif isinstance(db, (bpy.types.Material, bpy.types.World)):
        t = "SHADER"
        n = db.arnold.node_tree.name

        # For backwards compatibility with previous BtoA versions that
        # don't use UUIDs in the node tree name
        if len(db.arnold.node_tree.name.split("_")) == 2:
            n = "{}_{}".format(db.arnold.node_tree.name, db.name)

    return "{}_{}".format(t, n)

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

def get_viewport_camera_object(context):
    DEFAULT_SENSOR_WIDTH = 36.0
    ratio = context.region.width / context.region.height

    camera = BlenderCamera()
    camera.name = "BTOA_VIEWPORT_CAMERA"

    camera.matrix_world = context.region_data.view_matrix.inverted()
    camera.data.clip_start = context.space_data.clip_start
    camera.data.clip_end = context.space_data.clip_end

    sensor_width = context.space_data.camera.data.sensor_width if context.region_data.view_perspective == 'CAMERA' else DEFAULT_SENSOR_WIDTH
    lens = context.space_data.camera.data.lens if context.region_data.view_perspective == 'CAMERA' else context.space_data.lens
    camera.data.angle = 2 * math.atan(sensor_width / lens)

    if context.region_data.view_perspective == 'CAMERA':
        camera.data.arnold.camera_type = context.space_data.camera.data.arnold.camera_type
        camera.data.is_render_view = True

        camera.data.zoom = 2.0 / (2.0 ** 0.5 + context.region_data.view_camera_zoom / 50.0) ** 2
        camera.data.offset = (
            context.region_data.view_camera_offset[0] * 2,
            context.region_data.view_camera_offset[1] * 2
            )

        if camera.data.arnold.camera_type == 'ortho_camera':
            camera.data.ortho_scale = context.space_data.camera.data.ortho_scale
    elif context.region_data.view_perspective == 'ORTHO':
        camera.data.arnold.camera_type = "ortho_camera"

        sensor = sensor_width * ratio if ratio < 1.0 else DEFAULT_SENSOR_WIDTH
        camera.data.ortho_scale = context.region_data.view_distance * sensor / lens

        '''
        By default an orthographic viewport camera is VERY close to the origin of the
        scene, which causes clipping. We're going to manually move it back 100 units
        along the local Z (forward/backward) axis to avoid this.
        '''
        camera.matrix_world @= mathutils.Matrix.Translation((0.0, 0.0, 100.0))

    return camera

def get_parent_material_from_nodetree(ntree):
    for mat in bpy.data.materials:
        if mat.arnold.node_tree and mat.arnold.node_tree.name == ntree.name:
            return mat