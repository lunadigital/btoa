import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, IntProperty, BoolProperty

import os
import sys

def arnold_env_exists():
    if "ARNOLD_ROOT" in os.environ:
        return True

    return False

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

class ArnoldAddonPreferences(AddonPreferences):
    bl_idname = __package__

    arnold_path: StringProperty(
        name="Arnold Path",
        subtype="DIR_PATH"
    )

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "arnold_path")
        row.enabled = not arnold_env_exists()

        row = self.layout.row()
        if arnold_env_exists():
            row.label(text="Path automatically set by $ARNOLD_ROOT")

def register():
    bpy.utils.register_class(ArnoldAddonPreferences)
    configure_arnold_environment()

def unregister():
    bpy.utils.unregister_class(ArnoldAddonPreferences)

if __name__ == "__main__":
    register()