from . import coord_space
from . import uv_projection

def register():
    coord_space.register()
    uv_projection.register()

def unregister():
    coord_space.unregister()
    uv_projection.unregister()