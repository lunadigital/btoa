from . import camera
from . import options

def register():
    camera.register()
    options.register()

def unregister():
    camera.unregister()
    options.unregister()