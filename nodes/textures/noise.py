import bpy
from bpy.types import Node
from bpy.props import EnumProperty

from ..base import ArnoldNode

class AiNoise(Node, ArnoldNode):
    ''' Evaluates a coherent noise function. '''
    bl_label = "Noise"
    ai_name = "noise"

    mode: EnumProperty(
        name="Mode",
        items=[
            ("0", "Scalar", "Scalar"),
            ("1", "Vector", "Vector"),
        ],
        default="0"
    )

    def init(self, context):
        self.inputs.new("AiNodeSocketRGB", "Color1", identifier="color1")
        self.inputs.new("AiNodeSocketRGB", "Color2", identifier="color2").default_value = (0, 0 ,0)
        self.inputs.new("AiNodeSocketIntAboveOne", "Octaves", identifier="octaves").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Distortion", identifier="distortion").default_value = 1
        self.inputs.new("AiNodeSocketFloatPositive", "Lacunarity", identifier="lacunarity").default_value = 1.92
        self.inputs.new("AiNodeSocketFloatNormalized", "Amplitude", identifier="amplitude").default_value = 1
        self.inputs.new("AiNodeSocketVector", "Scale", identifier="scale").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketVector", "Offset", identifier="offset")
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")
        #self.inputs.new("AiNodeSocketCoord", "P", identifier="p")
        self.inputs.new("AiNodeSocketFloatUnbounded", "Time", identifier="time")
        
        self.outputs.new("AiNodeSocketRGB", "RGB")

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")
    
    def sub_export(self, node):
        node.set_int("mode", int(self.mode))
        
classes = (
    AiNoise,
)
register, unregister = bpy.utils.register_classes_factory(classes)