from . import core
from . import sockets
from . import shaders
from . import menus

def register():
    core.register()
    sockets.register()
    shaders.register()
    menus.register()

def unregister():
    core.unregister()
    sockets.unregister()
    shaders.unregister()
    menus.unregister()