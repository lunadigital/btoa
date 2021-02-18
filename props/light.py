import bpy
from bpy.types import Scene, PropertyGroup, Light
from bpy.props import BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, PointerProperty, EnumProperty

from .. import btoa

class ArnoldLight(PropertyGroup):
    # Common properties
    intensity: FloatProperty(
        name="Intensity",
        description="",
        soft_min=0,
        soft_max=10,
        default=1
        )
    exposure: FloatProperty(
        name="Exposure",
        description="",
        soft_min=0,
        soft_max=10
        )
    cast_shadows: BoolProperty(
        name="Cast Shadows",
        description="",
        default=True
        )
    cast_volumetric_shadows: BoolProperty(
        name="Cast Volumetric Shadows",
        description="",
        default=True
        )
    shadow_density: FloatProperty(
        name="Shadow Density",
        description="",
        default=1
        )
    shadow_color: FloatVectorProperty(
        name="Shadow Color",
        description="",
        size=3,
        min=0,
        max=1,
        subtype='COLOR'
        )
    samples: IntProperty(
        name="Samples",
        description="",
        min=0,
        max=100,
        default=1
        )
    normalize: BoolProperty(
        name="Normalize",
        description="",
        default=True
        )
    #affect_diffuse: BoolProperty(
    #    name="Emit Diffuse",
    #    description="",
    #    default=True
    #    )
    #affect_specular: BoolProperty(
    #    name="Emit Specular",
    #    description="",
    #    default=True
    #    )
    #affect_volumetrics: BoolProperty(
    #    name="Affect Volumetrics",
    #    description="",
    #    default=True
    #    )
    camera: FloatProperty(
        name="Camera",
        description="",
        min=0,
        soft_max=1,
        default=1
        )
    diffuse: FloatProperty(
        name="Diffuse",
        description="",
        min=0,
        soft_max=1,
        default=1
        )
    specular: FloatProperty(
        name="Specular",
        description="",
        min=0,
        soft_max=1,
        default=1
        )
    sss: FloatProperty(
        name="SSS",
        description="",
        min=0,
        soft_max=1,
        default=1
        )
    indirect: FloatProperty(
        name="Indirect",
        description="",
        min=0,
        soft_max=1,
        default=1
        )
    max_bounces: IntProperty(
        name="Max Bounces",
        description="",
        min=0,
        default=999
        )
    #volume_samples: IntProperty(
    #    name="Volume Samples",
    #    subtype='UNSIGNED',
    #    min=0,
    #    default=2
    #    )
    volume: FloatProperty(
       name="Volume",
        min=0,
        soft_max=1,
        default=1
        )

    def get_type(self):
        light = self.id_data
        return list(btoa.AI_LIGHT_TYPE).index(light.type)

    def set_type(self, value):
        light = self.id_data
        light.type = list(btoa.AI_LIGHT_TYPE)[value]
    
    #('skydome_light', "Skydome", "Skydome light", 3),
    #('mesh_light', "Mesh", "Mesh light", 6),
    #('photometric_light', "Photometric", "Photometric light", 7),
    type: EnumProperty(
        name="Type",
        description="",
        items=[
            ('point_light', "Point", "Point light"),
            ('distant_light', "Distant", "Distant light"),
            ('spot_light', "Spot", "Spot light"),
            ('area_light', "Area", "Area Light"),
        ],
        get=get_type,
        set=set_type
        )

    # Directional light attributes
    angle: FloatProperty(
        name="Angle",
        description="",
        min=0,
        max=180
        )
    
    # Spot light attributes
    aspect_ratio: FloatProperty(
        name="Aspect Ratio",
        description="",
        min=0,
        max=1,
        default=1
        )
    lens_radius: FloatProperty(
        name="Lens Radius",
        description="",
        min=0,
        soft_max=2
        )
    spot_roundness: FloatProperty(
        name="Roundness",
        description="",
        min=0,
        max=1,
        default=1
        )
    
    # Area light attributes
    spread: FloatProperty(
        name="Spread",
        description="",
        min=0,
        soft_max=1,
        default=1
        )
    resolution: IntProperty(
        name="Resolution",
        description="",
        min=2,
        default=512
        )
    soft_edge: FloatProperty(
        name="Soft Edge",
        description="",
        min=0,
        max=1
        )
    area_roundness: FloatProperty(
        name="Roundness",
        description="",
        min=0,
        max=1
        )

    def get_shape_type(self):
        light = self.id_data
        return list(btoa.AI_AREALIGHT_TYPE).index(light.shape)

    def set_shape_type(self, value):
        light = self.id_data
        light.shape = list(btoa.AI_AREALIGHT_TYPE)[value]

    shape: EnumProperty(
        name="Light Shape",
        description="",
        items=[
            ('quad_light', "Quad", "Quad light"),
            ('disk_light', "Disk", "Disk light"),
            ('cylinder_light', "Cylinder", "Cylinder light"),
        ],
        get=get_shape_type,
        set=set_shape_type
        )

def register():
    bpy.utils.register_class(ArnoldLight)
    Light.arnold = PointerProperty(type=ArnoldLight)

def unregister():
    bpy.utils.unregister_class(ArnoldLight)
    del Light.arnold