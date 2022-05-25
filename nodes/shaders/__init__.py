from . import (
    ambient_occlusion,
    bump2d,
    car_paint,
    displacement,
    flat,
    float_to_rgb,
    float_to_rgba,
    lambert,
    matte,
    mix_shader,
    normal_map,
    output,
    shadow_matte,
    skydome,
    standard_surface,
    two_sided,
    wireframe
)

modules = (
    ambient_occlusion,
    bump2d,
    car_paint,
    displacement,
    flat,
    float_to_rgb,
    float_to_rgba,
    lambert,
    matte,
    mix_shader,
    normal_map,
    output,
    shadow_matte,
    skydome,
    standard_surface,
    two_sided,
    wireframe
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()