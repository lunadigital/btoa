import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, BoolProperty

import os

from . import environ as aienv

def refresh_addon(self, context):
    prefs = bpy.context.preferences.addons[__package__].preferences
    aienv.save_cached_arnold_path(prefs.arnold_path)
    bpy.ops.script.reload()

class ArnoldAddonPreferences(AddonPreferences):
    bl_idname = __package__

    arnold_path: StringProperty(
        name="Arnold Path",
        subtype="DIR_PATH",
        update=refresh_addon
    )

    # Used to check if we need to unregister everything or just addon preferences
    full_unregister: BoolProperty()

    def draw(self, context):
        # SDK config
        box = self.layout.box()
        
        row = box.row()
        row.prop(self, "arnold_path")
        row.enabled = not aienv.is_preconfigured()

        row = box.row()
        if aienv.is_preconfigured():
            row.label(text="Path automatically set by $ARNOLD_ROOT")

        # OCIO config notification
        profile = "Filmic"
        if os.getenv("OCIO") != aienv.get_default_ocio_config():
            normalized_path = os.path.normpath(os.path.dirname(os.getenv("OCIO")))
            profile = normalized_path.split(os.sep).pop()

        box = self.layout.box()

        col = box.column()
        col.label(text="OCIO Color Management")
        col.separator()
        col.label(text="Active Config: {}".format(profile))
        col.label(text="Config Path: {}".format(os.getenv("OCIO")))

        if profile == "Filmic":
            col.separator()
            col.label(text="To use an OCIO config other than Filmic, point the OCIO environment variable to a valid OCIO config.")

        # Licensing
        box = self.layout.box()

        col = box.column()
        col.label(text="Licensing")
        col.separator()
        col.prop(context.scene.arnold, "abort_on_license_fail")
        col.prop(context.scene.arnold, "skip_license_check", text="Render with Watermarks (Skip License Check)")

classes = (
    ArnoldAddonPreferences,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)