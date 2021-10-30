from . import (
    color_correct,
    constant,
    color_jitter
)

modules = (
    color_correct,
    constant,
    color_jitter
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()