import bpy
from bpy.props import *

import math
import os
import shutil
import ssl
import stat
import subprocess
import sys
import tarfile
import threading
import urllib.request
import zipfile

from pathlib import Path

from .utils import sdk_utils
from .updater import Version, ArnoldUpdater

ADDON_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
ADDON_NAME = os.path.basename(ADDON_ROOT_PATH)
ENGINE_ID = 'ARNOLD'
ARNOLD_INSTALL_PATH = sdk_utils.get_sdk_install_path()
ARNOLD_PLUGIN_PATH = os.path.join(ARNOLD_INSTALL_PATH, 'drivers')
INSTALL_PROGRESS_LABEL = ''
INSTALL_IN_PROGRESS = False
INSTALL_JUST_COMPLETED = False
SDK_UPDATE_AVAILABLE = False
CHECK_FOR_SDK_UPDATE = True

def update_progress_percent(block_num, block_size, total_size):
    global INSTALL_PROGRESS_LABEL

    percent = math.floor(((block_num * block_size) / total_size) * 100)
    INSTALL_PROGRESS_LABEL = f'Downloading, please wait... ({percent}%)'

def delete_old_sdk():
    old_sdk_path = os.path.join(sdk_utils.get_arnold_install_root(), '.btoa')

    if os.path.exists(old_sdk_path):
        shutil.rmtree(old_sdk_path)

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
        subprocess.run([sdk_utils.get_license_manager_path()])
        return {'FINISHED'}

class ARNOLD_OT_install_arnold(bpy.types.Operator):
    bl_idname = 'arnold.install_arnold'
    bl_label = "Install Arnold"
    bl_description = 'Install the Arnold Server application'

    active = False
    timer = None
    terminated = False
    worker = None

    @classmethod
    def poll(cls, context):
        global INSTALL_IN_PROGRESS
        global INSTALL_JUST_COMPLETED
        return not INSTALL_IN_PROGRESS and not INSTALL_JUST_COMPLETED

    def download_arnold(self):
        global INSTALL_PROGRESS_LABEL
        global INSTALL_IN_PROGRESS

        INSTALL_IN_PROGRESS = True

        install_dir = sdk_utils.get_arnold_install_root()
        archive_path = os.path.join(install_dir, 'btoa.zip')

        Path(install_dir).mkdir(parents=True, exist_ok=True)

        updater = ArnoldUpdater()
        version = updater.latest_version.to_string()

        if sys.platform == 'win32':
            package = f'Arnold-{version}-windows.zip'
        elif sys.platform.startswith('linux'):
            package = f'Arnold-{version}-linux.zip'
        elif sys.platform == 'darwin':
            package = f'Arnold-{version}-darwin.zip'

        INSTALL_PROGRESS_LABEL =f'Downloading, please wait...'

        '''
        urllib returns a CERTIFICATE_VERIFY_FAILED error on Linux and
        macOS because of how the OSes handle SSL certs. I don't want
        to force users to do any additional noodling with their systems
        to get BtoA to install so we're going to create a temporary SSL
        context instead.
        '''
        ssl._create_default_https_context = ssl._create_unverified_context

        urllib.request.urlretrieve(
            f'https://www.arnoldforblender.com/downloads/{version}/{package}',
            archive_path,
            update_progress_percent
        )

        INSTALL_PROGRESS_LABEL = 'Installing Arnold...'

        with zipfile.ZipFile(archive_path, 'r') as f:
            f.extractall(ARNOLD_INSTALL_PATH)

        # If on macOS, we need to force chmod +x so the license manager runs as expected
        if sys.platform == 'darwin':
            license_manager = Path(os.path.join(ARNOLD_INSTALL_PATH, "bin", "ArnoldLicenseManager.app", "Contents", "MacOS", "ArnoldLicenseManager"))
            license_manager.chmod(license_manager.stat().st_mode | stat.S_IEXEC)

        os.remove(archive_path)

        INSTALL_PROGRESS_LABEL = 'Successfully installed Arnold. Please restart Blender.'
        INSTALL_IN_PROGRESS = False
        self.active = False

    def execute(self, context):
        self.active = True

        wm = context.window_manager
        self.timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        self.worker = threading.Thread(target=self.download_arnold, args=())
        self.worker.start()

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'ESC':
            self.terminated = True
            self.finish(context)

            global INSTALL_IN_PROGRESS
            INSTALL_IN_PROGRESS = False

            return {'CANCELLED'}

        if not self.worker.is_alive():
            self.finish(context)

            global INSTALL_JUST_COMPLETED
            INSTALL_JUST_COMPLETED = True

            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def finish(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

class ARNOLD_OT_uninstall_arnold(bpy.types.Operator):
    bl_idname = 'arnold.uninstall_arnold'
    bl_label = "Uninstall"
    bl_description = 'Uninstall the Arnold Server application'

    @classmethod
    def poll(cls, context):
        global INSTALL_IN_PROGRESS
        return not INSTALL_IN_PROGRESS

    def execute(self, context):
        global INSTALL_IN_PROGRESS
        global INSTALL_PROGRESS_LABEL

        INSTALL_IN_PROGRESS = True
        INSTALL_PROGRESS_LABEL = ''

        '''
        Windows won't let us outright delete files that are opened in other
        programs, so we have to move and hide the SDK folder here so BtoA
        triggers a new install. We will delete the SDK the next time Blender
        is opened.
        '''
        tmp_name = os.path.join(sdk_utils.get_arnold_install_root(), '.btoa')
        os.rename(ARNOLD_INSTALL_PATH, tmp_name)

        if sys.platform == "win32":
            subprocess.run(["attrib", "+H", tmp_name], check=True)

        INSTALL_IN_PROGRESS = False

        return {'FINISHED'}

class ARNOLD_OT_update_arnold(bpy.types.Operator):
    bl_idname = 'arnold.update_arnold'
    bl_label = ""
    bl_description = 'Update the Arnold Server application'

    @classmethod
    def poll(cls, context):
        global SDK_UPDATE_AVAILABLE
        global INSTALL_IN_PROGRESS
        return SDK_UPDATE_AVAILABLE and not INSTALL_IN_PROGRESS

    def execute(self, context):
        bpy.ops.arnold.uninstall_arnold()
        bpy.ops.arnold.install_arnold('INVOKE_DEFAULT')

        return {'FINISHED'}

class ARNOLD_OT_check_for_update(bpy.types.Operator):
    bl_idname = 'arnold.check_for_update'
    bl_label = "Check for update"
    bl_description = "Check for update to Arnold Server application"

    def execute(self, context):
        global CHECK_FOR_SDK_UPDATE
        CHECK_FOR_SDK_UPDATE = True

        return {'FINISHED'}

class ArnoldAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_NAME

    abort_on_license_fail: BoolProperty(name="Abort On License Fail")
    skip_license_check: BoolProperty(name="Skip License Check")
    ignore_missing_textures: BoolProperty(name="Ignore Missing Textures")
    missing_texture_color: FloatVectorProperty(name="Missing Texture Color", size=4, default=(1, 0, 1, 1), subtype='COLOR')
    log_to_file: BoolProperty(name="Log to file")
    log_path: StringProperty(name="Log Path", subtype="DIR_PATH", default=os.path.join(Path.home(), "arnold_logs"))
    log_info: BoolProperty(name="Info")
    log_warnings: BoolProperty(name="Warnings")
    log_errors: BoolProperty(name="Errors")
    log_debug: BoolProperty(name="Debug Messages")
    log_stats: BoolProperty(name="Render Statistics")
    log_plugins: BoolProperty(name="Plugin Details")
    log_progress: BoolProperty(name="Render Progress")
    log_nan: BoolProperty(name="NaN Pixels")
    log_timestamp: BoolProperty(name="Include timestamps")
    log_backtrace: BoolProperty(name="Stack Trace")
    log_memory: BoolProperty(name="Memory Usage")
    log_color: BoolProperty(name="Use colors in log")
    log_all: BoolProperty(name="Log All")

    def draw(self, context):
        global SDK_UPDATE_AVAILABLE
        global INSTALL_JUST_COMPLETED
        layout = self.layout

        # Arnold install
        if sdk_utils.is_arnoldserver_installed() and not INSTALL_IN_PROGRESS and not INSTALL_JUST_COMPLETED:
            import arnold

            arch, major, minor, fix = arnold.AiGetVersion()
            arch, major, minor, fix = arch.decode('utf-8'), major.decode('utf-8'), minor.decode('utf-8'), fix.decode('utf-8')
            version = Version(arch, major, minor, fix)

            # Check for SDK update
            global CHECK_FOR_SDK_UPDATE
            if CHECK_FOR_SDK_UPDATE:
                updater = ArnoldUpdater(version)
                SDK_UPDATE_AVAILABLE = updater.current_version.to_int() < updater.latest_version.to_int()

                CHECK_FOR_SDK_UPDATE = False

            layout.label(text="Arnold Server Configuration")

            box = layout.box()
            box.label(text=f'Version: {arch}.{major}.{minor}.{fix}')
            
            row = box.row(align=True)
            row.operator('arnold.check_for_update', text="", icon="FILE_REFRESH")
            row.operator('arnold.update_arnold', text="Update Arnold" if SDK_UPDATE_AVAILABLE else "Arnold is up-to-date")
            row.operator('arnold.uninstall_arnold')
        else:
            layout.operator('arnold.install_arnold')

            global INSTALL_PROGRESS_LABEL
            if INSTALL_PROGRESS_LABEL:
                layout.label(text=INSTALL_PROGRESS_LABEL)

        if sdk_utils.is_arnoldserver_installed() and not INSTALL_IN_PROGRESS and not INSTALL_JUST_COMPLETED:
            # OCIO config
            layout.label(text='Color Management')

            box = layout.box()

            profile = 'OCIO' if 'OCIO' in os.environ else 'Filmic'
            box.label(text=f'OCIO Config: {profile}')

            if profile == 'Filmic':
                box.separator()
                box.label(text='To use a config other than Filmic, point the `OCIO` environment variable to a valid OCIO config.')
            else:
                box.label(text='Path: {}'.format(os.getenv('OCIO')))

            # Licensing
            layout.label(text='Licensing')

            box = layout.box()
            box.operator('arnold.open_license_manager')
            box.prop(self, 'abort_on_license_fail')
            box.prop(self, 'skip_license_check', text='Render with Watermarks (Skip License Check)')

            # Error Handling
            layout.label(text='Error Handling')

            box = layout.box()

            row = box.row()
            row.prop(self, 'ignore_missing_textures')
            row.prop(self, 'missing_texture_color', text='')

            # Logging
            layout.label(text='Logging')

            box = layout.box()
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
    ARNOLD_OT_install_arnold,
    ARNOLD_OT_uninstall_arnold,
    ARNOLD_OT_update_arnold,
    ARNOLD_OT_check_for_update,
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

    delete_old_sdk()
    bootstrap_arnold()
    register_plugins()

def unregister():
    from .utils import register_utils
    register_utils.unregister_classes(classes)

    unregister_plugins()