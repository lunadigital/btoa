from . import camera
from . import light
from . import material
from . import options

def register():
    camera.register()
    light.register()
    material.register()
    options.register()

def unregister():
    camera.unregister()
    light.unregister()
    material.unregister()
    options.unregister()