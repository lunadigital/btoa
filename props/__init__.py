from . import camera
from . import light
from . import options

def register():
    camera.register()
    light.register()
    options.register()

def unregister():
    camera.unregister()
    light.unregister()
    options.unregister()