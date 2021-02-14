from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

from arnold import AiNodeSetBool

class AiMatte(Node, ArnoldNode):
    ''' Enables you to create holdout effects by rendering the alpha as zero. '''
    bl_label = "Matte"
    bl_icon = 'MATERIAL'

    ai_name = "matte"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGBA', "Color", identifier="color")
        self.inputs.new('AiNodeSocketRGB', "Opacity", identifier="opacity").default_value = (1, 1, 1)

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

def register():
    from bpy.utils import register_class
    register_class(AiMatte)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiMatte)