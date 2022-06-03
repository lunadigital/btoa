from . import color
from . import conversion
from . import lights
from . import math
from . import surface
from . import textures

def register():
    color.register()
    conversion.register()
    lights.register()
    math.register()
    surface.register()
    textures.register()

def unregister():
    color.unregister()
    conversion.unregister()
    lights.unregister()
    math.unregister()
    surface.unregister()
    textures.unregister()