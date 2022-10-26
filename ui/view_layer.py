import bpy
from bl_ui.properties_view_layer import ViewLayerButtonsPanel
from ..preferences import ENGINE_ID

class ArnoldViewLayerPanel(ViewLayerButtonsPanel, bpy.types.Panel):
    bl_context = "view_layer"
    COMPAT_ENGINES = {ENGINE_ID}

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

        aovs = context.view_layer.arnold.aovs

        for i in range(len(aovs.enabled_data_aovs)):
            aov = aovs.config.data[i]
            layout.prop(aovs, "enabled_data_aovs", index=i, text=aov.name)

class ARNOLD_RENDER_PT_aovs_light(ArnoldViewLayerPanel):
    bl_label = "Light"
    bl_parent_id = "ARNOLD_RENDER_PT_aovs"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        aovs = context.view_layer.arnold.aovs

        for i in range(len(aovs.enabled_light_aovs)):
            aov = aovs.config.light[i]
            label = aov.name.split()

            if i % 3 == 0:
                col = layout.column(heading=label[0])

            col.prop(aovs, "enabled_light_aovs", index=i, text=" ".join(label[1:]))

class ARNOLD_RENDER_PT_aovs_cryptomatte(ArnoldViewLayerPanel):
    bl_label = "Cryptomatte"
    bl_parent_id = "ARNOLD_RENDER_PT_aovs"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        view_layer = context.view_layer

        col = layout.column()
        col.prop(view_layer, "use_pass_cryptomatte_asset")
        col.prop(view_layer, "use_pass_cryptomatte_material")
        col.prop(view_layer, "use_pass_cryptomatte_object")

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
    ARNOLD_RENDER_PT_aovs_light,
    #ARNOLD_RENDER_PT_aovs_cryptomatte,
    ARNOLD_RENDER_PT_override,
)

def register():
    from ..utils import register_utils as utils
    utils.register_classes(classes)

def unregister():
    from ..utils import register_utils as utils
    utils.unregister_classes(classes)