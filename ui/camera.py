import bpy
from bl_ui.properties_data_camera import CameraButtonsPanel, CAMERA_PT_presets
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
        elif camera.arnold.camera_type == 'ortho_camera':
            col = self.layout.column()
            col.prop(camera, "ortho_scale")

        col.separator()

        col.prop(camera.arnold, "exposure")

class DATA_PT_arnold_dof(CameraButtonsPanel, bpy.types.Panel):
    bl_idname = "DATA_PT_arnold_dof"
    bl_label = "Depth of Field"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw_header(self, context):
        self.layout.prop(context.camera.arnold, "enable_dof", text="")

    def draw(self, context):
        camera = context.camera

        self.layout.use_property_split = True

        col = self.layout.column()
        col.enabled = camera.arnold.enable_dof
        col.prop(camera.dof, "focus_object", text="Focus on Object")

        sub = col.column()
        sub.active = (camera.dof.focus_object is None)
        sub.prop(camera.dof, "focus_distance")

# This is a hacky way to get more control over where Blender
# panels appear in relation to Arnold panels
#
# Copied directly from bl_ui.properties_data_camera
class DATA_PT_arnold_camera(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Camera"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw_header_preset(self, _context):
        CAMERA_PT_presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout

        cam = context.camera

        layout.use_property_split = True

        col = layout.column()
        col.prop(cam, "sensor_fit")

        if cam.sensor_fit == 'AUTO':
            col.prop(cam, "sensor_width", text="Size")
        else:
            sub = col.column(align=True)
            sub.active = cam.sensor_fit == 'HORIZONTAL'
            sub.prop(cam, "sensor_width", text="Width")

            sub = col.column(align=True)
            sub.active = cam.sensor_fit == 'VERTICAL'
            sub.prop(cam, "sensor_height", text="Height")

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

# This is a hacky way to get more control over where Blender
# panels appear in relation to Arnold panels
#
# Copied directly from bl_ui.properties_data_camera
class DATA_PT_arnold_camera_background_image(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Background Images"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw_header(self, context):
        cam = context.camera

        self.layout.prop(cam, "show_background_images", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        cam = context.camera
        use_multiview = context.scene.render.use_multiview

        col = layout.column()
        col.operator("view3d.background_image_add", text="Add Image")

        for i, bg in enumerate(cam.background_images):
            layout.active = cam.show_background_images
            box = layout.box()
            row = box.row(align=True)
            row.prop(bg, "show_expanded", text="", emboss=False)
            if bg.source == 'IMAGE' and bg.image:
                row.prop(bg.image, "name", text="", emboss=False)
            elif bg.source == 'MOVIE_CLIP' and bg.clip:
                row.prop(bg.clip, "name", text="", emboss=False)
            elif bg.source and bg.use_camera_clip:
                row.label(text="Active Clip")
            else:
                row.label(text="Not Set")

            row.prop(
                bg,
                "show_background_image",
                text="",
                emboss=False,
                icon='RESTRICT_VIEW_OFF' if bg.show_background_image else 'RESTRICT_VIEW_ON',
            )

            row.operator("view3d.background_image_remove", text="", emboss=False, icon='X').index = i

            if bg.show_expanded:
                row = box.row()
                row.prop(bg, "source", expand=True)

                has_bg = False
                if bg.source == 'IMAGE':
                    row = box.row()
                    row.template_ID(bg, "image", open="image.open")
                    if bg.image is not None:
                        box.template_image(bg, "image", bg.image_user, compact=True)
                        has_bg = True

                        if use_multiview:
                            box.prop(bg.image, "use_multiview")

                            column = box.column()
                            column.active = bg.image.use_multiview

                            column.label(text="Views Format:")
                            column.row().prop(bg.image, "views_format", expand=True)

                            sub = column.box()
                            sub.active = bg.image.views_format == 'STEREO_3D'
                            sub.template_image_stereo_3d(bg.image.stereo_3d_format)

                elif bg.source == 'MOVIE_CLIP':
                    box.prop(bg, "use_camera_clip", text="Active Clip")

                    column = box.column()
                    column.active = not bg.use_camera_clip
                    column.template_ID(bg, "clip", open="clip.open")

                    if bg.clip:
                        column.template_movieclip(bg, "clip", compact=True)

                    if bg.use_camera_clip or bg.clip:
                        has_bg = True

                    column = box.column()
                    column.active = has_bg
                    column.prop(bg.clip_user, "use_render_undistorted")
                    column.prop(bg.clip_user, "proxy_render_size")

                if has_bg:
                    col = box.column()
                    col.prop(bg, "alpha", slider=True)
                    col.row().prop(bg, "display_depth", expand=True)

                    col.row().prop(bg, "frame_method", expand=True)

                    row = box.row()
                    row.prop(bg, "offset")

                    col = box.column()
                    col.prop(bg, "rotation")
                    col.prop(bg, "scale")

                    col.prop(bg, "use_flip_x")
                    col.prop(bg, "use_flip_y")

# This is a hacky way to get more control over where Blender
# panels appear in relation to Arnold panels
#
# Copied directly from bl_ui.properties_data_camera
class DATA_PT_arnold_camera_display(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Viewport Display"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        cam = context.camera

        col = layout.column(align=True)

        col.prop(cam, "display_size", text="Size")

        col = layout.column(heading="Show")
        col.prop(cam, "show_limits", text="Limits")
        col.prop(cam, "show_mist", text="Mist")
        col.prop(cam, "show_sensor", text="Sensor")
        col.prop(cam, "show_name", text="Name")

        col = layout.column(align=False, heading="Passepartout")
        col.use_property_decorate = False
        row = col.row(align=True)
        sub = row.row(align=True)
        sub.prop(cam, "show_passepartout", text="")
        sub = sub.row(align=True)
        sub.active = cam.show_passepartout
        sub.prop(cam, "passepartout_alpha", text="")
        row.prop_decorator(cam, "passepartout_alpha")


class DATA_PT_arnold_camera_display_composition_guides(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Composition Guides"
    bl_parent_id = "DATA_PT_arnold_camera_display"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        cam = context.camera

        layout.prop(cam, "show_composition_thirds")

        col = layout.column(heading="Center", align=True)
        col.prop(cam, "show_composition_center")
        col.prop(cam, "show_composition_center_diagonal", text="Diagonal")

        col = layout.column(heading="Golden", align=True)
        col.prop(cam, "show_composition_golden", text="Ratio")
        col.prop(cam, "show_composition_golden_tria_a", text="Triangle A")
        col.prop(cam, "show_composition_golden_tria_b", text="Triangle B")

        col = layout.column(heading="Harmony", align=True)
        col.prop(cam, "show_composition_harmony_tri_a", text="Triangle A")
        col.prop(cam, "show_composition_harmony_tri_b", text="Triangle B")


classes = (
    DATA_PT_arnold_lens,
    DATA_PT_arnold_dof,
    DATA_PT_arnold_camera,
    DATA_PT_arnold_aperture,
    DATA_PT_arnold_camera_background_image,
    DATA_PT_arnold_camera_display,
    DATA_PT_arnold_camera_display_composition_guides,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
