import arnold

class Node:
    def __init__(self, name):
        self.__data = arnold.AiNode(name)

    def __get__(self, instance, owner):
        if self.__data is None:
            return None
            
        return self
    
    def set_byte(self, param, val):
        if self.__data is not None:
            arnold.AiSetByte(self.__data, param, val)

    def set_int(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetInt(self.__data, param, val)

    def set_uint(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetUInt(self.__data, param, val)

    def set_bool(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetBool(self.__data, param, val)

    def set_float(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetFlt(self.__data, param, val)

    def set_pointer(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetPtr(self.__data, param, val.get_data())

    def set_matrix(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetMatrix(self.__data, param, arnold.AiMatrix(*val))

    def set_string(self, param, val):
        if self.__data is not None:
            arnold.AiNodeSetStr(self.__data, param, val)

    def set_rgb(self, param, r, g, b):
        if self.__data is not None:
            arnold.AiNodeSetRGB(self.__data, param, r, g, b)

    def set_rgba(self, param, r, g, b, a):
        if self.__data is not None:
            arnold.AiNodeSetRGBA(self.__data, param, r, g, b, a)
    
    def set_vector(self, param, x, y, z):
        if self.__data is not None:
            arnold.AiNodeSetVec(self.__data, param, x, y, z)

    def set_vector2(self, param, x, y):
        if self.__data is not None:
            arnold.AiNodeSetVec2(self.__data, param, x, y)

    def set_data(data):
        '''
        For GPL compliance, this should ONLY be called
        from within the BTOA module and shouldn't be
        considered a public method.
        '''
        self.__data = data

    def get_data():
        '''
        For GPL compliance, this should ONLY be called
        from within the BTOA module and shouldn't be
        considered a public method.
        '''
        return self.__data