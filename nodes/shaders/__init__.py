from . import lambert
from . import output
from . import standard_surface

def register():
    lambert.register()
    output.register()
    standard_surface.register()

def unregister():
    lambert.unregister()
    output.unregister()
    standard_surface.unregister()