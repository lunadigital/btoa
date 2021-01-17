bl_info = {
    "name": "Arnold Render Engine",
    "description": "Unofficial Arnold renderer integration",
    "author": "Luna Digital, Ltd.",
    "version": (0, 0, 1),
    "blender": (2, 83, 0),
    "category": "Render"
}

def register():
    from . import addon_preferences
    addon_preferences.register()

    from . import engine
    engine.register()


def unregister():
    from . import addon_preferences
    addon_preferences.unregister()

    from . import engine
    engine.unregister()