from bpy.types import Material, World, PropertyGroup
from bpy.props import PointerProperty, EnumProperty

from ..nodes.base import ArnoldShaderTree

class ArnoldShader(PropertyGroup):
    node_tree: PointerProperty(name="Node Tree", type=ArnoldShaderTree)

def register():
    from bpy.utils import register_class
    register_class(ArnoldShader)

    Material.arnold = PointerProperty(
        name="Arnold Shader Settings",
        description="Arnold shader settings",
        type=ArnoldShader
        )
    
    World.arnold = PointerProperty(
        name="Arnold World Settings",
        description="Arnold World settings",
        type=ArnoldShader
        )

def unregister():
    from bpy.utils import unregister_class
    unregister_class(ArnoldShader)

    del Material.arnold