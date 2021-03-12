from bpy.types import Material, PropertyGroup
from bpy.props import PointerProperty

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

def unregister():
    from bpy.utils import unregister_class
    unregister_class(ArnoldShader)

    del Material.arnold