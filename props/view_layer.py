from bpy.types import ViewLayer, PropertyGroup
from bpy.props import *
from ..utils import register_utils

'''
RenderPassConfig is a simple helper class to manage AOV data
differences between Blender and Arnold.
'''
class RenderPassConfig:
    def __init__(self, name, ainame, channels, chan_id, pixel_type):
        self.name = name             # label in UI
        self.ainame = ainame         # Arnold-specific name
        self.channels = channels     # Number of channels
        self.chan_id = chan_id       # Channel names, one character per channel
        self.pixel_type = pixel_type # Arnold-specific pixel type (FLOAT, RGB, RGBA, etc)
        
        # For compositor
        # Enum in ['VALUE', 'VECTOR', 'COLOR']
        if pixel_type == 'FLOAT':
            self.pass_type = 'VALUE'
        elif 'RGB' in pixel_type:
            self.pass_type = 'COLOR'

class RenderPassConfigGroup:
    data = (
        RenderPassConfig("Beauty", "RGBA", 4, "RGBA", "RGBA"),
        RenderPassConfig("Z", "Z", 1, "Z", "FLOAT"),
        RenderPassConfig("Normal", "N", 3, "RGB", "VECTOR"),
        RenderPassConfig("Position", "P", 3, "RGB", "VECTOR"),
        RenderPassConfig("Direct", "direct", 3, "RGB", "RGB"),
        RenderPassConfig("Indirect", "indirect", 3, "RGB", "RGB"),
        RenderPassConfig("Emission", "emission", 3, "RGB", "RGB"),
        RenderPassConfig("Background", "background", 3, "RGB", "RGB"),
        RenderPassConfig("Diffuse", "diffuse", 3, "RGB", "RGB"),
        RenderPassConfig("Specular", "specular", 3, "RGB", "RGB"),
        RenderPassConfig("Coat", "coat", 3, "RGB", "RGB"),
        RenderPassConfig("Transmission", "transmission", 3, "RGB", "RGB"),
        RenderPassConfig("SSS", "sss", 3, "RGB", "RGB"),
        RenderPassConfig("Volume", "volume", 3, "RGB", "RGB"),
        RenderPassConfig("Albedo", "albedo", 3, "RGB", "RGB"),
        RenderPassConfig("Light Groups", "light_groups", 3, "RGB", "RGB"),
        RenderPassConfig("Motion Vectors", "motionvector", 3, "RGB", "RGB"),
    )

    light = (
        RenderPassConfig("Diffuse Direct", "diffuse_direct", 3, "RGB", "RGB"),
        RenderPassConfig("Diffuse Indirect", "diffuse_indirect", 3, "RGB", "RGB"),
        RenderPassConfig("Diffuse Albedo", "diffuse_albedo", 3, "RGB", "RGB"),
        RenderPassConfig("Specular Direct", "specular_direct", 3, "RGB", "RGB"),
        RenderPassConfig("Specular Indirect", "specular_indirect", 3, "RGB", "RGB"),
        RenderPassConfig("Specular Albedo", "specular_albedo", 3, "RGB", "RGB"),
        RenderPassConfig("Coat Direct", "coat_direct", 3, "RGB", "RGB"),
        RenderPassConfig("Coat Indirect", "coat_indirect", 3, "RGB", "RGB"),
        RenderPassConfig("Coat Albedo", "coat_albedo", 3, "RGB", "RGB"),
        RenderPassConfig("Transmission Direct", "transmission_direct", 3, "RGB", "RGB"),
        RenderPassConfig("Transmission Indirect", "transmission_indirect", 3, "RGB", "RGB"),
        RenderPassConfig("Transmission Albedo", "transmission_albedo", 3, "RGB", "RGB"),
        RenderPassConfig("SSS Direct", "sss_direct", 3, "RGB", "RGB"),
        RenderPassConfig("SSS Indirect", "sss_indirect", 3, "RGB", "RGB"),
        RenderPassConfig("SSS Albedo", "sss_albedo", 3, "RGB", "RGB"),
        RenderPassConfig("Volume Direct", "volume_direct", 3, "RGB", "RGB"),
        RenderPassConfig("Volume Indirect", "volume_indirect", 3, "RGB", "RGB"),
        RenderPassConfig("Volume Albedo", "volume_albedo", 3, "RGB", "RGB"),
    )

class ArnoldRenderPasses(PropertyGroup):
    config = RenderPassConfigGroup()

    def update_render_passes(self, context):
        context.view_layer.update_render_passes()

    enabled_data_aovs: BoolVectorProperty(
        name="Data AOVs",
        size=len(config.data),
        default=tuple(aov.name in {"Beauty", "Z"} for aov in config.data),
        update=update_render_passes
    )

    enabled_light_aovs: BoolVectorProperty(
        name="Light AOVs",
        size=len(config.light),
        default=tuple(False for i in range(len(config.light))),
        update=update_render_passes
    )

    @property
    def beauty(self):
        return self.config.data[0]

    @property
    def enabled_aovs(self):
        result = [aov for aov in self.config.data if self.enabled_data_aovs[self.config.data.index(aov)]]
        result += [aov for aov in self.config.light if self.enabled_light_aovs[self.config.light.index(aov)]]

        return result

class ArnoldRenderLayer(PropertyGroup):
    aovs: PointerProperty(type=ArnoldRenderPasses)

classes = (
    ArnoldRenderPasses,
    ArnoldRenderLayer,
)

def register():
    register_utils.register_classes(classes)
    ViewLayer.arnold = PointerProperty(type=ArnoldRenderLayer)

def unregister():
    del ViewLayer.arnold
    register_utils.unregister_classes(classes)