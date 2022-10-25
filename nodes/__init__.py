from . import core
from . import sockets
from . import shaders

def register():
    core.register()
    sockets.register()
    shaders.register()

def unregister():
    core.unregister()
    sockets.unregister()
    shaders.unregister()