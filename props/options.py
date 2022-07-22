import bpy
from bpy.types import Scene, PropertyGroup, Camera
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty, EnumProperty, StringProperty

class AiSpaceDataProperties(PropertyGroup):
    shader_type: EnumProperty(
        name="Shader Type",
        items=[
            ('OBJECT', "Object", "Object shaders", "OBJECT_DATA", 0),
            ('WORLD', "World", "World shaders", "WORLD_DATA", 1),
        ]
    )
   
class ArnoldOptions(PropertyGroup):
    # Sampling
    aa_samples: IntProperty(
        name="Camera (AA)",
        description="Supersampling control over the number of rays per pixel that will be traced from the camera. The higher the number of samples, the better the anti-aliasing quality, and the longer the render times. The exact number of rays per pixel is the square of this value",
        min=0,
        default=3
        )
    diffuse_samples: IntProperty(
        name="Diffuse",
        description="Controls the number of rays fired when computing the reflected indirect-radiance integrated over the hemisphere. The exact number of hemispherical rays is the square of this value. Increase this number to reduce the indirect diffuse noise",
        min=0,
        default=2
        )
    specular_samples: IntProperty(
        name="Specular",
        description="Controls the number of rays fired when computing the reflected indirect-radiance integrated over the hemisphere weighted by a specular BRDF. The exact number of rays is the square of this value. Increase this number to reduce the indirect specular noise",
        min=0,
        default=2
        )
    transmission_samples: IntProperty(
        name="Transmission",
        description="Controls the number of samples used to simulate the microfacet-based transmission evaluations. Increase this value to resolve any noise in the transmission",
        min=0,
        default=2
        )
    sss_samples: IntProperty(
        name="SSS",
        description="This value controls the number of lighting samples (direct and indirect) that will be taken to estimate lighting within a radius of the point being shaded to compute sub-surface scattering. Higher values produce a cleaner solution but will take longer to render",
        min=0,
        default=2
        )
    volume_samples: IntProperty(
        name="Volume",
        description="Controls the number of sample rays that get fired to compute indirect lighting of the volume",
        min=0,
        default=2
        )

    clamp_aa_samples: BoolProperty(
        name="Clamp AA Samples",
        description="Enable/disable clamping"
    )
    sample_clamp: FloatProperty(
        name="AA Clamp Value",
        description="If enabled, this control will clamp pixel samples to this specified maximum value. This can make it easier to anti-alias certain high-dynamic-range effects such as bright motion-blurred specular streaks (at the cost of reduced contrast)",
        min=0,
        default=10
        )
    clamp_aovs: BoolProperty(
        name="Affect AOVs",
        description="With this control enabled the pixel samples of the AOVs will also be clamped. AOV clamping will affect every RGB and RGBA (except the A component) AOV. Currently, there is no way to tell Arnold which AOV's to clamp and which ones to preserve"
        )
    indirect_sample_clamp: FloatProperty(
        name="Indirect Sample Clamp",
        description="The threshold to clamp away fireflies from indirect light samples and reduce noise. This works similarly to AA_sample_clamp but preserves specular highlights from direct lighting. Lower values result in more aggressive noise reduction, possibly at the expense of dynamic range",
        min=0,
        default=10
        )
    low_light_threshold: FloatProperty(
        name="Low Light Threshold",
        description="Raising this value can speed up rendering by allowing Arnold to ignore tracing a shadow ray for light samples whose light contribution is below a certain value. The point of low_light_threshold is to save casting shadow rays when Arnold knows that the error from not casting that ray is below a certain amount. This makes sense because below a certain threshold there will be no perceptible difference between shadowed and unshadowed areas",
        min=0,
        default=0.001
        )
    use_adaptive_sampling: BoolProperty()
    adaptive_aa_samples_max: IntProperty(
        name="Max Camera (AA)",
        description="Sets the maximum amount of supersampling. It controls the per-pixel maximum sampling rate and is equivalent to the units used by AA_samples. Adaptive sampling is enabled when AA_samples_max > Camera (AA) samples and Camera (AA) samples >= 2. Scenes with a large amount of depth of field or motion blur may require higher Max. Camera (AA) values. This parameter can also help with 'buzzing' speculars and hair shading as well",
        min=0, 
        default=20
        )
    adaptive_threshold: FloatProperty(
        name="Adaptive Threshold",
        description="The threshold which triggers/terminates adaptive-AA. This value controls how sensitive to noise the adaptive sampling algorithm gets. Lower numbers will detect more noise. The default value should work well for most scenes",
        min=0,
        default=0.015,
        precision=3
        )
    
    lock_sampling_pattern: BoolProperty(
        name="Lock Sampling Pattern",
        description=""
    )

    filter_type: EnumProperty(
        name="Filter Type",
        items=[
            ("blackman_harris_filter", "Blackman-Harris", "Blackman-Harris"),
            ("box_filter", "Box", "Box"),
            ("catrom_filter", "Catrom", "Catrom"),
            ("closest_filter", "Closest", "Closest"),
            ("contour_filter", "Contour", "Contour"),
            ("difference_filter", "Difference", "Difference"),
            ("farthest_filter", "Farthest", "Farthest"),
            ("gaussian_filter", "Gaussian", "Gaussian"),
            ("heatmap_filter", "Heatmap", "Heatmap"),
            ("mitnet_filter", "Mitnet", "Mitnet"),
            ("sinc_filter", "Sinc", "Sinc"),
            ("triangle_filter", "Triangle", "Triangle"),
            ("variance_filter", "Variance", "Variance"),
        ],
        default="gaussian_filter"
    )

    filter_width: FloatProperty(
        name="Width",
        description="",
        default=2
    )

    # Ray depth
    total_depth: IntProperty(
        name="Total",
        description="Specifies the total maximum recursion depth of any ray in the scene (diffuse + transmission + specular <= Total)",
        min=0,
        default=10
        )
    diffuse_depth: IntProperty(
        name="Diffuse",
        description="Defines the maximum ray diffuse depth bounces. Zero diffuse is equal to disabling diffuse illumination. Increasing the depth will add more bounced light to the scene, which can be especially noticeable in interiors",
        min=0,
        default=1
        )
    specular_depth: IntProperty(
        name="Specular",
        description="Defines the maximum number of times a ray can be specularly reflected. Scenes with many specular surfaces may require higher values to look correct. A minimum value of 1 is necessary to get any specular reflections",
        min=0,
        default=1
        )
    transmission_depth: IntProperty(
        name="Transmission",
        description="The maximum number of times a ray can be refracted. Scenes with many refractive surfaces may require higher values to look correct",
        min=0,
        default=8
        )
    volume_depth: IntProperty(
        name="Volume",
        description="This parameter sets the number of multiple scattering bounces within a volume. This is useful when rendering volumes such as clouds for which multiple scattering has a large influence on their appearance",
        min=0
        )
    transparency_depth: IntProperty(
        name="Transparency",
        description="The number of allowed transparency hits. With 0 objects will be treated as opaque",
        min=0,
        default=10
        )

    # Rendering
    bucket_size: IntProperty(
        name="Bucket Size", 
        description="The size of the image buckets. Bigger buckets use more memory, while smaller buckets may perform redundant computations and filtering and thus render slower but give initial faster feedback",
        min=2,
        default=64
        )
    bucket_scanning: EnumProperty(
        name="Bucket Scanning",
        description="Specifies the spatial order in which the image buckets (i.e. threads) will be processed. By default, buckets start in the center of the image and proceed outwards in a spiral pattern",
        items=[
            ('top', "Top", "Top"),
            ('left', "Left", "Left"),
            ('random', "Random", "Random"),
            ('spiral', "Spiral", "Spiral"),
            ('hilbert', "Hilbert", "Hilbert"),
        ],
        default='spiral'
        )
    parallel_node_init: BoolProperty(
        name="Parallel Node Init",
        description="Enables parallel initialization of all scene nodes",
        default=True
        )
    threads: IntProperty(
        name="Threads",
        description="The number of threads used for rendering. Set it to zero to autodetect and use as many threads as cores in the system. Negative values indicate how many cores not to use, so that -3, for instance, will use 29 threads on a 32 logical core machine. Negative values are useful when you want to reserve some of the CPU for non-Arnold tasks"
        )

    # Motion blur
    # Assumes motion blur is centered on frame
    def update_shutter_limits(self, context):
        options = context.scene.arnold
        options.shutter_start = -options.shutter_length / 2
        options.shutter_end = options.shutter_length / 2
        
    enable_motion_blur: BoolProperty(
        name="Enable Motion Blur",
        description=""
        )
    # instantaneous_shutter
    deformation_motion_blur: BoolProperty(
        name="Deformation",
        description=""
    )
    camera_motion_blur: BoolProperty(
        name="Camera",
        description="",
        default=True
        )
    # shaders_motion_blur
    motion_keys: IntProperty(
        name="Keys",
        description="",
        min=2,
        default=2
        )
    shutter_length: FloatProperty(
        name="Length",
        description="",
        min=0,
        max=1,
        default=0.5,
        update=update_shutter_limits
        )
    shutter_start: FloatProperty(
        name="Start",
        description="",
        default=-0.25
        )
    shutter_end: FloatProperty(
        name="End",
        description="",
        default=0.25
        )

    # Render device
    render_device: EnumProperty(
        name="Render Device",
        description="",
        items=[
            ("0", "CPU", "CPU"),
            ("1", "GPU", "GPU"),
        ]
    )

    # To save default display device for color management
    display_device_cache: StringProperty(
        name="Display Device Cache",
        default="sRGB"
    )

    space_data: PointerProperty(type=AiSpaceDataProperties)

    viewport_scale: EnumProperty(
        name="Viewport Scale",
        items=[
            ("1.0", "100%", "100% Render Resolution"),
            ("0.75", "75%", "75% Render Resolution"),
            ("0.5", "50%", "50% Render Resolution"),
            ("0.25", "25%", "25% Render Resolution")
        ],
        default="1.0"
    )

    enable_denoising: BoolProperty(name="Enable Denoising")
    denoiser: EnumProperty(
        name="Denoiser",
        items=[
            ('imager_denoiser_oidn', "OpenImageDenoise", "Use OpenImageDenoise AI denoiser running on the CPU"),
            ('imager_denoiser_optix', "OptiX", "Use the OptiX AI denoiser with GPU acceleration, only available on NVIDIA GPUs")
        ]
    )

    # Ignore flags
    ignore_textures: BoolProperty(name="Ignore Textures")
    ignore_shaders: BoolProperty(name="Ignore Shaders")
    ignore_atmosphere: BoolProperty(name="Ignore Atmosphere")
    ignore_lights: BoolProperty(name="Ignore Lights")
    ignore_shadows: BoolProperty(name="Ignore Shadows")
    ignore_subdivision: BoolProperty(name="Ignore Subdivision")
    ignore_displacement: BoolProperty(name="Ignore Displacement")
    ignore_bump: BoolProperty(name="Ignore Bump")
    ignore_motion: BoolProperty(name="Ignore Motion")
    ignore_dof: BoolProperty(name="Ignore Depth of Field")
    ignore_smoothing: BoolProperty(name="Ignore Normal Smoothing")
    ignore_sss: BoolProperty(name="Ignore Sub-Surface Scattering")
    # ignore_operators: BoolProperty(name="Ignore Operators")
    ignore_imagers: BoolProperty(name="Ignore Imagers")
    # force_shader_assignments

classes = (
    AiSpaceDataProperties,
    ArnoldOptions,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    Scene.arnold = PointerProperty(type=ArnoldOptions)

def unregister():
    del Scene.arnold

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)