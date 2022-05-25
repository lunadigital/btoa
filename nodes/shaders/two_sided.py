import bpy
from bpy.types import Node
from bpy.props import BoolProperty, EnumProperty

from ..base import ArnoldNode
from .. import constants

class AiTwoSided(Node, ArnoldNode):
    '''Applies two shaders on either side of a double sided surface.'''
    bl_label = "Two Sided"
    bl_icon = 'NONE'

    ai_name = "two_sided"

    def init(self, context):
        self.inputs.new('AiNodeSocketSurface', "Front", identifier="front")
        self.inputs.new('AiNodeSocketSurface', "Back", identifier="back")
        
        self.outputs.new('AiNodeSocketSurface', name="Closure", identifier="output")

def register():
    bpy.utils.register_class(AiTwoSided)

def unregister():
    bpy.utils.unregister_class(AiTwoSided)