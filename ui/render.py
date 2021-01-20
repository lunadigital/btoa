import bpy
from .. import engine

class ARNOLD_PT_sampling(bpy.types.Panel):
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}
    bl_idname = "ARNOLD_PT_sampling"
    bl_label = "Sampling"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

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

    def draw_header(self, context):
        self.layout.prop(context.scene.arnold_options, "use_adaptive_sampling", text="")

    def draw(self, context):
        options = context.scene.arnold_options

        self.layout.use_property_split = True

        col = self.layout.column()
        col.prop(options, "adaptive_aa_samples_max")
        col.prop(options, "adaptive_threshold")

        self.layout.enabled = context.scene.arnold_options.use_adaptive_sampling

def register():
    bpy.utils.register_class(ARNOLD_PT_sampling)
    bpy.utils.register_class(ARNOLD_PT_advanced_sampling)
    bpy.utils.register_class(ARNOLD_PT_adaptive_sampling)

def unregister():
    bpy.utils.unregister_class(ARNOLD_PT_sampling)
    bpy.utils.unregister_class(ARNOLD_PT_advanced_sampling)
    bpy.utils.unregister_class(ARNOLD_PT_adaptive_sampling)