from bpy.types import Node
from bpy.props import FloatProperty, BoolProperty, IntProperty

from ..base import ArnoldNode

class AiAmbientOcclusion(Node, ArnoldNode):
    '''Ambient occlusion shader. Outputs RGB.'''
    bl_label = "Ambient Occlusion"
    bl_icon = 'NONE'
    
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
        self.inputs.new("AiNodeSocketRGB", "Black Color", identifier="black").default_value = (0, 0, 0)
        self.inputs.new("AiNodeSocketRGB", "White Color", identifier="white")
        self.inputs.new('AiNodeSocketFloatPositive', "Falloff", identifier="falloff").default_value = 1
        self.inputs.new('AiNodeSocketVector', "Normal", identifier="normal")

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "samples")
        layout.prop(self, "spread")
        layout.prop(self, "near_clip")
        layout.prop(self, "far_clip")
        layout.prop(self, "invert_normals")
        layout.prop(self, "self_only")

    def sub_export(self, node):
        node.set_uint("samples", self.samples)
        node.set_float("spread", self.spread)
        node.set_float("near_clip", self.near_clip)
        node.set_float("far_clip", self.far_clip)
        node.set_bool("invert_normals", self.invert_normals)
        node.set_bool("self_only", self.self_only)

def register():
    from bpy.utils import register_class
    register_class(AiAmbientOcclusion)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiAmbientOcclusion)
    