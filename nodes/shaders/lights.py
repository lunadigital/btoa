import bpy
import math, mathutils
from bpy.props import *
from .. import base
from ... import btoa, utils

'''
AiSkydome
https://docs.arnoldrenderer.com/display/A5NodeRef/skydome_light

Returns a skydome light for World rendering.
'''
class AiSkydome(bpy.types.Node, base.ArnoldNode):
    bl_label = "Skydome"
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
        self.inputs.new('AiNodeSocketRGB', "Color", identifier="color").default_value = (0.050876, 0.050876, 0.050876)
        self.inputs.new('AiNodeSocketSkydomeIntensity', "Intensity", identifier="intensity")
        self.inputs.new('AiNodeSocketSkydomeExposure', "Exposure", identifier="exposure")
        self.inputs.new('AiNodeSocketSkydomeResolution', "Resolution", identifier="resolution")

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "image_format", text="")
        layout.prop(self, "portal_mode", text="")

        layout.prop(context.scene.world.arnold, "rotation_controller")

    def sub_export(self, node):
        node.set_int("format", int(self.image_format))
        node.set_int("portal_mode", int(self.portal_mode))

        '''
        Set the skydome's rotation to align with Blender's coordinate system. Additional rotation
        can be set with a rotation controller in the UI.
        '''
        rx = mathutils.Matrix.Rotation(0 + (math.pi / 2), 4, 'X')
        ry = mathutils.Matrix.Rotation(0, 4, 'Y')
        rz = mathutils.Matrix.Rotation(0, 4, 'Z')
        rot_matrix = rx @ ry @ rz

        scale_matrix = mathutils.Matrix.Scale(-1, 4, (0, 0, 1))

        matrix = mathutils.Matrix.Identity(4)
        matrix = matrix @ rot_matrix @ scale_matrix

        node.set_matrix("matrix", btoa.utils.flatten_matrix(matrix))

classes = (
    AiSkydome,
)

def register():
    utils.register_classes(classes)

def unregister():
    utils.unregister_classes(classes)