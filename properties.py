import bpy
from bpy.types import Scene, PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty

class ArnoldOptions(PropertyGroup):
    use_adaptive_sampling: BoolProperty()
    aa_samples: IntProperty(name="AA Samples", min=0, default=3)
    diffuse_samples: IntProperty(name="Diffuse Samples", min=0, default=2)
    specular_samples: IntProperty(name="Specular Samples", min=0, default=2)
    transmission_samples: IntProperty(name="Transmission Samples", min=0, default=2)
    sss_samples: IntProperty(name="SSS Samples", min=0, default=2)
    volume_samples: IntProperty(name="Volume Samples", min=0, default=2)
    aa_seed: IntProperty(name="AA Seed", min=0, default=1)
    sample_clamp: IntProperty(name="Sample Clamp", min=0, default=10)
    clamp_aovs: BoolProperty(name="Clamp AOVs")
    indirect_sample_clamp: IntProperty(name="Indirect Sample Clamp", min=0, default=10)
    low_light_threshold: FloatProperty(name="Low Light Threshold", min=0, default=0.001)
    adaptive_aa_samples_max: IntProperty(name="AA Samples Max", min=0, default=0)
    adaptive_threshold: FloatProperty(name="Adaptive Threshold", min=0, default=0.05)

def register():
    bpy.utils.register_class(ArnoldOptions)
    Scene.arnold_options = PointerProperty(type=ArnoldOptions)

def unregister():
    del Scene.arnold_options
    bpy.utils.unregister_class(ArnoldOptions)