import bpy
from dataclasses import dataclass
import numpy as np

'''
Evaluates object data for a single frame.
'''

@dataclass(init=False)
class ObjectData:
    transform: np.ndarray
    visibility: int
    is_matte: bool

    @staticmethod
    def init_from_object(ob: bpy.types.Object):
        data = ObjectData()
        data.transform = np.reshape(ob.matrix_world.transposed(), -1)

        return data