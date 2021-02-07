from . import ambient_occlusion
from . import lambert
from . import output
from . import standard_surface

def register():
    ambient_occlusion.register()
    lambert.register()
    output.register()
    standard_surface.register()

def unregister():
    ambient_occlusion.unregister()
    lambert.unregister()
    output.unregister()
    standard_surface.unregister()