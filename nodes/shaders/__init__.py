from . import (
    ambient_occlusion,
    bump2d,
    car_paint,
    flat,
    lambert,
    matte,
    output,
    shadow_matte,
    skydome,
    standard_surface,
    wireframe
)

modules = (
    ambient_occlusion,
    bump2d,
    car_paint,
    flat,
    lambert,
    matte,
    output,
    shadow_matte,
    skydome,
    standard_surface,
    wireframe
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()