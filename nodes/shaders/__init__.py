from . import color
from . import conversion
from . import inputs
from . import lights
from . import math
from . import surface
from . import textures
from . import utility

def register():
    color.register()
    conversion.register()
    inputs.register()
    lights.register()
    math.register()
    surface.register()
    textures.register()
    utility.register()

def unregister():
    color.unregister()
    conversion.unregister()
    inputs.unregister()
    lights.unregister()
    math.unregister()
    surface.unregister()
    textures.unregister()
    utility.unregister()