from . import bl_id
from . import camera
from . import light
from . import material
from . import mesh
from . import options
from . import view_layer
from . import world

def register():
    bl_id.register()
    camera.register()
    light.register()
    material.register()
    mesh.register()
    options.register()
    view_layer.register()
    world.register()

def unregister():
    bl_id.unregister()
    camera.unregister()
    light.unregister()
    material.unregister()
    mesh.unregister()
    options.unregister()
    view_layer.unregister()
    world.unregister()