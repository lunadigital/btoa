from ctypes import *

class AtAOV(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("channels", c_int),
        ("data", POINTER(c_float))
    ]

class AtRenderData(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("width", c_int),
        ("height", c_int),
        ("size", c_int),
        ("count", c_int),
        ("aovs", POINTER(AtAOV))
    ]

ArnoldDisplayCallback = CFUNCTYPE(
    None,
    POINTER(AtRenderData)
)