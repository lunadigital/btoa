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
    from . import preferences #, nodes, props, engine, operators, ui
    preferences.register()
    #nodes.register()
    #props.register()
    #engine.register()
    #operators.register()
    #ui.register()

def unregister():
    from . import preferences #, nodes, props, engine, operators, ui
    preferences.unregister()
    #nodes.unregister()
    #props.unregister()
    #engine.unregister()
    #operators.unregister()
    #ui.unregister()