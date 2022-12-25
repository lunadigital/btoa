import os
import sys

def get_arnold_install_root():
    return os.path.join(os.path.expanduser('~'), 'Autodesk')

def get_server_path():
    return os.path.join(get_arnold_install_root(), 'ArnoldServer')

def get_license_manager_path():
    root = os.path.join(get_server_path(), 'bin')
    
    if sys.platform == 'win32':
        return os.path.join(root, 'ArnoldLicenseManager.exe')

def is_arnoldserver_installed():
    try:
        import arnold
        return True
    except:
        return False