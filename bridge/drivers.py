from ctypes import *
from .node import ArnoldNode

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

class DisplayDriver:
    def __init__(self, function):
        self.callback = ArnoldDisplayCallback(function)
        self.driver = ArnoldNode("btoa_display_driver")
        self.driver.set_string("name", "btoa_driver")
        self.driver.set_pointer("callback", self.callback)