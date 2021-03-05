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

    def convert_from_buffer(self, length, type_string, data):
        self._data = arnold.AiArrayConvert(
            length,
            1,
            constants.BT_TYPE_CONSTANTS[type_string],
            data
        )

    def set_string(self, param, val):
        if self.is_valid():
            arnold.AiArraySetStr(self._data, param, val)

    def set_matrix(self, i, val):
        if self.is_valid():
            arnold.AiArraySetMtx(self._data, i, arnold.AtMatrix(*val))