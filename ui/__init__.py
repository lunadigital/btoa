from . import camera
from . import render

def register():
    camera.register()
    render.register()

def unregister():
    camera.unregister()
    render.unregister()