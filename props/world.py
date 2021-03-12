from bpy.types import World, PropertyGroup
from bpy.props import PointerProperty

from ..nodes.base import ArnoldShaderTree
from .light import ArnoldLight

class ArnoldWorld(PropertyGroup):
    node_tree: PointerProperty(name="Node Tree", type=ArnoldShaderTree)
    data: PointerProperty(name="Light Settings", type=ArnoldLight)

def register():
    from bpy.utils import register_class
    register_class(ArnoldWorld)
    
    World.arnold = PointerProperty(
        name="Arnold World Settings",
        description="Arnold World settings",
        type=ArnoldWorld
    )

def unregister():
    from bpy.utils import unregister_class
    unregister_class(ArnoldWorld)

    del World.arnold