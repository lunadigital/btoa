import bpy

bl_info = {
    "name": "Arnold Render Engine (BtoA)",
    "description": "Community-developed Arnold renderer integration",
    "author": "Luna Digital, Ltd.",
    "version": (0, 5, 0),
    "blender": (3, 0, 0),
    "category": "Render"
}

def register():
    from . import preferences
    preferences.register()

    from . import handlers, props, nodes, operators
    handlers.register()
    nodes.register()
    props.register()
    operators.register()

    #engine.register()
    #ui.register()

def unregister():
    from . import preferences, handlers, nodes, operators
    preferences.unregister()
    handlers.unregister()
    nodes.unregister()
    props.unregister()
    #engine.unregister()
    operators.unregister()
    #ui.unregister()