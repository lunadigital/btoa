from . import (
    camera,
    light,
    material,
    options,
    world
)

modules = (
    camera,
    light,
    material,
    options,
    world
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()