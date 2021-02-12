from . import base
from . import sockets
from . import shaders
from . import textures
from . import utilities

def register():
    base.register()
    sockets.register()
    shaders.register()
    textures.register()
    utilities.register()

def unregister():
    base.unregister()
    sockets.unregister()
    shaders.unregister()
    textures.unregister()
    utilities.unregister()