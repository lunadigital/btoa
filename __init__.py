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
    '''
    We need to register preferences before importing any other modules so
    anything that requires `import arnoldserver` will work properly.
    '''
    from . import preferences
    preferences.register()

    from . import handlers, props, nodes, operators, ui
    handlers.register()
    nodes.register()
    props.register()
    operators.register()
    ui.register()
    #engine.register()

def unregister():
    from . import preferences, handlers, nodes, operators, ui
    preferences.unregister()
    handlers.unregister()
    nodes.unregister()
    props.unregister()
    operators.unregister()
    ui.unregister()
    #engine.unregister()