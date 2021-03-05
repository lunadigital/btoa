import bpy
from . import environ as aienv

bl_info = {
    "name": "Arnold Render Engine",
    "description": "Unofficial Arnold renderer integration",
    "author": "Luna Digital, Ltd.",
    "version": (0, 2, 6),
    "blender": (2, 83, 0),
    "category": "Render"
}

def register():
    from . import addon_preferences
    addon_preferences.register()

    aienv.configure_arnold_environment()
    aienv.configure_ocio()

    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.arnold_path != "":
        aienv.configure_plugins()

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

        prefs.full_unregister = True

def unregister():
    prefs = bpy.context.preferences.addons[__package__].preferences

    if prefs.arnold_path != "" and prefs.full_unregister:
        from . import props
        from . import engine
        from . import operators
        from . import nodes
        from . import ui
        nodes.unregister()
        props.unregister()
        engine.unregister()
        operators.unregister()
        ui.unregister()

        aienv.remove_plugins()
    else:
        prefs.full_unregister = False
          
    from . import addon_preferences
    addon_preferences.unregister()

    aienv.reset_ocio()