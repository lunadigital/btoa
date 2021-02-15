bl_info = {
    "name": "Arnold Render Engine",
    "description": "Unofficial Arnold renderer integration",
    "author": "Luna Digital, Ltd.",
    "version": (0, 0, 6),
    "blender": (2, 83, 0),
    "category": "Render"
}

def register():
    from . import addon_preferences
    addon_preferences.register()

    from . import props
    from . import engine
    from . import operators
    from . import nodes
    from . import ui
    nodes.register()
    props.register()
    engine.register()
    operators.register()
    ui.register()


def unregister():
    from . import addon_preferences
    from . import props
    from . import engine
    from . import operators
    from . import nodes
    from . import ui
    addon_preferences.unregister()
    nodes.unregister()
    props.unregister()
    engine.unregister()
    operators.unregister()
    ui.unregister()