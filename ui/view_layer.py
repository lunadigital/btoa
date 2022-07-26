import bpy
from bl_ui.properties_view_layer import ViewLayerButtonsPanel

class ArnoldViewLayerPanel(ViewLayerButtonsPanel, bpy.types.Panel):
    bl_context = "view_layer"

    @classmethod
    def poll(cls, context):
        return context.engine in {'ARNOLD'}

class ARNOLD_RENDER_PT_aovs(ArnoldViewLayerPanel):
    bl_label = "AOVs"

    def draw(self, context):
        pass

class ARNOLD_RENDER_PT_aovs_data(ArnoldViewLayerPanel):
    bl_label = "Data"
    bl_parent_id = "ARNOLD_RENDER_PT_aovs"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        arnold_view_layer = context.view_layer.arnold

        col = layout.column()
        for annotation in arnold_view_layer.passes.__annotations__.keys():
            col.prop(arnold_view_layer.passes, annotation)

class ARNOLD_RENDER_PT_override(ArnoldViewLayerPanel):
    bl_label = "Override"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        view_layer = context.view_layer

        layout.prop(view_layer, "material_override")

classes = (
    ARNOLD_RENDER_PT_aovs,
    ARNOLD_RENDER_PT_aovs_data,
    ARNOLD_RENDER_PT_override,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)