from . import camera
from . import light
from . import material
from . import render

def register():
    camera.register()
    light.register()
    material.register()
    render.register()

def unregister():
    camera.unregister()
    light.unregister()
    material.unregister()
    render.unregister()