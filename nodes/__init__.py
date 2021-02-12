from . import base
from . import sockets
from . import shaders
from . import textures

def register():
    base.register()
    sockets.register()
    shaders.register()
    textures.register()

def unregister():
    base.unregister()
    sockets.unregister()
    shaders.unregister()
    textures.unregister()