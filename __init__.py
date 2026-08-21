import bpy
from .utils import sdk_utils

bl_info = {
    "name": "Arnold Render Engine (BtoA)",
    "description": "Community-developed Arnold renderer integration",
    "author": "Luna Digital, Ltd.",
    "version": (0, 6, 2),
    "blender": (4, 2, 0),
    "category": "Render"
}


def register():
    '''
    We need to register preferences before importing any other modules so
    anything that requires `import arnoldserver` will work properly.
    '''
    from . import preferences
    preferences.register()

    if sdk_utils.is_arnoldserver_installed():
        from . import handlers, props, nodes, operators, ui, engine
        handlers.register()
        nodes.register()
        props.register()
        operators.register()
        ui.register()
        engine.register()


def unregister():
    if sdk_utils.is_arnoldserver_installed():
        from . import handlers, props, nodes, operators, ui, engine
        engine.unregister()
        ui.unregister()
        operators.unregister()
        props.unregister()
        nodes.unregister()
        handlers.unregister()

    from . import preferences
    preferences.unregister()
