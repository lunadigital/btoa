import bpy
import os
import sys
from bpy.props import *
from pathlib import Path
from .utils import sdk_utils

ADDON_NAME = 'btoa'
ENGINE_ID = 'ARNOLD'
ADDON_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
ARNOLD_INSTALL_PATH = sdk_utils.get_arnold_install_root()
ARNOLD_PLUGIN_PATH = os.path.join(ADDON_ROOT_PATH, 'drivers', 'build')

# TODO: Move to `operators.py`?
class ARNOLD_OT_reset_log_flags(bpy.types.Operator):
    bl_idname = 'arnold.reset_log_flags'
    bl_label = "Reset Log Flags"
    bl_description = "Reset logging flags"
    bl_options = {'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_NAME].preferences

        flags = {
            'log_info',
            'log_warnings',
            'log_errors',
            'log_debug',
            'log_stats',
            'log_plugins',
            'log_progress',
            'log_nan',
            'log_timestamp',
            'log_backtrace',
            'log_memory',
            'log_color',
            'log_all'
        }

        for flag in flags:
            prefs.property_unset(flag)

        return {'FINISHED'}

class ARNOLD_OT_open_license_manager(bpy.types.Operator):
    bl_idname = 'arnold.open_license_manager'
    bl_label = "Open License Manager"
    bl_description = 'Open the Arnold License Manager application'

    def execute(self, context):
        import subprocess
        subprocess.run([sdk_utils.get_license_manager_path()])
        
        return {'FINISHED'}

class ArnoldAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_NAME

    abort_on_license_fail: BoolProperty(name="Abort On License Fail")
    skip_license_check: BoolProperty(name="Skip License Check")
    ignore_missing_textures: BoolProperty(name="Ignore Missing Textures", default=True)
    missing_texture_color: FloatVectorProperty(name="Missing Texture Color", size=4, default=(1, 0, 1, 1), subtype='COLOR')
    log_to_file: BoolProperty(name="Log to file")
    log_path: StringProperty(name="Log Path", subtype="DIR_PATH", default=os.path.join(Path.home(), "arnold_logs"))
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

    def draw(self, context):
        layout = self.layout

        layout.operator('arnold.open_license_manager')

        # OCIO config
        profile = 'OCIO' if 'OCIO' in os.environ else 'Filmic'

        box = layout.box()
        box.label(text='Color Management')
        box.separator()

        box.label(text=f'OCIO Config: {profile}')

        if profile == 'Filmic':
            box.separator()
            box.label(text='To use a config other than Filmic, point the `OCIO` environment variable to a valid OCIO config.')
        else:
            box.label(text='Path: {}'.format(os.getenv('OCIO')))

        # Licensing
        box = layout.box()
        box.label(text='Licensing')
        box.separator()

        # TODO: Add operator that opens ArnoldLicensingManager

        box.prop(self, 'abort_on_license_fail')
        box.prop(self, 'skip_license_check', text='Render with Watermarks (Skip License Check)')

        # Error Handling
        box = layout.box()
        box.label(text='Error Handling')
        box.separator()

        row = box.row()
        row.prop(self, 'ignore_missing_textures')
        row.prop(self, 'missing_texture_color', text='')

        # Logging
        box = layout.box()
        box.label(text='Logging')
        box.separator()

        box.prop(self, 'log_to_file')

        col = box.column()
        col.enabled = self.log_to_file
        col.prop(self, 'log_path')

        box.separator()
        box.prop(self, 'log_all')

        inner_box = box.box()
        inner_box.enabled = not self.log_all

        row = inner_box.row()
        row.prop(self, 'log_info')
        row.prop(self, 'log_warnings')
        row.prop(self, 'log_errors')
        row.prop(self, 'log_debug')

        row = inner_box.row()
        row.prop(self, 'log_stats')
        row.prop(self, 'log_plugins')
        row.prop(self, 'log_progress')
        row.prop(self, 'log_nan')

        row = inner_box.row()
        row.prop(self, 'log_timestamp')
        row.prop(self, 'log_backtrace')
        row.prop(self, 'log_memory')
        row.prop(self, 'log_color')

        box.operator('arnold.reset_log_flags')

classes = (
    ARNOLD_OT_reset_log_flags,
    ARNOLD_OT_open_license_manager,
    ArnoldAddonPreferences
)

def register_plugins():
    if 'ARNOLD_PLUGIN_PATH' in os.environ:
        plugins = os.getenv('ARNOLD_PLUGIN_PATH').split(os.pathsep)

        if ARNOLD_PLUGIN_PATH not in plugins:
            os.environ['ARNOLD_PLUGIN_PATH'] += os.pathsep + ARNOLD_PLUGIN_PATH
    else:
        os.environ['ARNOLD_PLUGIN_PATH'] = ARNOLD_PLUGIN_PATH

def unregister_plugins():
    plugins = os.getenv('ARNOLD_PLUGIN_PATH').split(os.pathsep)

    if len(plugins) > 1:
        plugins.remove(ARNOLD_PLUGIN_PATH)
        os.environ['ARNOLD_PLUGIN_PATH'] = os.pathsep.join(plugins)
    else:
        del os.environ['ARNOLD_PLUGIN_PATH']

def bootstrap_arnold():
    # SDK
    python_path = os.path.join(ARNOLD_INSTALL_PATH, 'python')
    lib_path = os.path.join(ARNOLD_INSTALL_PATH, 'bin')

    if python_path not in sys.path:
        sys.path.append(python_path)

    os.environ['PATH'] = lib_path + os.pathsep + os.environ['PATH']

    # Material presets
    blender_presets_path = os.path.join(
        bpy.utils.user_resource('SCRIPTS'),
        'presets',
        ADDON_NAME,
        'materials'
    )

    btoa_presets_path = os.path.join(
        ADDON_ROOT_PATH,
        'presets',
        'materials'
    )

    if not os.path.isdir(blender_presets_path):
        os.makedirs(blender_presets_path)

        files = os.listdir(btoa_presets_path)

        for f in files:
            shutil.copy2(
                os.path.join(btoa_presets_path, f),
                blender_presets_path
            )

def register():
    from .utils import register_utils
    register_utils.register_classes(classes)

    bootstrap_arnold()
    register_plugins()

def unregister():
    from .utils import register_utils
    register_utils.unregister_classes(classes)

    unregister_plugins()