from . import (
    coord_space,
    facing_ratio,
    uv_projection
)

modules = (
    coord_space,
    facing_ratio,
    uv_projection
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()