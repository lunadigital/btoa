import bpy
from bpy.types import Node, PropertyGroup
from bpy.props import BoolProperty, StringProperty, PointerProperty, EnumProperty, CollectionProperty

from ..base import ArnoldNode
from .. import constants

class LayerProperties(PropertyGroup):
    enabled: BoolProperty(name="Enable", default=True)
    name: StringProperty(name="Name")
    operation: EnumProperty(
        name="Operation",
        items=[
            ("atop", "Atop", ""),
            ("average", "Average", ""),
            ("cojoint_over", "Cojoint Over", ""),
            ("color_burn", "Color Burn", ""),
            ("color_dodge", "Color Dodge", ""),
            ("difference", "Difference", ""),
            ("disjoint_over", "Disjoint Over", ""),
            ("divide", "Divide", ""),
            ("exclusion", "Exclusion", ""),
            ("from", "From", ""),
            ("geometric", "Geometric", ""),
            ("glow", "Glow", ""),
            ("hard_light", "Hard Light", ""),
            ("hard_mix", "Hard Mix", ""),
            ("hypot_diagonal", "Hypot Diagonal", ""),
            ("in", "In", ""),
            ("linear_light", "Linear Light", ""),
            ("mask", "Mask", ""),
            ("matte", "Matte", ""),
            ("max", "Max", ""),
            ("min", "Min", ""),
            ("minus", "Minus", ""),
            ("multiply", "Multiply", ""),
            ("negation", "Negation", ""),
            ("out", "Out", ""),
            ("over", "Over", ""),
            ("overlay", "Overlay", ""),
            ("overwrite", "Overwrite", ""),
            ("phoenix", "Phoenix", ""),
            ("pin_light", "Pin Light", ""),
            ("plus", "Plus", ""),
            ("reflect", "Reflect", ""),
            ("screen", "Screen", ""),
            ("soft_light", "Soft Light", ""),
            ("stencil", "Stencil", ""),
            ("subtract", "Subtract", ""),
            ("under", "Under", ""),
            ("vivid_light", "Vivid Light", ""),
            ("xor", "XOR", "")
        ],
        default="over"
    )
    alpha_operation: EnumProperty(
        name="Alpha Channel Operation",
        description="",
        items=[
            ("result", "Result", ""),
            ("preserve", "Preserve", ""),
            ("overwrite", "Overwrite", ""),
            ("mask", "Mask", ""),
        ],
        default="result"
    )

class AiLayeredTexture(Node, ArnoldNode):
    ''' A base class for layered Arnold texture nodes (layer_float, layer_rgba). This is NOT a public-facing class. '''
    bl_icon = 'NONE'
    bl_width_default = constants.BL_NODE_WIDTH_DEFAULT

    layers: CollectionProperty(type=LayerProperties)

    def init(self, context):
        for i in range(1, 9):
            layer = self.layers.add()
            layer.name = "Layer{}".format(i)

    def template_layer_properties(self, layout, layer):
        split = layout.split(factor=0.1)

        col = split.column()
        col.prop(layer, "enabled", text="")

        col = split.column()
        col.prop(layer, "name", text="")
        col.enabled = layer.enabled

    def draw_buttons(self, context, layout):
        for layer in self.layers:
            self.template_layer_properties(layout, layer)

    def sub_export(self, node):
        for layer, i in zip(self.layers, range(1, 9)):
            node.set_bool("enable{}".format(i), layer.enabled)
            node.set_string("name{}".format(i), layer.name)

def register():
    bpy.utils.register_class(LayerProperties)

def unregister():
    bpy.utils.unregister_class(LayerProperties)