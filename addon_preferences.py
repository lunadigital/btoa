import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, BoolProperty, FloatVectorProperty

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

    abort_on_license_fail: BoolProperty(name="Abort On License Fail")
    skip_license_check: BoolProperty(name="Skip License Check")
    ignore_missing_textures: BoolProperty(name="Ignore Missing Textures", default=True)
    missing_texture_color: FloatVectorProperty(name="Missing Texture Color", size=4, default=(1, 0, 1, 1), subtype='COLOR')
    log_to_file: BoolProperty(name="Log to file")
    log_path: StringProperty(name="Log Path", subtype="FILE_PATH")
    log_info: BoolProperty(name="Info", default=True)
    log_warnings: BoolProperty(name="Warnings", default=True)
    log_errors: BoolProperty(name="Errors", default=True)
    log_debug: BoolProperty(name="Debug Messages", default=True)
    log_stats: BoolProperty(name="Render Statistics", default=True)
    log_plugins: BoolProperty(name="Plugin Details", default=True)
    log_progress: BoolProperty(name="Render Progress", default=True)
    log_nan: BoolProperty(name="NaN Pixels", default=True)
    log_timestamp: BoolProperty(name="Include timestamps", default=True)
    log_backtrace: BoolProperty(name="Stack Trace", default=True)
    log_memory: BoolProperty(name="Memory Usage", default=True)
    log_color: BoolProperty(name="Use colors in log", default=True)
    log_all: BoolProperty(name="Log All", default=True)

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
        col.prop(self, "abort_on_license_fail")
        col.prop(self, "skip_license_check", text="Render with Watermarks (Skip License Check)")

        # Error Handling
        box = self.layout.box()
        box.label(text="Error Handling")

        row = box.row()
        row.prop(self, "ignore_missing_textures")
        row.prop(self, "missing_texture_color", text="")

        # Logging
        box = self.layout.box()
        box.label(text="Logging")

        row = box.row(align=True, heading="Log to file")
        col = row.column(align=True)
        col.prop(self, "log_to_file", text="")
        col = row.column(align=True)
        col.enabled = self.log_to_file
        col.prop(self, "log_path", text="")

        box.separator()
        box.prop(self, "log_all")

        innerbox = box.box()
        innerbox.enabled = not self.log_all
        
        row = innerbox.row()
        row.prop(self, "log_info")
        row.prop(self, "log_warnings")
        row.prop(self, "log_errors")
        row.prop(self, "log_debug")

        row = innerbox.row()
        row.prop(self, "log_stats")
        row.prop(self, "log_plugins")
        row.prop(self, "log_progress")
        row.prop(self, "log_nan")

        row = innerbox.row()
        row.prop(self, "log_timestamp")
        row.prop(self, "log_backtrace")
        row.prop(self, "log_memory")
        row.prop(self, "log_color")

classes = (
    ArnoldAddonPreferences,
)
def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
