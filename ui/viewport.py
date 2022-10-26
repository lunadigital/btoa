from bpy.types import VIEW3D_HT_header
from ..utils import ui_utils

def viewport_mult_func(self, context):
    if ui_utils.arnold_is_active(context):
        self.layout.prop(context.scene.arnold, "viewport_scale", text="")

def register():
    VIEW3D_HT_header.append(viewport_mult_func)

def unregister():
    VIEW3D_HT_header.remove(viewport_mult_func)