from . import (
    color_correct,
    constant,
    color_jitter,
    composite,
    shuffle
)

modules = (
    color_correct,
    constant,
    color_jitter,
    composite,
    shuffle
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()