from bpy.types import VIEW3D_HT_header
from ..utils import ui_utils

def viewport_mult_func(self, context):
    layout = self.layout
    view = context.space_data
    scene = context.scene

    if view.shading.type == 'RENDERED' and ui_utils.arnold_is_active(context):
        layout.prop(scene.arnold, "viewport_scale", text="")
        layout.prop(scene.arnold, "preview_pause", icon='PLAY' if scene.arnold.preview_pause else 'PAUSE', text="")

def register():
    VIEW3D_HT_header.append(viewport_mult_func)

def unregister():
    VIEW3D_HT_header.remove(viewport_mult_func)