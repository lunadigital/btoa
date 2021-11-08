from . import (
    camera,
    light,
    material,
    mesh,
    options,
    world
)

modules = (
    camera,
    light,
    material,
    mesh,
    options,
    world
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()