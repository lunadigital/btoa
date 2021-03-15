from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode
from .. import constants

class AiShadowMatte(Node, ArnoldNode):
    '''
    Typically used on floor planes to 'catch' shadows from lighting within the scene.
    It is useful for integrating a rendered object onto a photographic background.
    '''
    bl_label = "Shadow Matte"
    bl_width_default = constants.BL_NODE_WIDTH_DEFAULT
    bl_icon = 'MATERIAL'

    ai_name = "shadow_matte"

    diffuse_use_background: BoolProperty(
        name="Diffuse Use Background",
        default=True
    )

    indirect_diffuse_enable: BoolProperty(name="Enable Indirect Diffuse")
    indirect_specular_enable: BoolProperty(name="Enable Indirect Specular")

    alpha_mask: BoolProperty(
        name="Alpha Mask",
        default=True
    )

    def init(self, context):
        # background - Not sure how to implement this yet...
        self.inputs.new('AiNodeSocketRGB', "Offscreen Color", identifier="offscreen_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketRGB', "Shadow Color", identifier="shadow_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatNormalized', "Shadow Opacity", identifier="shadow_opacity").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Diffuse Color", identifier="diffuse_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatPositive', "Diffuse Intensity", identifier="diffuse_intensity").default_value = 1
        self.inputs.new('AiNodeSocketFloatNormalized', "Backlighting", identifier="backlighting")
        self.inputs.new('AiNodeSocketRGB', "Specular Color", identifier="specular_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Intensity", identifier="specular_intensity")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.1
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.52

        # aov_shadow
        # aov_shadow_diff
        # aov_shadow_mask

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "diffuse_use_background")
        layout.prop(self, "indirect_diffuse_enable")
        layout.prop(self, "indirect_specular_enable")
        layout.prop(self, "alpha_mask")

    def sub_export(self, node):
        node.set_bool("diffuse_use_background", self.diffuse_use_background)
        node.set_bool("indirect_diffuse_enable", self.indirect_diffuse_enable)
        node.set_bool("indirect_specular_enable", self.indirect_specular_enable)
        node.set_bool("alpha_mask", self.alpha_mask)

def register():
    from bpy.utils import register_class
    register_class(AiShadowMatte)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiShadowMatte)