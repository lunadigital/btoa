import bpy
from bl_ui.properties_data_light import DataButtonsPanel
from ..preferences import ENGINE_ID

class ArnoldLightPanel(DataButtonsPanel, bpy.types.Panel):
    COMPAT_ENGINES = {ENGINE_ID}

class DATA_PT_arnold_light(ArnoldLightPanel):
    bl_idname = "DATA_PT_arnold_light"
    bl_label = "Light"

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.prop(light.arnold, "type", expand=True)
        layout.separator()

        layout.use_property_split = True

        is_quad_light = (light.type == 'AREA' and light.arnold.shape == 'quad_light')

        col = layout.column()
        col.enabled = not is_quad_light or not light.arnold.portal
        col.prop(light, "color")
        col.prop(light.arnold, "intensity")
        col.prop(light.arnold, "exposure")

        if is_quad_light:
            col = layout.column()
            col.prop(light.arnold, "portal")

        col.separator()

        if light.type in ('POINT', 'SPOT'):
            col.prop(light, "shadow_soft_size", text="Radius")

        if light.type == 'SUN':
            col.prop(light.arnold, "angle")

class DATA_PT_arnold_light_shape(ArnoldLightPanel):
    bl_idname = "DATA_PT_arnold_light_shape"
    bl_label = "Shape"
    bl_parent_id = DATA_PT_arnold_light.bl_idname

    @classmethod
    def poll(self, context):
        return context.light.type in ('SPOT', 'AREA')

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.use_property_split = True

        is_quad_light = (light.type == 'AREA' and light.arnold.shape == 'quad_light')

        col = layout.column()
        col.enabled = not is_quad_light or not light.arnold.portal

        if light.type == 'SPOT':
            col.prop(light, "spot_size", text="Cone Angle")
            col.prop(light.arnold, "penumbra_angle")
            col.prop(light, "show_cone")

            col.separator()
            
            col.prop(light.arnold, "spot_roundness")
            col.prop(light.arnold, "aspect_ratio")
            col.prop(light.arnold, "lens_radius")

        if light.type == 'AREA':
            col.prop(light.arnold, "shape")

            if light.shape == 'DISK':
                col.prop(light, "size", text="Radius")
            elif light.shape == 'RECTANGLE':
                col.prop(light, "size", text="Radius")
                col.prop(light, "size_y", text="Length")
            else:
                col.prop(light, "size", text="Size")

            col.prop(light.arnold, "spread")
            col.prop(light.arnold, "resolution")

            if light.shape == 'SQUARE':
                col.prop(light.arnold, "area_roundness")
                col.prop(light.arnold, "soft_edge")

class DATA_PT_arnold_light_shadows(ArnoldLightPanel):
    bl_idname = "DATA_PT_arnold_light_shadows"
    bl_label = "Shadows"

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

class DATA_PT_arnold_light_advanced(ArnoldLightPanel):
    bl_idname = "DATA_PT_arnold_light_advanced"
    bl_label = "Advanced"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.use_property_split = True

        col = layout.column()
        col.prop(light.arnold, "samples")
        col.prop(light.arnold, "normalize")

class DATA_PT_arnold_light_visibility(ArnoldLightPanel):
    bl_idname = "DATA_PT_arnold_light_visibility"
    bl_label = "Visibility"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        light = context.light

        layout.use_property_split = True

        col = layout.column()
        col.prop(light.arnold, "camera")
        col.prop(light.arnold, "diffuse")
        col.prop(light.arnold, "specular")
        col.prop(light.arnold, "transmission")
        col.prop(light.arnold, "sss")
        col.prop(light.arnold, "indirect")
        col.prop(light.arnold, "volume")
        col.prop(light.arnold, "max_bounces")

classes = (
    DATA_PT_arnold_light,
    DATA_PT_arnold_light_shape,
    DATA_PT_arnold_light_shadows,
    DATA_PT_arnold_light_advanced,
    DATA_PT_arnold_light_visibility
)

def register():
    from ..utils import register_utils as utils
    utils.register_classes(classes)

def unregister():
    from ..utils import register_utils as utils
    utils.unregister_classes(classes)