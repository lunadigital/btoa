from . import camera
from . import light
from . import material
from . import render
from . import gizmos

def register():
    camera.register()
    light.register()
    material.register()
    render.register()
    gizmos.register()

def unregister():
    camera.unregister()
    light.unregister()
    material.unregister()
    render.unregister()
    gizmos.unregister()