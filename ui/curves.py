import bpy
from bl_ui.properties_data_curve import CurveButtonsPanel
from bl_ui.properties_object import ObjectButtonsPanel
from ..utils import ui_utils


class ArnoldCurvesDataPanel(CurveButtonsPanel, bpy.types.Panel):
    @classmethod
    def poll(self, context):
        return ui_utils.arnold_is_active(context) and context.curves is not None


class ArnoldCurvesObjectPanel(ObjectButtonsPanel, bpy.types.Panel):
    @classmethod
    def poll(self, context):
        return ui_utils.arnold_is_active(context) and context.object.type == 'CURVES'


class DATA_PT_arnold_curves_settings(ArnoldCurvesDataPanel):
    bl_label = "Arnold Curves"

    def draw(self, context):
        layout = self.layout
        curves = context.curves

        layout.use_property_split = True

        layout.prop(curves.arnold_curves, "mode")
        layout.prop(curves.arnold_curves, "basis")
        layout.prop(curves.arnold_curves, "min_pixel_width")
        layout.prop(curves.arnold_curves, "subdivide_curves")
        layout.prop(curves.arnold_curves, "export_uvs")
        layout.prop(curves.arnold_curves, "attach_to_surface")


class OBJECT_PT_arnold_curves_visibility(ArnoldCurvesObjectPanel):
    bl_parent_id = "OBJECT_PT_visibility"
    bl_label = "Arnold"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        curves = context.curves

        layout.use_property_split = True

        layout.prop(curves.arnold_curves, "camera")
        layout.prop(curves.arnold_curves, "shadow")
        layout.prop(curves.arnold_curves, "diffuse_transmission")
        layout.prop(curves.arnold_curves, "specular_transmission")
        layout.prop(curves.arnold_curves, "volume")
        layout.prop(curves.arnold_curves, "diffuse_reflection")
        layout.prop(curves.arnold_curves, "specular_reflection")
        layout.prop(curves.arnold_curves, "sss")


classes = (
    DATA_PT_arnold_curves_settings,
    OBJECT_PT_arnold_curves_visibility
)


def register():
    from ..utils import register_utils
    register_utils.register_classes(classes)


def unregister():
    from ..utils import register_utils
    register_utils.unregister_classes(classes)
