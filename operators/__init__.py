from . import (
    handlers,
    material,
    world
)

modules = (
    handlers,
    material,
    world
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()