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
    #from . import preferences, nodes, props, engine, operators, ui
    from . import preferences
    from . import handlers
    from . import operators
    preferences.register()
    handlers.register()
    #nodes.register()
    #props.register()
    #engine.register()
    operators.register()
    #ui.register()

def unregister():
    #from . import preferences, nodes, props, engine, operators, ui
    from . import preferences
    from . import handlers
    from . import operators
    preferences.unregister()
    handlers.unregister()
    #nodes.unregister()
    #props.unregister()
    #engine.unregister()
    operators.unregister()
    #ui.unregister()