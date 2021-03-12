import arnold

from .bttemplate import BtTemplate
from . import constants

class BtArray(BtTemplate):
    def allocate(self, nelements, nkeys, type_string):
        self._data = arnold.AiArrayAllocate(
            nelements,
            nkeys,
            constants.BT_TYPE_CONSTANTS[type_string]
        )

    def convert_from_buffer(self, length, keys, type_string, data):
        self._data = arnold.AiArrayConvert(
            length,
            keys,
            constants.BT_TYPE_CONSTANTS[type_string],
            data
        )

    def set_string(self, param, val):
        if self.is_valid():
            arnold.AiArraySetStr(self._data, param, val)

    def set_array(self, i, btarray):
        if self.is_valid():
            arnold.AiArraySetArray(self._data, i, btarray._data)

    def set_matrix(self, i, val):
        if self.is_valid():
            arnold.AiArraySetMtx(self._data, i, arnold.AtMatrix(*val))

    def set_vector(self, i, btarray):
        if self.is_valid():
            arnold.AiArraySetVec(self._data, i, btarray._data)