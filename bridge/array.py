from .ai_template_class import AiTemplateClass
from .constants import BTOA_TYPE_CONSTANTS
from .matrix import ArnoldMatrix

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
        if self.is_valid:
            arnold.AiArraySetStr(self.data, param, val)

    def set_array(self, i, array):
        if self.is_valid:
            arnold.AiArraySetArray(self.data, i, array.data)

    def set_byte(self, i, val):
        if self.is_valid:
            arnold.AiArraySetByte(self.data, i, val)

    def set_matrix(self, i, val):
        if self.is_valid:
            if isinstance(val, ArnoldMatrix):
                arnold.AiArraySetMtx(self.data, i, val.data)
            else:
                arnold.AiArraySetMtx(self.data, i, arnold.AtMatrix(*val))

    def set_vector(self, i, array):
        if self.is_valid:
            arnold.AiArraySetVec(self.data, i, array.data)

    def set_pointer(self, i, val):
        if self.is_valid:
            ptr = val.data if hasattr(val, "data") else val
            arnold.AiArraySetPtr(self.data, i, ptr)
            
    def get_num_keys(self):
        if not self.is_valid:
            return None
        
        return arnold.AiArrayGetNumKeys(self.data)
    
    def get_matrix(self, i):
        if not self.is_valid:
            return None

        node = ArnoldMatrix()
        node.data = arnold.AiArrayGetMtx(self.data, i)
        
        return node