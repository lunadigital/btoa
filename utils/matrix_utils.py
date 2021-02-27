import numpy

def flatten_matrix(matrix):
    return numpy.reshape(matrix.transposed(), -1)

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