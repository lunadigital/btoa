import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, IntProperty, BoolProperty

import os
import sys

def arnold_env_exists():
    if "ARNOLD_ROOT" in os.environ:
        return True

    return False

def get_default_ocio_config():
    blender_root = os.path.dirname(bpy.app.binary_path)
    version = "{major}.{minor}".format(
        major=bpy.app.version[0],
        minor=bpy.app.version[1]
    )

    return os.path.join(blender_root, version, "datafiles", "colormanagement", "config.ocio")

def configure_plugins():
    addon_root = os.path.dirname(os.path.abspath(__file__))
    drivers = os.path.join(addon_root, "drivers", "build")

    if "ARNOLD_PLUGIN_PATH" in os.environ:
        addon_root = os.path.dirname(os.path.abspath(__file__))
        drivers = os.path.join(addon_root, "drivers", "build")
        
        plugins = os.getenv("ARNOLD_PLUGIN_PATH").split(os.pathsep)

        if drivers not in plugins:
            os.environ["ARNOLD_PLUGIN_PATH"] += os.pathsep + drivers
    else:
        os.environ["ARNOLD_PLUGIN_PATH"] = drivers

def remove_plugins():
    addon_root = os.path.dirname(os.path.abspath(__file__))
    drivers = os.path.join(addon_root, "drivers", "build")

    plugins = os.getenv("ARNOLD_PLUGIN_PATH").split(os.pathsep)

    if len(plugins) > 1:
        plugins.remove(drivers)
        os.environ["ARNOLD_PLUGIN_PATH"] = os.pathsep.join(plugins)
    else:
        del os.environ["ARNOLD_PLUGIN_PATH"]

def configure_arnold_environment():
    if arnold_env_exists():
        path = os.getenv("ARNOLD_ROOT")
        print("Arnold installation found: " + path)

        prefs = bpy.context.preferences.addons[__package__].preferences
        prefs.arnold_path = path
    else:
        prefs = bpy.context.preferences.addons[__package__].preferences
        path = prefs.arnold_path
        print("No Arnold installation found. Settings from preferences: " + path)

    path = os.path.join(path, "python")

    if path not in sys.path:
        sys.path.append(path)

    configure_plugins()

def toggle_ocio(self, context):
    if self.use_color_management:
        if not "OCIO" in os.environ:
            print("No custom OCIO config found, using default Filmic...")
            os.environ["OCIO"] = get_default_ocio_config()
    else:
        # Clear OCIO profile if set to Filmic
        if os.getenv("OCIO") == get_default_ocio_config():
            del os.environ["OCIO"]

class ArnoldAddonPreferences(AddonPreferences):
    bl_idname = __package__

    arnold_path: StringProperty(
        name="Arnold Path",
        subtype="DIR_PATH"
    )

    use_color_management: BoolProperty(
        name="Use OCIO Color Management",
        update=toggle_ocio
    )

    def draw(self, context):
        # Arnold SDK config
        box = self.layout.box()
        
        row = box.row()
        row.prop(self, "arnold_path")
        row.enabled = not arnold_env_exists()

        row = box.row()
        if arnold_env_exists():
            row.label(text="Path automatically set by $ARNOLD_ROOT")

        # Color management
        box = self.layout.box()

        row = box.row()
        row.prop(self, "use_color_management")

        if not self.use_color_management:
            row = box.row()
            row.label(text="Using Arnold's built-in color manager.")
        else:
            row = box.row()
            row.label(text="Using OCIO color management. If the OCIO environment variable is not set, Filmic will be used by default.")


def register():
    bpy.utils.register_class(ArnoldAddonPreferences)
    configure_arnold_environment()

def unregister():
    bpy.utils.unregister_class(ArnoldAddonPreferences)
    remove_plugins()

if __name__ == "__main__":
    register()