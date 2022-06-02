from . import color
from . import conversion
from . import lights
from . import surface

def register():
    color.register()
    conversion.register()
    lights.register()
    surface.register()

def unregister():
    color.register()
    conversion.unregister()
    lights.unregister()
    surface.unregister()