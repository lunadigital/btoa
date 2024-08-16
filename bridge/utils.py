import bpy
import bmesh
import math
import mathutils
import numpy

from arnold import *
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix

from .node import ArnoldNode
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

def get_render_resolution(scene, context=None):
    if context:
        region = context.region

        x = int(region.width * float(scene.arnold.viewport_scale))
        y = int(region.height * float(scene.arnold.viewport_scale))
    else:
        render = scene.render
        scale = render.resolution_percentage / 100

        x = int(render.resolution_x * scale)
        y = int(render.resolution_y * scale)

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
        camera.data.arnold.exposure = context.space_data.camera.data.arnold.exposure
        camera.data.is_render_view = True

        camera.data.zoom = 4.0 / ((math.sqrt(2) + context.region_data.view_camera_zoom / 50.0) ** 2)
        camera.data.offset = (
            context.region_data.view_camera_offset[0] * 2,
            context.region_data.view_camera_offset[1] * 2
            )

        if camera.data.arnold.camera_type == 'ortho_camera':
            camera.data.ortho_scale = context.space_data.camera.data.ortho_scale
    elif context.region_data.view_perspective == 'ORTHO':
        camera.data.arnold.camera_type = "ortho_camera"

        sensor = sensor_width * ratio if ratio < 1.0 else DEFAULT_SENSOR_WIDTH
        camera.data.ortho_scale = 2.0 * context.region_data.view_distance * sensor / lens

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

def get_node_by_name(name):
    ainode = AiNodeLookUpByName(None, name)

    node = ArnoldNode()
    node.set_data(ainode)

    return node

def get_all_by_uuid(uuid):
    iterator = AiUniverseGetNodeIterator(None, AI_NODE_SHAPE | AI_NODE_LIGHT | AI_NODE_SHADER)
    result = []

    while not AiNodeIteratorFinished(iterator):
        ainode = AiNodeIteratorGetNext(iterator)
        
        if AiNodeGetStr(ainode, 'btoa_id') == uuid:
            node = ArnoldNode()
            node.set_data(ainode)
            result.append(node)
    
    return result

def get_node_by_uuid(uuid):
    iterator = AiUniverseGetNodeIterator(None, AI_NODE_SHAPE | AI_NODE_LIGHT | AI_NODE_SHADER)
    node = ArnoldNode()

    while not AiNodeIteratorFinished(iterator):
        ainode = AiNodeIteratorGetNext(iterator)
        btoa_id = AiNodeGetStr(ainode, 'btoa_id')
        
        if btoa_id == uuid:
            node.set_data(ainode)
            break
    
    return node