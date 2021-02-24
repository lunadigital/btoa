import bpy
import os
import sys

def is_preconfigured():
    if "ARNOLD_ROOT" in os.environ:
        return True
    return False

def load_cached_arnold_path():
    try:
        path_to_cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefs")
        f = open(path_to_cache, "r")
        return f.readline()
    except:
        return ""

def save_cached_arnold_path(path):
    path_to_cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefs")
    with open(path_to_cache, "w") as f:
        f.write(path)

def configure_arnold_environment():
    prefs = bpy.context.preferences.addons[__package__].preferences

    if is_preconfigured():
        path = os.getenv("ARNOLD_ROOT")
        print("Arnold installation found: " + path)
    else:
        path = load_cached_arnold_path()
        print("No Arnold installation found. Settings from preferences: " + path)

    prefs.arnold_path = path

    if path != "":
        python_path = os.path.join(prefs.arnold_path, "python")
        if python_path not in sys.path:
            sys.path.append(python_path)

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

def get_default_ocio_config():
    version = "{major}.{minor}".format(
        major=bpy.app.version[0],
        minor=bpy.app.version[1]
    )

    if sys.platform == 'darwin':
        blender_root = os.path.join("/", *bpy.app.binary_path.split("/")[:-2], "Resources")
    else:
        blender_root = os.path.dirname(bpy.app.binary_path)

    return os.path.join(blender_root, version, "datafiles", "colormanagement", "config.ocio")

def configure_ocio():
    if not "OCIO" in os.environ:
        print("No custom OCIO config found, using default Filmic...")
        os.environ["OCIO"] = get_default_ocio_config()

def reset_ocio():
    # Clear OCIO profile if set to Filmic
    if os.getenv("OCIO") == get_default_ocio_config():
        del os.environ["OCIO"]