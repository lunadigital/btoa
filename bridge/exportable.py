import bpy
import math
import numpy

from .array import ArnoldArray
from .node import ArnoldNode
from . import utils as bridge_utils

class ArnoldNodeExportable(ArnoldNode):
    def __init__(self, ndata=None, frame_set=None):
        # `data` can either be an Arnold node type (type string)
        # or a BtoA node (type ArnoldNode). If it's a string,
        # we'll create a new node of that type; if it's a 
        # BtoA node, we'll sync all new data with the
        # existing node.
        if isinstance(ndata, str):
            super().__init__(ndata)
        elif isinstance(ndata, ArnoldNode):
            self.set_data(ndata.data)
        else:
            super().__init__()

        self.depsgraph = None
        self.parent = None
        self.is_instance = False
        self.datablock = None
        self.frame_set = frame_set

    def __get_matrix(self):
        return self.parent.matrix_world if self.is_instance else self.datablock.matrix_world

    def evaluate_datablock(self, datablock):
        if isinstance(datablock, bpy.types.DepsgraphObjectInstance):
            self.datablock = bridge_utils.get_object_data_from_instance(datablock)
        elif isinstance(datablock, bpy.types.DepsgraphUpdate):
            self.datablock = datablock.id
        else:
            self.datablock = datablock

        if hasattr(datablock, "parent"):
            self.parent = datablock.parent

        if hasattr(datablock, "is_instance"):
            self.is_instance = datablock.is_instance

    def get_blur_matrices(self):
        sdata = self.depsgraph.scene.arnold
        frame_current = self.depsgraph.scene.frame_current

        steps = numpy.linspace(sdata.shutter_start, sdata.shutter_end, sdata.motion_keys)

        m_array = ArnoldArray()
        m_array.allocate(1, sdata.motion_keys, 'MATRIX')

        for i in range(0, steps.size):
            frame, subframe = self.get_target_frame(frame_current, steps[i])
            self.frame_set(frame, subframe=subframe)

            matrix = bridge_utils.flatten_matrix(self.__get_matrix())
            m_array.set_matrix(i, matrix)
        
        self.frame_set(frame_current, subframe=0)

        return m_array

    def get_target_frame(self, frame_current, step):
        frame_flt = frame_current + step
        frame_int = math.floor(frame_flt)
        subframe = frame_flt - frame_int

        return frame_int, subframe
    
    def get_transform_matrix(self):
        sdata = self.depsgraph.scene.arnold
        matrix = bridge_utils.flatten_matrix(self.__get_matrix())

        return self.get_blur_matrices() if sdata.enable_motion_blur else matrix