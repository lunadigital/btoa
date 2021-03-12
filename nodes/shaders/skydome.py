from bpy.types import Node
from ..base import ArnoldNode

class AiSkydome(Node, ArnoldNode):
    ''' Returns a skydome light for World rendering '''
    bl_label = "Skydome"
    bl_icon = 'MATERIAL'

    ai_name = "skydome_light"

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="color")
        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

def register():
    from bpy.utils import register_class
    register_class(AiSkydome)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiSkydome)