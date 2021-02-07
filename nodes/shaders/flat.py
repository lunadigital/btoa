from bpy.types import Node
from ..base import ArnoldNode

class AiFlat(Node, ArnoldNode):
    '''A simple color shader node which just allows a color with no other effects.'''
    bl_label = "Flat"
    bl_icon = 'MATERIAL'

    ai_name = "flat"

    def init(self, context):
        self.inputs.new('AiNodeSocketColor', "Color", identifier="color")
        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

def register():
    from bpy.utils import register_class
    register_class(AiFlat)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiFlat)