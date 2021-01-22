import bpy
from bpy.types import Scene, PropertyGroup, Camera
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty, EnumProperty

class ArnoldOptions(PropertyGroup):
    # Sampling
    use_adaptive_sampling: BoolProperty()
    aa_samples: IntProperty(name="AA Samples", min=0, default=3)
    diffuse_samples: IntProperty(name="Diffuse Samples", min=0, default=2)
    specular_samples: IntProperty(name="Specular Samples", min=0, default=2)
    transmission_samples: IntProperty(name="Transmission Samples", min=0, default=2)
    sss_samples: IntProperty(name="SSS Samples", min=0, default=2)
    volume_samples: IntProperty(name="Volume Samples", min=0, default=2)
    aa_seed: IntProperty(name="AA Seed", min=0, default=1)
    sample_clamp: IntProperty(name="Sample Clamp", min=0, default=10)
    clamp_aovs: BoolProperty(name="Clamp AOVs")
    indirect_sample_clamp: IntProperty(name="Indirect Sample Clamp", min=0, default=10)
    low_light_threshold: FloatProperty(name="Low Light Threshold", min=0, default=0.001)
    adaptive_aa_samples_max: IntProperty(name="AA Samples Max", min=0, default=0)
    adaptive_threshold: FloatProperty(name="Adaptive Threshold", min=0, default=0.05)

    # Ray depth
    total_depth: IntProperty(name="Total Depth", min=0, default=10)
    diffuse_depth: IntProperty(name="Diffuse Depth", min=0, default=1)
    specular_depth: IntProperty(name="Specular Depth", min=0, default=1)
    transmission_depth: IntProperty(name="Transmission Depth", min=0, default=10)
    volume_depth: IntProperty(name="Volume Depth", min=0)
    transparency_depth: IntProperty(name="Transparency Depth", min=0, default=10)

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

class ArnoldCamera(PropertyGroup):
    # Basic lens settings
    camera_type: EnumProperty(
        name="Type",
        items=[
            ('cyl_camera', "Cylindrical ", "Cylindrical "),
            ('fisheye_camera', "Fisheye", "Fisheye"),
            ('ortho_camera', "Orthographic", "Orthographic"),
            ('persp_camera', "Perspective", "Perspective"),
            ('spherical_camera', "Spherical", "Spherical"),
            ('vr_camera', "VR", "VR"),
            ('uv_camera', "UV", "UV"),
        ],
        default='persp_camera'
    )

    exposure: FloatProperty(name="Exposure")

    # DOF
    enable_dof: BoolProperty(name="Enable DOF")
    focus_distance: FloatProperty(name="Focus Distance")
    aperture_size: FloatProperty(name="Size", min=0)
    aperture_blades: IntProperty(name="Blades", min=0)
    aperture_rotation: FloatProperty(name="Rotation")
    aperture_blade_curvature: FloatProperty(name="Curvature", min=-1, max=1)
    aperture_aspect_ratio: FloatProperty(name="Aspect Ratio", min=0, default=1)
    flat_field_focus: BoolProperty(name="Flat Field Focus")

    # Shutter
    shutter_start: FloatProperty(name="Shutter: Start")
    shutter_end: FloatProperty(name="Shutter: Stop")

    shutter_type: EnumProperty(
        name="Shutter Type",
        items=[
            ('box', "Box", "Box"),
            ('triangle', "Triangle", "Triangle"),
            #('curve', "Curve", "Curve")
        ],
        default='box'
    )

    rolling_shutter: EnumProperty(
        name="Rolling Shutter",
        items=[
            ('off', "Off", "Off"),
            ('top', "Top", "Top"),
            ('bottom', "Bottom", "Bottom"),
            ('left', "Left", "Left"),
            ('right', "Right", "Right")
        ],
        default='off'
    )
    rolling_shutter_duration: FloatProperty(name="Rolling Shutter: Duration")

def register():
    bpy.utils.register_class(ArnoldOptions)
    bpy.utils.register_class(ArnoldCamera)
    Scene.arnold_options = PointerProperty(type=ArnoldOptions)
    Camera.arnold = PointerProperty(type=ArnoldCamera)

def unregister():
    del Camera.arnold
    del Scene.arnold_options
    bpy.utils.unregister_class(ArnoldCamera)
    bpy.utils.unregister_class(ArnoldOptions)