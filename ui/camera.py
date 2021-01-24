import bpy
from bl_ui.properties_data_camera import CameraButtonsPanel
from .. import engine

class DATA_PT_arnold_lens(CameraButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_lens"
    bl_label = "Lens"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        camera = context.camera

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(camera.arnold, "camera_type")

        col.separator()

        if camera.arnold.camera_type == 'persp_camera':
            col = self.layout.column()
            if camera.lens_unit == 'MILLIMETERS':
                col.prop(camera, "lens")
            elif camera.lens_unit == 'FOV':
                col.prop(camera, "angle")
            col.prop(camera, "lens_unit")

        col.separator()

        col.prop(camera.arnold, "exposure")

class DATA_PT_arnold_dof(CameraButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_dof"
    bl_label = "Depth of Field"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw_header(self, context):
        self.layout.prop(context.camera.arnold, "enable_dof", text="")

    def draw(self, context):
        camera = context.camera

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(camera.arnold, "focus_distance")
        col.enabled = camera.arnold.enable_dof

class DATA_PT_arnold_aperture(CameraButtonsPanel, bpy.types.Panel):
    bl_parent_id = DATA_PT_arnold_dof.bl_idname
    bl_idname = "DATA_PT_arnold_aperture"
    bl_label = "Aperture"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        camera = context.camera

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(camera.arnold, "aperture_size")
        col.prop(camera.arnold, "aperture_blades")
        col.prop(camera.arnold, "aperture_blade_curvature")
        col.prop(camera.arnold, "aperture_rotation")
        col.prop(camera.arnold, "aperture_aspect_ratio")
        col.enabled = camera.arnold.enable_dof

classes = (
    DATA_PT_arnold_lens,
    DATA_PT_arnold_dof,
    DATA_PT_arnold_aperture,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
