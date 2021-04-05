from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

# TODO: Add missing parameters
# order
# tangent_space

class AiNormalMap(Node, ArnoldNode):
    ''' Provides bump mapping based on a 2d texture map '''
    bl_label = "Normal Map"
    bl_icon = 'NONE'
    
    ai_name = "normal_map"

    invert_x: BoolProperty(name="Invert X")
    invert_y: BoolProperty(name="Invert Y")
    invert_z: BoolProperty(name="Invert Z")

    color_to_signed: BoolProperty(
        name="Color to signed",
        description="For 8-bit maps. If enabled, the input is remapped to the [-1,1] range"
    )

    normalize: BoolProperty(name="Normalize")

    def init(self, context):
        self.inputs.new('AiNodeSocketVector', name="Input", identifier="input")

        self.inputs.new('AiNodeSocketFloatUnbounded', name="Strength", identifier="strength").default_value = 1
        
        self.inputs.new('AiNodeSocketVector', name="Tangent", identifier="tangent")
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "invert_x")
        layout.prop(self, "invert_y")
        layout.prop(self, "invert_z")

        layout.separator()

        layout.prop(self, "color_to_signed")
        layout.prop(self, "normalize")

    def sub_export(self, node):
        node.set_bool("invert_x", self.invert_x)
        node.set_bool("invert_y", self.invert_y)
        node.set_bool("invert_z", self.invert_z)
        node.set_bool("color_to_signed", self.color_to_signed)
        node.set_bool("normalize", self.normalize)

def register():
    from bpy.utils import register_class
    register_class(AiNormalMap)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiNormalMap)