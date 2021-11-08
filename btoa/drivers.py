from ctypes import *

ArnoldDisplayCallback = CFUNCTYPE(
    None,
    c_uint32,
    c_uint32,
    c_uint32,
    c_uint32,
    POINTER(c_float),
    c_void_p
)