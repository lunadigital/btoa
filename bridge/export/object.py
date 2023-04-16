import arnold
import bpy
from dataclasses import dataclass
import numpy as np

'''
Evaluates object data for a single frame.
'''

@dataclass(init=False)
class ObjectData:
    transform: np.ndarray
    #visibility: int
    #is_matte: bool

    @staticmethod
    def init_from_object(ob: bpy.types.Object):
        data = ObjectData()
        data.transform = np.reshape(ob.matrix_world.transposed(), -1)

        return data
    
    @staticmethod
    def to_arnold(node: arnold.AiNode, steps: list, keys: int, ):
        m_array = arnold.AiArrayAllocate(1, keys, arnold.AI_TYPE_MATRIX)
        
        for i, mtx in enumerate([ob.transform for ob in steps]):
            arnold.AiArraySetMtx(m_array, i, arnold.AtMatrix(*mtx))

        arnold.AiNodeSetArray(node, 'matrix', m_array)