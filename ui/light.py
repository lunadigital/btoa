import bpy
from bl_ui.properties_data_light import DataButtonsPanel
from .. import engine

class DATA_PT_arnold_light(DataButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_light"
    bl_label = "Light"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.prop(light.arnold, "type", expand=True)
        layout.separator()

        layout.use_property_split = True

        col = layout.column()
        col.prop(light, "color")
        col.prop(light.arnold, "intensity")
        col.prop(light.arnold, "exposure")

        col.separator()

        if light.type in ('POINT', 'SPOT'):
            col.prop(light, "shadow_soft_size", text="Radius")

        if light.type == 'SUN':
            col.prop(light.arnold, "angle")

class DATA_PT_arnold_light_shape(DataButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_light_shape"
    bl_label = "Shape"
    bl_parent_id = DATA_PT_arnold_light.bl_idname
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    @classmethod
    def poll(self, context):
        return context.light.type in ('SPOT', 'AREA')

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.use_property_split = True

        col = layout.column()

        if light.type == 'SPOT':
            col.prop(light.arnold, "spot_roundness")
            col.prop(light.arnold, "aspect_ratio")
            col.prop(light.arnold, "lens_radius")

        if light.type == 'AREA':
            col.prop(light.arnold, "shape")
            col.prop(light.arnold, "spread")
            col.prop(light.arnold, "resolution")
            col.prop(light.arnold, "area_roundness")
            col.prop(light.arnold, "soft_edge")

class DATA_PT_arnold_light_shadows(DataButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_light_shadows"
    bl_label = "Shadows"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.use_property_split = True

        col = layout.column()
        col.prop(light.arnold, "shadow_color")
        col.prop(light.arnold, "shadow_density")

        col.separator()

        col.prop(light.arnold, "cast_shadows")
        col.prop(light.arnold, "cast_volumetric_shadows")

class DATA_PT_arnold_light_advanced(DataButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_light_advanced"
    bl_label = "Advanced"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.use_property_split = True

        col = layout.column()
        col.prop(light.arnold, "samples")
        col.prop(light.arnold, "normalize")

classes = [
    DATA_PT_arnold_light,
    DATA_PT_arnold_light_shape,
    DATA_PT_arnold_light_shadows,
    DATA_PT_arnold_light_advanced,
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
