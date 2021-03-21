import bpy
from bpy.types import Node, PropertyGroup
from bpy.props import EnumProperty, BoolProperty

from ..base import ArnoldNode

class AiCellNoise(Node, ArnoldNode):
    ''' A cell noise pattern generator. '''
    bl_label = "Cell Noise"
    bl_icon = 'NONE'
    
    ai_name = "cell_noise"

    pattern: EnumProperty(
        name="Pattern",
        items=[
            ("0", "Noise1", "Noise1"),
            ("1", "Noise2", "Noise2"),
            ("2", "Cell1", "Cell1"),
            ("3", "Cell2", "Cell2"),
            ("4", "Worley1", "Worley1"),
            ("5", "Worley2", "Worley2"),
            ("6", "Alligator", "Alligator")
        ],
        default="0"
    )

    additive: BoolProperty(name="Additive")

    def init(self, context):
        self.inputs.new("AiNodeSocketIntAboveOne", "Octaves", identifier="octaves").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Randomness", identifier="randomness").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Lacunarity", identifier="lacunarity").default_value = 1.92
        self.inputs.new("AiNodeSocketFloatNormalized", "Amplitude", identifier="amplitude").default_value = 1
        self.inputs.new("AiNodeSocketVector", "Scale", identifier="scale").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketVector", "Offset", identifier="offset")
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")
        #self.inputs.new("AiNodeSocketCoord", "P", identifier="p")
        self.inputs.new("AiNodeSocketFloatUnbounded", "Time", identifier="time")
        self.inputs.new("AiNodeSocketRGB", "Palette", identifier="palette").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketFloatPositive", "Density", identifier="density").default_value = 0.5

        self.outputs.new("AiNodeSocketRGB", "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pattern", text="")
        layout.prop(self, "additive")
    
    def sub_export(self, node):
        node.set_int("pattern", int(self.pattern))
        node.set_bool("additive", self.additive)

classes = (
    AiCellNoise,
)
register, unregister = bpy.utils.register_classes_factory(classes)