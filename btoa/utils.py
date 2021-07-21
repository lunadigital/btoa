import bmesh
import math
import numpy

from mathutils import Vector, Matrix

from .universe_options import UniverseOptions

def bake_mesh(ob):
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

def get_unique_name(object_instance):
    prefix = ""
    name = ""

    if hasattr(object_instance, "is_instance"):
        if object_instance.is_instance:
            prefix = object_instance.parent.name + "_"
        
        ob = get_object_data_from_instance(object_instance)
        name = ob.name + "_MESH"
    else: # assume it's a material
        if object_instance.library:
            prefix = object_instance.library.name + "_"
        
        name = object_instance.name + "_MATERIAL"

    return prefix + name

def get_render_resolution(scene):
    render = scene.render
    scale = render.resolution_percentage / 100

    x = int(render.resolution_x * scale)
    y = int(render.resolution_y * scale)

    return x, y