from bpy.types import Node
from ..base import ArnoldNode

class AiBump2d(Node, ArnoldNode):
    ''' Provides bump mapping based on a 2d texture map '''
    bl_label = "Bump 2D"
    bl_icon = 'MATERIAL'

    ai_name = "bump2d"

    def init(self, context):
        self.inputs.new('AiNodeSocketVector', name="Bump Map", identifier="bump_map")
        self.inputs.new('AiNodeSocketFloatUnbounded', name="Bump Height", identifier="bump_height").default_value = 1
        self.inputs.new('AiNodeSocketVector', name="Normal", identifier="normal")

        self.outputs.new('AiNodeSocketVector', name="Vector", identifier="output")

def register():
    from bpy.utils import register_class
    register_class(AiBump2d)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiBump2d)