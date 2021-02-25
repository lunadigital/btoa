from . import (
    cell_noise,
    checkerboard,
    image
)

modules = (
    cell_noise,
    checkerboard,
    image
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()