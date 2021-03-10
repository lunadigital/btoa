from . import (
    camera,
    light,
    material,
    options
)

modules = (
    camera,
    light,
    material,
    options
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()