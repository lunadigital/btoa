from . import (
    cell_noise,
    checkerboard,
    flakes,
    image,
    noise
)

modules = (
    cell_noise,
    checkerboard,
    flakes,
    image,
    noise
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()