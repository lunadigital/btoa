import bpy
from bpy.types import Node
from bpy.props import EnumProperty, FloatProperty, IntProperty

from ..base import ArnoldNode

class AiColorJitter(Node, ArnoldNode):
    '''
    This shader enables you to alter the input color by applying a random
    color variation. For each of the following parameters, you can specify
    the range of hue, saturation, and gain (HSV) for the random colors.
    The seed is used to get a different random variation.
    '''
    bl_label = "Color Jitter"
    bl_icon = 'NONE'
    
    ai_name = "color_jitter"

    jitter_type: EnumProperty(
        name="Type",
        items=[
            # ('data', "User Data", ""),
            ('proc', "Procedural", ""),
            ('obj', "Object", ""),
            ('face', "Face", "")
        ]
    )

    # `data_*` parameters aren't exposed because they rely on user data to work, and
    # BtoA doesn't support user data at the moment

    # data_input
    # data_gain_min
    # data_gain_max
    # data_hue_min
    # data_hue_max
    # data_saturation_min
    # data_saturation_max
    # data_seed

    proc_gain_min: FloatProperty(
        name="Gain Min",
        min=0,
        soft_max=1
    )

    proc_gain_max: FloatProperty(
        name="Gain Max",
        min=0,
        soft_max=1
    )

    proc_hue_min: FloatProperty(
        name="Hue Min",
        min=-1,
        max=1
    )

    proc_hue_max: FloatProperty(
        name="Hue Max",
        min=-1,
        max=1
    )

    proc_saturation_min: FloatProperty(
        name="Saturation Min",
        min=0,
        soft_max=1
    )

    proc_saturation_max: FloatProperty(
        name="Saturation Max",
        min=0,
        soft_max=1
    )

    proc_seed: IntProperty(
        name="Seed",
        min=0,
        soft_max=10
    )

    obj_gain_min: FloatProperty(
        name="Gain Min",
        min=0,
        soft_max=1
    )

    obj_gain_max: FloatProperty(
        name="Gain Max",
        min=0,
        soft_max=1
    )

    obj_hue_min: FloatProperty(
        name="Hue Min",
        min=-1,
        max=1
    )

    obj_hue_max: FloatProperty(
        name="Hue Max",
        min=-1,
        max=1
    )

    obj_saturation_min: FloatProperty(
        name="Saturation Min",
        min=0,
        soft_max=1
    )

    obj_saturation_max: FloatProperty(
        name="Saturation Max",
        min=0,
        soft_max=1
    )

    obj_seed: IntProperty(
        name="Seed",
        min=0,
        soft_max=10
    )

    face_gain_min: FloatProperty(
        name="Gain Min",
        min=0,
        soft_max=1
    )

    face_gain_max: FloatProperty(
        name="Gain Max",
        min=0,
        soft_max=1
    )

    face_hue_min: FloatProperty(
        name="Hue Min",
        min=-1,
        max=1
    )

    face_hue_max: FloatProperty(
        name="Hue Max",
        min=-1,
        max=1
    )

    face_saturation_min: FloatProperty(
        name="Saturation Min",
        min=0,
        soft_max=1
    )

    face_saturation_max: FloatProperty(
        name="Saturation Max",
        min=0,
        soft_max=1
    )

    face_seed: IntProperty(
        name="Seed",
        min=0,
        soft_max=10
    )

    face_mode: EnumProperty(
        name="Mode",
        items=[
            ("face id", "Face ID", ""),
            ("uniform id", "Uniform ID", ""),
        ]
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketRGB', name="Input", identifier="input")
        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "jitter_type")

        layout.prop(self, "{}_gain_min".format(self.jitter_type))
        layout.prop(self, "{}_gain_max".format(self.jitter_type))
        layout.prop(self, "{}_hue_min".format(self.jitter_type))
        layout.prop(self, "{}_hue_max".format(self.jitter_type))
        layout.prop(self, "{}_saturation_min".format(self.jitter_type))
        layout.prop(self, "{}_saturation_max".format(self.jitter_type))
        layout.prop(self, "{}_seed".format(self.jitter_type))

        if self.jitter_type == "face":
            layout.prop(self, "face_mode")

    def sub_export(self, node):
        if self.jitter_type == "proc":
            node.set_float("proc_gain_min", self.proc_gain_min)
            node.set_float("proc_gain_max", self.proc_gain_max)
            node.set_float("proc_hue_min", self.proc_hue_min)
            node.set_float("proc_hue_max", self.proc_hue_max)
            node.set_float("proc_saturation_min", self.proc_saturation_min)
            node.set_float("proc_saturation_max", self.proc_saturation_max)
            node.set_int("proc_seed", self.proc_seed)
        
        elif self.jitter_type == "obj":
            node.set_float("obj_gain_min", self.obj_gain_min)
            node.set_float("obj_gain_max", self.obj_gain_max)
            node.set_float("obj_hue_min", self.obj_hue_min)
            node.set_float("obj_hue_max", self.obj_hue_max)
            node.set_float("obj_saturation_min", self.obj_saturation_min)
            node.set_float("obj_saturation_max", self.obj_saturation_max)
            node.set_int("obj_seed", self.obj_seed)

        elif self.jitter_type == "face":
            node.set_float("face_gain_min", self.face_gain_min)
            node.set_float("face_gain_max", self.face_gain_max)
            node.set_float("face_hue_min", self.face_hue_min)
            node.set_float("face_hue_max", self.face_hue_max)
            node.set_float("face_saturation_min", self.face_saturation_min)
            node.set_float("face_saturation_max", self.face_saturation_max)
            node.set_int("face_seed", self.face_seed)

            node.set_string("face_mode", self.face_mode)
            
def register():
    bpy.utils.register_class(AiColorJitter)

def unregister():
    bpy.utils.unregister_class(AiColorJitter)