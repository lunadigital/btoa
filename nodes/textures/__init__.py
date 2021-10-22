from . import (
    cell_noise,
    checkerboard,
    flakes,
    image,
    layered_texture,
    layer_float,
    layer_rgba,
    noise,
    round_corners
)

modules = (
    cell_noise,
    checkerboard,
    flakes,
    image,
    layered_texture,
    layer_float,
    layer_rgba,
    noise,
    round_corners
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()