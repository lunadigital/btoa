from . import base
#from . import sockets
from . import shaders

def register():
    base.register()
    #sockets.register()
    shaders.register()

def unregister():
    base.unregister()
    #sockets.unregister()
    shaders.unregister()