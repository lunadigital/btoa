from . import base
from . import color
from . import math_shaders
from . import sockets
from . import shaders
from . import textures
from . import utilities

def register():
    base.register()
    color.register()
    math_shaders.register()
    sockets.register()
    shaders.register()
    textures.register()
    utilities.register()

def unregister():
    base.unregister()
    color.unregister()
    math_shaders.unregister()
    sockets.unregister()
    shaders.unregister()
    textures.unregister()
    utilities.unregister()