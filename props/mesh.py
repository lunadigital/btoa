import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty

class ArnoldShape(PropertyGroup):
    camera: BoolProperty(
        name="Camera",
        description="",
        default=True
    )

    shadow: BoolProperty(
        name="Shadow",
        description="",
        default=True
    )
    
    diffuse_transmission: BoolProperty(
        name="Diffuse Transmission",
        description="",
        default=True
    )
    
    specular_transmission: BoolProperty(
        name="Specular Transmission",
        description="",
        default=True
    )
    
    volume: BoolProperty(
        name="Volume",
        description="",
        default=True
    )
    
    diffuse_reflection: BoolProperty(
        name="Diffuse Reflection",
        description="",
        default=True
    )
    
    specular_reflection: BoolProperty(
        name="Specular Reflection",
        description="",
        default=True
    )
    
    sss: BoolProperty(
        name="SSS",
        description="",
        default=True
    )
    
    subdiv_type: EnumProperty(
        name="Subdivision Type",
        description="Defines the subdivision rule that will be applied to the polymesh at render time",
        items=[
            ('none', "None", ""),
            ('linear', "Linear", ""),
            ('catclark', "Catmull-Clark", "")
        ]
    )
    
    subdiv_iterations: IntProperty(
        name="Maximum Subdivisions",
        description="The maximum number of subdivision rounds applied to the mesh. When subdiv_pixel_error is 0 the number of rounds will be exact instead of a maximum",
        min=0,
        soft_max=3
    )
    
    subdiv_adaptive_error: FloatProperty(
        name="Adaptive Error",
        description="The maximum allowable difference for the chosen metric in the chosen space. The smaller the error, the closer to the limit surface a mesh will be and the less inter-frame \"popping\" when the subdivision level jumps, at the expense of using more polygons. A value of 0 disables adaptive subdivision, reverting to uniform subdivision, which can be more stable in animation",
        min=0,
        soft_max=1
    )
    
    subdiv_adaptive_metric: EnumProperty(
        name="Adaptive Metric",
        description="The metric used to determine the amount of error between a given subdivision level and the limit surface",
        items=[
            ('edge_length', "Edge Length", ""),
            ('flatness', "Flatness", ""),
            ('auto', "Auto", "")
        ],
        default='auto'
    )

    subdiv_adaptive_space: EnumProperty(
        name="Adaptive Space",
        description="Adaptive subdivision in raster space is problematic when instancing: A tessellation that is good for one instance will not be good for another further away. Using object space subdivision will ensure that all instances will subdivide to the proper level",
        items=[
            ('raster', "Raster", ""),
            ('object', "Object", "")
        ]
    )

    subdiv_frustum_ignore: BoolProperty(
        name="Frustum Culling",
        description="Disables subdivision frustum culling of the mesh"
    )

    subdiv_uv_smoothing: EnumProperty(
        name="UV Smoothing",
        description="The face-varying \"limit\" dPdu and dPdv vectors computed during subdivision are stored and used for shading instead of computing face-constant dPdu and dPdv vectors on the fly during shading. This can be useful for anisotropic shaders but has a storage cost",
        items=[
            ('linear', "Linear", ""),
            ('pin_borders', "Pin Borders", ""),
            ('pin_corners', "Pin Corners", ""),
            ('smooth', "Smooth", "")
        ],
        default='pin_corners'
    )

    subdiv_smooth_derivs: BoolProperty(
        name="Smooth Tangents",
        description="You may notice faceting appear in specular highlights when using anisotropy. It is possible to remove the faceted appearance by enabling smooth subdivision tangents. Take into account this requires a subdivision iteration of at least one in the polymesh to work"
    )

def register():
    bpy.utils.register_class(ArnoldShape)
    Object.arnold = PointerProperty(type=ArnoldShape)

def unregister():
    bpy.utils.unregister_class(ArnoldShape)
    del Object.arnold