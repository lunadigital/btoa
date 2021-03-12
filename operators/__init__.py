from . import (
    material,
    world
)

modules = (
    material,
    world
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()