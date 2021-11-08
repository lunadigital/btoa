import bpy
import mathutils

from .camera_data import BlenderCameraData

class BlenderCamera:
    '''
    This is a dummy class that mimics internal Blender camera classes so we
    can easily sync and update viewport camera data during IPR rendering.
    '''

    def __init__(self):
        self.name = ""
        self.matrix_world = mathutils.Matrix.Identity(4)
        self.type = 'CAMERA'
        self.data = BlenderCameraData()
        self.library = None