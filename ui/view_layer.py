import bpy
from bl_ui.properties_view_layer import ViewLayerButtonsPanel
from bpy.types import Panel

from .. import engine

class ARNOLD_PT_override(ViewLayerButtonsPanel, Panel):
    bl_label = "Override"
    bl_context = "view_layer"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        view_layer = context.view_layer

        layout.prop(view_layer, "material_override")

classes = (
    ARNOLD_PT_override,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)