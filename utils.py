def register_classes(classes):
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

def unregister_classes(classes):
    from bpy.utils import unregister_class
    for c in reversed(classes):
        unregister_class(c)