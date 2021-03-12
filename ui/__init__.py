from . import (
    camera,
    light,
    material,
    render,
    gizmos,
    world
)

modules = (
    camera,
    light,
    material,
    render,
    gizmos,
    world
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()