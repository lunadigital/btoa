from bpy.types import Node
from bpy.props import EnumProperty, FloatVectorProperty

import math
import mathutils

from ..base import ArnoldNode
from ... import utils

class AiSkydome(Node, ArnoldNode):
    ''' Returns a skydome light for World rendering '''
    bl_label = "Skydome"
    bl_icon = 'NONE'
    
    ai_name = "skydome_light"

    image_format: EnumProperty(
        name="Format",
        items=[
            ("0", "Angular", "Angular"),
            ("1", "Mirrored Ball", "Mirrored Ball"),
            ("2", "Lat-long", "Lat-long"),
        ],
        default="2"
    )

    portal_mode: EnumProperty(
        name="Portal Mode",
        items=[
            ("0", "Off", "Off"),
            ("1", "Interior Only", "Interior Only"),
            ("2", "Interior/Exterior", "Interior/Exterior"),
        ],
        default="1"
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="color")
        self.inputs.new('AiNodeSocketFloatPositive', "Intensity", identifier="intensity").default_value = 1
        self.inputs.new('AiNodeSocketFloatPositive', "Exposure", identifier="exposure")
        self.inputs.new('AiNodeSocketIntPositive', "Resolution", identifier="resolution").default_value = 1000

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "image_format", text="")
        layout.prop(self, "portal_mode", text="")

        layout.prop(context.scene.world.arnold, "rotation_controller")

    def sub_export(self, node):
        node.set_int("format", int(self.image_format))
        node.set_int("portal_mode", int(self.portal_mode))

        # Set skydome orientation
        # This assumes a rotation of (0, 0, 0)
        # Additional rotation should be set with a rotation controller
        rx = mathutils.Matrix.Rotation(0 + (math.pi / 2), 4, 'X')
        ry = mathutils.Matrix.Rotation(0, 4, 'Y')
        rz = mathutils.Matrix.Rotation(0, 4, 'Z')
        rot_matrix = rx @ ry @ rz

        scale_matrix = mathutils.Matrix.Scale(-1, 4, (0, 0, 1))

        matrix = mathutils.Matrix.Identity(4)
        matrix = matrix @ rot_matrix @ scale_matrix

        node.set_matrix("matrix", utils.flatten_matrix(matrix))

def register():
    from bpy.utils import register_class
    register_class(AiSkydome)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiSkydome)