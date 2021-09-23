from . import (
    camera,
    light,
    material,
    mesh,
    presets,
    render,
    gizmos,
    world
)

modules = (
    camera,
    light,
    material,
    mesh,
    presets,
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