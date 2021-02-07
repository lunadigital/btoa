from bpy.types import Node
from bpy.props import FloatProperty, BoolProperty, IntProperty

from ..base import ArnoldNode

from arnold import AiNodeSetInt, AiNodeSetFlt, AiNodeSetBool

class AiAmbientOcclusion(Node, ArnoldNode):
    '''Ambient occlusion shader. Outputs RGB.'''
    bl_label = "Ambient Occlusion"
    bl_icon = 'MATERIAL'

    ai_name = "ambient_occlusion"

    samples: IntProperty(
        name="Samples",
        min=1,
        default=3
    )

    spread: FloatProperty(
        name="Spread",
        min=0,
        max=1,
        default=1
    )

    near_clip: FloatProperty(
        name="Near Clip",
        min=0
    )

    far_clip: FloatProperty(
        name="Far Clip",
        min=0,
        default=5
    )

    invert_normals: BoolProperty(name="Invert Normals")
    self_only: BoolProperty(name="Self Only")

    def init(self, context):
        #black color
        #white color
        self.inputs.new("AiNodeSocketColorRGB", "Black Color", identifier="black_color").default_value = (0, 0, 0)
        self.inputs.new("AiNodeSocketColorRGB", "White Color", identifier="white_color")

        self.inputs.new('AiNodeSocketFloatPositive', "Falloff", identifier="falloff").default_value = 1

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "samples")
        layout.prop(self, "spread")
        layout.prop(self, "near_clip")
        layout.prop(self, "far_clip")
        layout.prop(self, "invert_normals")
        layout.prop(self, "self_only")

    def sub_export(self, ainode):
        AiNodeSetInt(ainode, "samples", self.samples)
        AiNodeSetFlt(ainode, "spread", self.spread)
        AiNodeSetFlt(ainode, "near_clip", self.near_clip)
        AiNodeSetFlt(ainode, "far_clip", self.far_clip)
        AiNodeSetBool(ainode, "invert_normals", self.invert_normals)
        AiNodeSetBool(ainode, "self_only", self.self_only)

def register():
    from bpy.utils import register_class
    register_class(AiAmbientOcclusion)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiAmbientOcclusion)
    