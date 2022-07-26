from ctypes import *

ArnoldDisplayCallback = CFUNCTYPE(
    None,
    c_char_p,
    c_uint32,
    c_uint32,
    c_uint32,
    c_uint32,
    POINTER(c_float)
)