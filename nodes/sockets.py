from bpy.types import NodeSocket

class ArnoldNodeSocketProperty(NodeSocket):
    pass

classes = (
    ArnoldNodeSocketProperty
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)