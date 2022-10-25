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
    preferences.register()
    from . import handlers
    handlers.register()
    from . import nodes
    nodes.register()
    #props.register()
    #engine.register()
    from . import operators
    operators.register()
    #from . import ui
    #ui.register()

def unregister():
    #from . import preferences, nodes, props, engine, operators, ui
    from . import preferences
    from . import handlers
    from . import operators
    from . import nodes
    #from . import ui
    preferences.unregister()
    handlers.unregister()
    nodes.unregister()
    #props.unregister()
    #engine.unregister()
    operators.unregister()
    #ui.unregister()