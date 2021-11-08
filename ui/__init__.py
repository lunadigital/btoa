from . import (
    camera,
    light,
    material,
    mesh,
    presets,
    render,
    gizmos,
    view_layer,
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
    view_layer,
    world
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()