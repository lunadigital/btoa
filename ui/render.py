import bpy
from .. import engine

class ARNOLD_PT_sampling(bpy.types.Panel):
    bl_idname = "ARNOLD_PT_sampling"
    bl_label = "Sampling"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

    def draw(self, context):
        options = context.scene.arnold_options

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(options, "aa_samples")
        col.prop(options, "diffuse_samples")
        col.prop(options, "specular_samples")
        col.prop(options, "transmission_samples")
        col.prop(options, "sss_samples")
        col.prop(options, "volume_samples")

class ARNOLD_PT_advanced_sampling(bpy.types.Panel):
    bl_parent_id = ARNOLD_PT_sampling.bl_idname
    bl_idname = "ARNOLD_PT_advanced_sampling"
    bl_label = "Advanced"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        options = context.scene.arnold_options

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(options, "aa_seed")
        col.prop(options, "sample_clamp")
        col.prop(options, "clamp_aovs")
        col.prop(options, "indirect_sample_clamp")
        col.prop(options, "low_light_threshold")
    
class ARNOLD_PT_adaptive_sampling(bpy.types.Panel):
    bl_parent_id = ARNOLD_PT_sampling.bl_idname
    bl_idname = "ARNOLD_PT_adaptive_sampling"
    bl_label = "Adaptive Sampling"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.arnold_options, "use_adaptive_sampling", text="")

    def draw(self, context):
        options = context.scene.arnold_options

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(options, "adaptive_aa_samples_max")
        col.prop(options, "adaptive_threshold")

        self.layout.enabled = context.scene.arnold_options.use_adaptive_sampling

class ARNOLD_PT_ray_depth(bpy.types.Panel):
    bl_idname = "ARNOLD_PT_ray_depth"
    bl_label = "Ray Depth"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold_options

        layout.use_property_split = True

        col = layout.column()
        col.prop(options, "total_depth")
        col.prop(options, "diffuse_depth")
        col.prop(options, "specular_depth")
        col.prop(options, "transmission_depth")
        col.prop(options, "volume_depth")
        col.prop(options, "transparency_depth")

class ARNOLD_PT_rendering(bpy.types.Panel):
    bl_idname = "ARNOLD_PT_rendering"
    bl_label = "Rendering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold_options

        layout.use_property_split = True

        col = layout.column()
        col.prop(options, "bucket_size")
        col.prop(options, "bucket_scanning")
        col.prop(options, "parallel_node_init")
        col.prop(options, "threads")

class ARNOLD_PT_motion_blur(bpy.types.Panel):
    bl_idname = "ARNOLD_PT_motion_blur"
    bl_label = "Motion Blur"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

    def draw_header(self, context):
        self.layout.prop(context.scene.arnold_options, "enable_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        options = context.scene.arnold_options

        layout.use_property_split = True

        col = layout.column()
        col.enabled = options.enable_motion_blur
        col.prop(options, "deformation_motion_blur")
        col.prop(options, "camera_motion_blur")
        col.prop(options, "motion_keys")

class ARNOLD_PT_motion_blur_shutter(bpy.types.Panel):
    bl_parent_id = ARNOLD_PT_motion_blur.bl_idname
    bl_idname = "ARNOLD_PT_motion_blur_shutter"
    bl_label = "Shutter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        options = context.scene.arnold_options

        self.layout.use_property_split = True

        col = self.layout.column()
        col.enabled = options.enable_motion_blur
        col.prop(options, "shutter_length")
        
        col = self.layout.column()
        col.enabled = False
        col.prop(options, "shutter_start")
        col.prop(options, "shutter_end")

classes = (
    ARNOLD_PT_sampling,
    ARNOLD_PT_advanced_sampling,
    ARNOLD_PT_adaptive_sampling,
    ARNOLD_PT_ray_depth,
    ARNOLD_PT_motion_blur,
    ARNOLD_PT_motion_blur_shutter,
    ARNOLD_PT_rendering
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)