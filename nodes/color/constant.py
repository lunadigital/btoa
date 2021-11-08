import bpy
from bpy.types import Node

from ..base import ArnoldNode

class AiColorConstant(Node, ArnoldNode):
    ''' Returns a constant RGBA color value. '''
    bl_label = "Constant"
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new("AiNodeSocketRGB", name="Color", identifier="input")
        self.outputs.new("AiNodeSocketRGB", "RGB", identifier="output")

    # This isn't a native Arnold node class, so we're
    # hijacking the export method to get the result
    # we want.
    def export(self):
        return self.inputs[0].default_value, self.inputs[0].default_type

def register():
    from bpy.utils import register_class
    register_class(AiColorConstant)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiColorConstant)