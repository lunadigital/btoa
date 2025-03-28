from . import material
from . import world

def register():
    material.register()
    world.register()

def unregister():
    world.unregister()
    material.unregister()