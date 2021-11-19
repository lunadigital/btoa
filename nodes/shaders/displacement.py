import bpy
from bpy.types import Node
from bpy.props import BoolProperty, FloatProperty

from ..base import ArnoldNode
from .. import constants

class AiDisplacement(Node, ArnoldNode):
    '''
    This is a dummy node to send displacement data to Arnold by
    hijacking the polymesh node. It's not beautiful, but it works.
    '''
    bl_label = "Displacement"
    bl_width_default = constants.BL_NODE_WIDTH_DEFAULT
    bl_icon = 'NONE'

    disp_padding: FloatProperty(
        name="Padding",
        min=0,
        soft_max=1
    )

    disp_height: FloatProperty(
        name="Height",
        soft_min=0,
        soft_max=2,
        default=1
    )

    disp_zero_value: FloatProperty(
        name="Zero Value",
        soft_min=-1,
        soft_max=1
    )

    disp_autobump: BoolProperty(name="Auto Bump")

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Input", identifier="disp_map").default_value = (0, 0, 0)
        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "disp_padding")
        layout.prop(self, "disp_height")
        layout.prop(self, "disp_zero_value")
        layout.prop(self, "disp_autobump")

    # This isn't a native Arnold node class, so we're
    # hijacking the export method to get the result
    # we want.
    def export(self):
        return (
            self.inputs[0].export()[0],
            self.disp_padding,
            self.disp_height,
            self.disp_zero_value,
            self.disp_autobump
        )

def register():
    bpy.utils.register_class(AiDisplacement)

def unregister():
    bpy.utils.unregister_class(AiDisplacement)