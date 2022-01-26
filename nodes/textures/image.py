import bpy
from bpy.types import Node, PropertyGroup
from bpy.props import PointerProperty, EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty

from ..base import ArnoldNode
from .. import constants

class AiImageUser(PropertyGroup):
    image: PointerProperty(type=bpy.types.Image)

    frame_start: IntProperty(name="First Frame")
    frame_offset: IntProperty(name="Offset")

class AiImage(Node, ArnoldNode):
    ''' Performs texture mapping using a specified image file. '''
    bl_label = "Image"
    bl_width_default = constants.BL_NODE_WIDTH_DEFAULT
    bl_icon = 'NONE'

    ai_name = "image"

    AI_WRAP_OPTIONS = [
            ("0", "Periodic", "Periodic"),
            ("1", "Black", "Black"),
            ("2", "Clamp", "Clamp"),
            ("3", "Mirror", "Mirror"),
            ("4", "File", "File")
        ]

    image: PointerProperty(
        name="Image",
        type=bpy.types.Image
    )

    image_user: PointerProperty(type=AiImageUser)

    image_filter: EnumProperty(
        name="Filter",
        items=[
            ('closest', "Closest", "Closest"),
            ('bilinear', "Bilinear", "Bilinear"),
            ('bicubic', "Bicubic", "Bicubic"),
            ('smart_bicubic', "Smart Bicubic", "Smart Bicubic")
        ],
        default='smart_bicubic'
    )

    swrap: EnumProperty(
        name="Wrap U",
        items=AI_WRAP_OPTIONS,
        default="0"
    )

    twrap: EnumProperty(
        name="Wrap V",
        items=AI_WRAP_OPTIONS,
        default="0"
    )

    sscale: FloatProperty(
        name="Scale U",
        min=0.00001,
        soft_max=2,
        default=1
    )

    tscale: FloatProperty(
        name="Scale V",
        min=0.00001,
        soft_max=2,
        default=1
    )

    sflip: BoolProperty(name="Flip U")
    tflip: BoolProperty(name="Flip V")
    swap_st: BoolProperty(name="Swap UV")
    
    single_channel: BoolProperty(name="Single Channel")

    start_channel: IntProperty(
        name="Start Channel",
        min=0,
        max=3
    )

    mipmap_bias: IntProperty(
        name="Mipmap Bias",
        soft_min=-5,
        soft_max=5
    )

    uvset: StringProperty(
        name="UV Set"
    )

    # uvcoords?

    soffset: FloatProperty(
        name="Offset U",
        soft_min=-1,
        soft_max=1
    )

    toffset: FloatProperty(
        name="Offset V",
        soft_min=-1,
        soft_max=1
    )

    ignore_missing_textures: BoolProperty(name="Ignore Missing Textures")
    
    def init(self, context):
        self.inputs.new("AiNodeSocketRGB", "Multiply", identifier="multiply").default_value = (1, 1, 1)
        self.inputs.new("AiNodeSocketRGB", "Offset", identifier="offset").default_value = (0, 0, 0)
        self.inputs.new("AiNodeSocketRGBA", "Missing Texture Color", identifier="missing_texture_color").default_value = (1, 0, 1, 1)

        self.outputs.new("AiNodeSocketRGBA", "RGBA")

    def draw_label(self):
        if self.image:
            return self.image.name
        else:
            return self.bl_label

    def draw_buttons(self, context, layout):
        layout.template_ID(self, "image", open="image.open")

        layout.separator()

        if self.image:
            layout.prop(self.image.colorspace_settings, "name")

        layout.prop(self, "image_filter")
        layout.prop(self, "swrap")
        layout.prop(self, "twrap")
        layout.prop(self, "sscale")
        layout.prop(self, "tscale")
        layout.prop(self, "sflip")
        layout.prop(self, "tflip")
        layout.prop(self, "swap_st")
        layout.prop(self, "single_channel")
        layout.prop(self, "start_channel")
        layout.prop(self, "mipmap_bias")
        layout.prop(self, "uvset")
        layout.prop(self, "soffset")
        layout.prop(self, "toffset")
        layout.prop(self, "ignore_missing_textures")

    def sub_export(self, node):
        if self.image:
            if self.image.library:
                node.set_string("filename", bpy.path.abspath(self.image.filepath, library=self.image.library))
            else:
                node.set_string("filename", bpy.path.abspath(self.image.filepath))

            node.set_string("color_space", self.image.colorspace_settings.name)

        node.set_string("filter", self.image_filter)
        node.set_int("swrap", int(self.swrap))
        node.set_int("twrap", int(self.twrap))
        node.set_float("sscale", self.sscale)
        node.set_float("tscale", self.tscale)
        node.set_bool("sflip", self.sflip)
        node.set_bool("tflip", self.tflip)
        node.set_bool("swap_st", self.swap_st)
        node.set_bool("single_channel", self.single_channel)
        node.set_int("start_channel", self.start_channel)
        node.set_int("mipmap_bias", self.mipmap_bias)
        node.set_string("uvset", self.uvset)
        node.set_float("soffset", self.soffset)
        node.set_float("toffset", self.toffset)
        node.set_bool("ignore_missing_textures", self.ignore_missing_textures)

classes = (
    AiImageUser,
    AiImage
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)