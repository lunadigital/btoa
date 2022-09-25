from .ai_template_class import AiTemplateClass
from .array import ArnoldArray
from .matrix import ArnoldMatrix

import arnold

class ArnoldNode(AiTemplateClass):
    def __init__(self, node_type=None):
        super().__init__()
        self.is_instance = False

        if node_type is not None:
            self.data = arnold.AiNode(node_type)

    def type_is(self, node_type):
        return arnold.AiNodeIs(self.data, node_type)

    def link(self, param, val, output_type):
        if self.is_valid:
            arnold.AiNodeLinkOutput(self.data, output_type, val.data, param)

    def declare(self, param, param_type):
        if self.is_valid:
            arnold.AiNodeDeclare(self.data, param, param_type)

    def destroy(self):
        if self.is_valid:
            arnold.AiNodeDestroy(self.data)
            self.data = None

    # Sets UUID to track nodes during render session.
    # Not an internal Arnold parameter, we need to
    # create it ourselves.
    def set_uuid(self, uuid):
        if self.is_valid:
            self.declare("btoa_id", "constant STRING")
            self.set_string("btoa_id", uuid)
    
    def set_byte(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetByte(self.data, param, val)

    def set_int(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetInt(self.data, param, val)

    def set_uint(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetUInt(self.data, param, val)

    def set_bool(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetBool(self.data, param, val)

    def set_float(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetFlt(self.data, param, val)

    def set_pointer(self, param, val):
        if self.is_valid:
            ptr = val.data if hasattr(val, "data") else val
            arnold.AiNodeSetPtr(self.data, param, ptr)

    def set_array(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetArray(self.data, param, val.data)

    def set_matrix(self, param, val):
        if self.is_valid:
            if isinstance(val, ArnoldMatrix):
                arnold.AiNodeSetMatrix(self.data, param, val.data)
            else:
                arnold.AiNodeSetMatrix(self.data, param, arnold.AtMatrix(*val))

    def set_string(self, param, val):
        if self.is_valid:
            arnold.AiNodeSetStr(self.data, param, val)

    def set_rgb(self, param, r, g, b):
        if self.is_valid:
            arnold.AiNodeSetRGB(self.data, param, r, g, b)

    def set_rgba(self, param, r, g, b, a):
        if self.is_valid:
            arnold.AiNodeSetRGBA(self.data, param, r, g, b, a)
    
    def set_vector(self, param, x, y, z):
        if self.is_valid:
            arnold.AiNodeSetVec(self.data, param, x, y, z)

    def set_vector2(self, param, x, y):
        if self.is_valid:
            arnold.AiNodeSetVec2(self.data, param, x, y)

    def get_int(self, param):
        if not self.is_valid:
            return None
            
        return arnold.AiNodeGetInt(self.data, param)

    def get_array(self, param, copy=False):
        if not self.is_valid:
            return None

        ainode = arnold.AiNodeGetArray(self.data, param)

        if copy:
            ainode = arnold.AiArrayCopy(ainode)

        node = ArnoldArray()
        node.data = ainode

        return node

    def get_bool(self, param):
        if not self.is_valid:
            return None
        
        return arnold.AiNodeGetBool(self.data, param)

    def get_byte(self, param):
        if not self.is_valid:
            return None

        return arnold.AiNodeGetByte(self.data, param)

    def get_link(self, param, comp=None):
        if not self.is_valid:
            return None

        node = ArnoldNode()
        node.data = arnold.AiNodeGetLink(self.data, param, comp)
        return node

    def get_matrix(self, param):
        if not self.is_valid:
            return None
        
        data = arnold.AiNodeGetMatrix(self.data, param)
        node = ArnoldMatrix()
        node.data = data # We pass the data directly because it's already an AtMatrix object

        return node