from . import camera
from . import light
from . import render

def register():
    camera.register()
    light.register()
    render.register()

def unregister():
    camera.unregister()
    light.unregister()
    render.unregister()