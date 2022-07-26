from bpy.types import ViewLayer, PropertyGroup
from bpy.props import *
from .. import utils

class ArnoldRenderPasses(PropertyGroup):
    use_pass_beauty: BoolProperty(name="Beauty", default=True)
    use_pass_z: BoolProperty(name="Z", default=True)
    use_pass_direct: BoolProperty(name="Direct")
    use_pass_indirect: BoolProperty(name="Indirect")
    use_pass_emission: BoolProperty(name="Emission")
    use_pass_background: BoolProperty(name="Background")
    use_pass_diffuse: BoolProperty(name="Diffuse")
    use_pass_specular: BoolProperty(name="Specular")
    use_pass_coat: BoolProperty(name="Coat")
    use_pass_transmission: BoolProperty(name="Transmission")
    use_pass_sss: BoolProperty(name="SSS")
    use_pass_volume: BoolProperty(name="Volume")
    use_pass_albedo: BoolProperty(name="Albedo")
    use_pass_diffuse_direct: BoolProperty(name="Diffuse Direct")
    use_pass_diffuse_indirect: BoolProperty(name="Diffuse Indirect")
    use_pass_diffuse_albedo: BoolProperty(name="Diffuse Albedo")
    use_pass_specular_direct: BoolProperty(name="Specular Direct")
    use_pass_specular_indirect: BoolProperty(name="Specular Indirect")
    use_pass_specular_albedo: BoolProperty(name="Specular Albedo")
    use_pass_coat_direct: BoolProperty(name="Coat Direct")
    use_pass_coat_indirect: BoolProperty(name="Coat Indirect")
    use_pass_coat_albedo: BoolProperty(name="Coat Albedo")
    use_pass_transmission_direct: BoolProperty(name="Transmission Direct")
    use_pass_transmission_indirect: BoolProperty(name="Transmission Indirect")
    use_pass_transmission_albedo: BoolProperty(name="Transmission Albedo")
    use_pass_sss_direct: BoolProperty(name="SSS Direct")
    use_pass_sss_indirect: BoolProperty(name="SSS Indirect")
    use_pass_sss_albedo: BoolProperty(name="SSS Albedo")
    use_pass_volume_direct: BoolProperty(name="Volume Direct")
    use_pass_volume_indirect: BoolProperty(name="Volume Indirect")
    use_pass_volume_albedo: BoolProperty(name="Volume Albedo")
    use_pass_light_groups: BoolProperty(name="Light Groups")
    use_pass_motionvector: BoolProperty(name="Motion Vectors")

class ArnoldRenderLayer(PropertyGroup):
    passes: PointerProperty(type=ArnoldRenderPasses)

classes = (
    ArnoldRenderPasses,
    ArnoldRenderLayer,
)

def register():
    utils.register_classes(classes)
    ViewLayer.arnold = PointerProperty(type=ArnoldRenderLayer)

def unregister():
    del ViewLayer.arnold
    utils.unregister_classes(classes)