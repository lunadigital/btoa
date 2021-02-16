import bpy
from bpy.app.handlers import persistent

from .engine import ArnoldRenderEngine

subscription_owner = object()

def toggle_blender_color_management(*args):
    options = bpy.context.scene.arnold_options
    engine = bpy.context.scene.render.engine
    display_settings = bpy.context.scene.display_settings

    if engine == ArnoldRenderEngine.bl_idname:
        options.display_device_cache = display_settings.display_device
        display_settings.display_device = 'None'
    else:
        display_settings.display_device = options.display_device_cache

def subscribe(subscription_owner):
    subscribe_to = bpy.types.RenderSettings, "engine"

    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=subscription_owner,
        args=("a", "b", "c"),
        notify=toggle_blender_color_management,
        options={"PERSISTENT",}
    )

@persistent
def load_display_device_handler(dummy):
    subscribe(subscription_owner)

def register():
    handlers = bpy.app.handlers

    load_display_device_handler(None)

    if load_display_device_handler not in handlers.load_post:
        handlers.load_post.append(load_display_device_handler)

def unregister():
    handlers = bpy.app.handlers

    if load_display_device_handler in handlers.load_post:
        handlers.load_post.remove(load_display_device_handler)