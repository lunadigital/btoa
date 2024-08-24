import bpy

from ..preferences import ENGINE_ID
from ..utils import ui_utils

class ArnoldRenderPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    COMPAT_ENGINES = {ENGINE_ID}

    @classmethod
    def poll(cls, context):
        return ui_utils.arnold_is_active(context)

class ARNOLD_PT_sampling(ArnoldRenderPanel):
    bl_label = "Sampling"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        options = context.scene.arnold

        layout.prop(options, "aa_samples")

        col = self.layout.column()
        col.prop(options, "diffuse_samples")
        col.prop(options, "specular_samples")
        col.prop(options, "transmission_samples")
        col.prop(options, "sss_samples")
        col.prop(options, "volume_samples")
        col.enabled = (options.render_device == '0') # if using CPU
    
class ARNOLD_PT_denoising(ArnoldRenderPanel):
    bl_parent_id = 'ARNOLD_PT_sampling'
    bl_label = "Denoising"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.arnold, "use_denoiser", text="")
    
    def draw(self, context):
        options = context.scene.arnold
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(options, "denoiser")
        row.enabled = options.use_denoiser

class ARNOLD_PT_adaptive_sampling(ArnoldRenderPanel):
    bl_label = "Adaptive Sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.arnold, "use_adaptive_sampling", text="")

    def draw(self, context):
        options = context.scene.arnold
        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(options, "adaptive_aa_samples_max")
        col.prop(options, "adaptive_threshold")

        self.layout.enabled = context.scene.arnold.use_adaptive_sampling

class ARNOLD_PT_clamping(ArnoldRenderPanel):
    bl_label = "Clamping"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        options = context.scene.arnold
        layout = self.layout

        layout.use_property_split = True

        layout.prop(options, "indirect_sample_clamp")

        heading = layout.column(align=True, heading="Camera Sample Clamp")
        row = heading.row(align=True)
        row.prop(options, "clamp_aa_samples", text="")
        sub = row.row()
        sub.enabled = options.clamp_aa_samples
        sub.prop(options, "sample_clamp", text="")

        col = layout.column()
        col.enabled = options.clamp_aa_samples
        col.prop(options, "clamp_aovs")

class ARNOLD_PT_sample_filtering(ArnoldRenderPanel):
    bl_label = "Pixel Filter"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        options = context.scene.arnold
        layout = self.layout

        layout.use_property_split = True

        layout.prop(options, "filter_type")
        layout.prop(options, "filter_width")

class ARNOLD_PT_advanced_sampling(ArnoldRenderPanel):
    bl_label = "Advanced"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        options = context.scene.arnold

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(options, "lock_sampling_pattern")
       
        #col.prop(options, "low_light_threshold")

class ARNOLD_PT_ray_depth(ArnoldRenderPanel):
    bl_label = "Ray Depth"

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold

        layout.use_property_split = True

        col = layout.column()
        col.prop(options, "total_depth")
        col.prop(options, "diffuse_depth")
        col.prop(options, "specular_depth")
        col.prop(options, "transmission_depth")
        col.prop(options, "volume_depth")
        col.prop(options, "transparency_depth")

class ARNOLD_PT_rendering(ArnoldRenderPanel):
    bl_label = "Rendering"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold

        layout.use_property_split = True

        col = layout.column()
        col.prop(options, "bucket_size")
        col.prop(options, "bucket_scanning")
        col.prop(options, "parallel_node_init")
        col.prop(options, "threads")

class ARNOLD_PT_motion_blur(ArnoldRenderPanel):
    bl_label = "Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.arnold, "enable_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold

        layout.use_property_split = True

        col = layout.column()
        col.enabled = options.enable_motion_blur
        col.prop(options, "deformation_motion_blur")
        col.prop(options, "camera_motion_blur")
        col.prop(options, "motion_keys")

class ARNOLD_PT_motion_blur_shutter(ArnoldRenderPanel):
    bl_parent_id = 'ARNOLD_PT_motion_blur'
    bl_label = "Shutter"

    def draw(self, context):
        options = context.scene.arnold

        self.layout.use_property_split = True

        col = self.layout.column()
        col.enabled = options.enable_motion_blur
        col.prop(options, "shutter_length")
        
        col = self.layout.column()
        col.enabled = False
        col.prop(options, "shutter_start")
        col.prop(options, "shutter_end")

class ARNOLD_PT_film(ArnoldRenderPanel):
    bl_label = "Film"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.prop(context.scene.render, "film_transparent")

class ARNOLD_PT_feature_overrides(ArnoldRenderPanel):
    bl_label = "Feature Overrides"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold

        layout.prop(options, "ignore_textures")
        layout.prop(options, "ignore_shaders")
        layout.prop(options, "ignore_atmosphere")
        layout.prop(options, "ignore_lights")
        layout.prop(options, "ignore_shadows")
        layout.prop(options, "ignore_subdivision")
        layout.prop(options, "ignore_displacement")
        layout.prop(options, "ignore_bump")
        layout.prop(options, "ignore_smoothing")
        layout.prop(options, "ignore_motion")
        layout.prop(options, "ignore_dof")
        layout.prop(options, "ignore_sss")

classes = (
    ARNOLD_PT_sampling,
    ARNOLD_PT_denoising,
    ARNOLD_PT_adaptive_sampling,
    ARNOLD_PT_clamping,
    ARNOLD_PT_sample_filtering,
    ARNOLD_PT_advanced_sampling,
    ARNOLD_PT_ray_depth,
    ARNOLD_PT_motion_blur,
    ARNOLD_PT_motion_blur_shutter,
    ARNOLD_PT_rendering,
    ARNOLD_PT_film,
    ARNOLD_PT_feature_overrides,
)

def draw_device(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    options = context.scene.arnold

    if context.engine == 'ARNOLD':
        col = layout.column()
        col.prop(options, "render_device", text="Device")

def register():
    from ..utils import register_utils as utils
    utils.register_classes(classes)

    bpy.types.RENDER_PT_context.append(draw_device)

def unregister():
    from ..utils import register_utils as utils
    utils.unregister_classes(classes)

    bpy.types.RENDER_PT_context.remove(draw_device)