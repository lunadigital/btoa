from bpy.types import Material, PropertyGroup
from bpy.props import PointerProperty

from ..nodes.base import ArnoldShaderTree

class ArnoldMaterialProps(PropertyGroup):
    node_tree: PointerProperty(name="Node Tree", type=ArnoldShaderTree)

def register():
    from bpy.utils import register_class
    register_class(ArnoldMaterialProps)

    Material.arnold = PointerProperty(
        name="Arnold Material Settings",
        description="Arnold material settings",
        type=ArnoldMaterialProps
        )

def unregister():
    from bpy.utils import unregister_class
    unregister_class(ArnoldMaterialProps)

    del Material.arnold