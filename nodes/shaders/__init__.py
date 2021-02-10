from . import ambient_occlusion
from . import car_paint
from . import flat
from . import lambert
from . import matte
from . import output
from . import shadow_matte
from . import standard_surface
from . import wireframe

def register():
    ambient_occlusion.register()
    car_paint.register()
    flat.register()
    lambert.register()
    matte.register()
    output.register()
    shadow_matte.register()
    standard_surface.register()
    wireframe.register()

def unregister():
    ambient_occlusion.unregister()
    car_paint.unregister()
    flat.unregister()
    lambert.unregister()
    matte.unregister()
    output.unregister()
    shadow_matte.unregister()
    standard_surface.unregister()
    wireframe.unregister()