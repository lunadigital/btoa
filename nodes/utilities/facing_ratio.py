import bpy
from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

class AiFacingRatio(Node, ArnoldNode):
    ''' '''
    bl_label = "Facing Ratio"
    bl_icon = 'NONE'
    
    ai_name = "facing_ratio"

    linear: BoolProperty(name="Linear")
    invert: BoolProperty(name="Invert")

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Bias", identifier="bias").default_value = 0.5
        self.inputs.new('AiNodeSocketFloatNormalized', "Gain", identifier="gain").default_value = 0.5

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "linear")
        layout.prop(self, "invert")

    def sub_export(self, node):
        node.set_bool("linear", self.linear)
        node.set_bool("invert", self.invert)

def register():
    bpy.utils.register_class(AiFacingRatio)

def unregister():
    bpy.utils.unregister_class(AiFacingRatio)