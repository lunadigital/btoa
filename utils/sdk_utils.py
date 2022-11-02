import os
import sys

def get_arnold_install_root():
    if sys.platform == 'win32':
        return "C:\\Program Files\\Autodesk\\ArnoldServer"

def get_license_manager_path():
    root = os.path.join(get_arnold_install_root(), 'bin')
    
    if sys.platform == 'win32':
        return os.path.join(root, 'ArnoldLicenseManager.exe')