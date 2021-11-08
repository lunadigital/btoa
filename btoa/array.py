from .ai_template_class import AiTemplateClass
from .constants import BTOA_TYPE_CONSTANTS

import arnold

class ArnoldArray(AiTemplateClass):
    def allocate(self, nelements, nkeys, type_string):
        self.data = arnold.AiArrayAllocate(
            nelements,
            nkeys,
            BTOA_TYPE_CONSTANTS[type_string]
        )

    def convert_from_buffer(self, length, keys, type_string, data):
        self.data = arnold.AiArrayConvert(
            length,
            keys,
            BTOA_TYPE_CONSTANTS[type_string],
            data
        )

    def set_string(self, param, val):
        if self.is_valid():
            arnold.AiArraySetStr(self.data, param, val)

    def set_array(self, i, array):
        if self.is_valid():
            arnold.AiArraySetArray(self.data, i, array.data)

    def set_matrix(self, i, val):
        if self.is_valid():
            arnold.AiArraySetMtx(self.data, i, arnold.AtMatrix(*val))

    def set_vector(self, i, array):
        if self.is_valid():
            arnold.AiArraySetVec(self.data, i, array.data)

    def set_pointer(self, i, val):
        if self.is_valid():
            ptr = val.data if hasattr(val, "data") else val
            arnold.AiArraySetPtr(self.data, i, ptr)