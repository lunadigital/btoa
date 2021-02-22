from . import base
from . import color
from . import sockets
from . import shaders
from . import textures
from . import utilities

def register():
    base.register()
    color.register()
    sockets.register()
    shaders.register()
    textures.register()
    utilities.register()

def unregister():
    base.unregister()
    color.unregister()
    sockets.unregister()
    shaders.unregister()
    textures.unregister()
    utilities.unregister()