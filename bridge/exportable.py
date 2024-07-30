import math
import numpy

from .array import ArnoldArray
from .node import ArnoldNode
from . import utils as bridge_utils

class ArnoldNodeExportable(ArnoldNode):
    def __init__(self, node_type=None):
        super().__init__(node_type)
        self.depsgraph = None
        self.datablock = None

    def get_blur_matrices(self, depsgraph, datablock):
        sdata = depsgraph.scene.arnold
        frame_current = depsgraph.scene.frame_current
        frame_set = depsgraph.scene.frame_set

        steps = numpy.linspace(sdata.shutter_start, sdata.shutter_end, sdata.motion_keys)

        m_array = ArnoldArray()
        m_array.allocate(1, sdata.motion_keys, 'MATRIX')

        for i in range(0, steps.size):
            frame, subframe = self.get_target_frame(steps[i])
            frame_set(frame, subframe=subframe)

            matrix = bridge_utils.flatten_matrix(datablock.matrix_world)
            m_array.set_matrix(i, matrix)
        
        frame_set(frame_current, subframe=0)

        return m_array

    def get_target_frame(self, step):
        frame_flt = self.frame_current + step
        frame_int = math.floor(frame_flt)
        subframe = frame_flt - frame_int

        return frame_int, subframe
    
    def get_transform_matrix(self, depsgraph, datablock):
        sdata = depsgraph.scene.arnold
        matrix = bridge_utils.flatten_matrix(datablock.matrix_world)

        return self.get_blur_matrices() if sdata.enable_motion_blur else matrix