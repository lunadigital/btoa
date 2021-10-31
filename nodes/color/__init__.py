from . import (
    color_correct,
    constant,
    color_jitter,
    composite
)

modules = (
    color_correct,
    constant,
    color_jitter,
    composite
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()