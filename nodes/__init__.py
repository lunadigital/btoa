from . import core
from . import sockets
from . import shaders
from . import menus
from . import autoswitch

def register():
    core.register()
    sockets.register()
    shaders.register()
    menus.register()
    autoswitch.register()

def unregister():
    core.unregister()
    sockets.unregister()
    shaders.unregister()
    menus.unregister()
    autoswitch.unregister()