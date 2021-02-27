import arnold

from .bttemplate import BtTemplate

class BtNode(BtTemplate):
    def __init__(self, node_type=None):
        super().__init__()

        if node_type is not None:
            self._data = arnold.AiNode(node_type)

    def type_is(self, node_type):
        return arnold.AiNodeIs(self._data, node_type)

    def link(self, param, val):
        if self.is_valid():
            arnold.AiNodeLink(self._data, param, val._get_data())
    
    def set_byte(self, param, val):
        if self.is_valid():
            arnold.AiSetByte(self._data, param, val)

    def set_int(self, param, val):
        if self.is_valid():
            arnold.AiNodeSetInt(self._data, param, val)

    def set_uint(self, param, val):
        if self.is_valid():
            arnold.AiNodeSetUInt(self._data, param, val)

    def set_bool(self, param, val):
        if self.is_valid():
            arnold.AiNodeSetBool(self._data, param, val)

    def set_float(self, param, val):
        if self.is_valid():
            arnold.AiNodeSetFlt(self._data, param, val)

    def set_pointer(self, param, val):
        if self.is_valid():
            ptr = val._get_data() if hasattr(val, "_get_data") else val
            arnold.AiNodeSetPtr(self._data, param, ptr)

    def set_array(self, param, btarray):
        if self.is_valid():
            arnold.AiNodeSetArray(self._data, param, btarray._get_data())

    def set_matrix(self, param, val):
        if self.is_valid():
            arnold.AiNodeSetMatrix(self._data, param, arnold.AtMatrix(*val))

    def set_string(self, param, val):
        if self.is_valid():
            arnold.AiNodeSetStr(self._data, param, val)

    def set_rgb(self, param, r, g, b):
        if self.is_valid():
            arnold.AiNodeSetRGB(self._data, param, r, g, b)

    def set_rgba(self, param, r, g, b, a):
        if self.is_valid():
            arnold.AiNodeSetRGBA(self._data, param, r, g, b, a)
    
    def set_vector(self, param, x, y, z):
        if self.is_valid():
            arnold.AiNodeSetVec(self._data, param, x, y, z)

    def set_vector2(self, param, x, y):
        if self.is_valid():
            arnold.AiNodeSetVec2(self._data, param, x, y)

    def get_int(self, param):
        if not self.is_valid():
            return None
            
        return arnold.AiNodeGetInt(self._data, "xres")