import os
import sys

def get_arnold_install_root():
    return os.path.join(os.path.expanduser('~'), 'Autodesk')

def get_sdk_install_path():
    return os.path.join(get_arnold_install_root(), 'btoa')

def get_license_manager_path():
    root = os.path.join(get_sdk_install_path(), 'bin')
    
    if sys.platform == 'win32':
        return os.path.join(root, 'ArnoldLicenseManager.exe')
    elif sys.platform.startswith('linux'):
        return os.path.join(root, 'ArnoldLicenseManager')
    elif sys.platform == 'darwin':
        return os.path.join(root, 'ArnoldLicenseManager.app', 'Contents', 'MacOS', 'ArnoldLicenseManager')

def is_arnoldserver_installed():
    sdk_installed = os.path.exists(get_sdk_install_path())
    import_success = False

    try:
        import arnold
        import_success = True
    except:
        pass

    return sdk_installed and import_success