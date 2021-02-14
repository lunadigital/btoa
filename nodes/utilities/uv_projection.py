
from bpy.types import Node
from bpy.props import EnumProperty

from ..base import ArnoldNode

from arnold import *

class AiUVProjection(Node, ArnoldNode):
    '''
    Turns any 2D texture into a 3D texture that you can place on the
    surface using one of the available projection types. Use to adjust
    the texture placement on the surface.
    '''
    bl_label = "UV Projection"

    ai_name = "uv_projection"

    projection_type: EnumProperty(
        name="Projection Type",
        items=[
            ('planar', "Planar", "Planar"),
            ('spherical', "Spherical", "Spherical"),
            ('cylindrical', "Cylindrical", "Cylindrical"),
            ('ball', "Ball", "Ball"),
            ('cubic', "Cubic", "Cubic"),
            ('shrinkwrap', "Shrinkwrap", "Shrinkwrap")
        ],
        default='planar'
    )

    def init(self, context):
        self.inputs.new("AiNodeSocketRGBA", "Color", identifier="projection_color")
        self.inputs.new("AiNodeSocketCoord", "Coords", identifier="coord_space")

        self.outputs.new("AiNodeSocketRGBA", "RGBA")

    def draw_buttons(self, context, layout):
        layout.prop(self, "projection_type")

    def sub_export(self, ainode):
        AiNodeSetStr(ainode, "projection_type", self.projection_type)

def register():
    from bpy.utils import register_class
    register_class(AiUVProjection)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiUVProjection)