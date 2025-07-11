"""
S647 PyWin32 Bootstrap Module
============================

Custom bootstrap module for initializing pywin32 in Blender environment.
This module handles the specific requirements for loading pywin32 DLLs
and modules within Blender's Python environment.
"""

import os
import sys
from pathlib import Path


def setup_pywin32_environment():
    """
    Setup pywin32 environment for Blender
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    try:
        # Get the lib directory path
        lib_dir = Path(__file__).parent
        print(f"S647 PyWin32: Setting up environment from {lib_dir}")
        
        # Check if we're on Windows
        if os.name != 'nt':
            print("S647 PyWin32: Not on Windows, skipping pywin32 setup")
            return True
        
        # Add pywin32 system32 directory to DLL search path
        pywin32_system32 = lib_dir / "pywin32_system32"
        if pywin32_system32.exists():
            try:
                # Add DLL directory for Python 3.8+
                if hasattr(os, 'add_dll_directory'):
                    os.add_dll_directory(str(pywin32_system32))
                    print(f"S647 PyWin32: Added DLL directory: {pywin32_system32}")
                else:
                    # Fallback for older Python versions
                    os.environ['PATH'] = str(pywin32_system32) + os.pathsep + os.environ.get('PATH', '')
                    print(f"S647 PyWin32: Added to PATH: {pywin32_system32}")
            except Exception as e:
                print(f"S647 PyWin32: Warning - Could not add DLL directory: {e}")
        
        # Add win32 directories to Python path
        win32_paths = [
            lib_dir / "win32",
            lib_dir / "win32" / "lib",
            lib_dir / "Pythonwin"
        ]
        
        for win32_path in win32_paths:
            if win32_path.exists() and str(win32_path) not in sys.path:
                sys.path.insert(0, str(win32_path))
                print(f"S647 PyWin32: Added to sys.path: {win32_path}")
        
        # Try to import and initialize pywin32 modules
        try:
            # Import pywintypes first
            import pywintypes
            print("S647 PyWin32: pywintypes imported successfully")
            
            # Try to import pythoncom
            import pythoncom
            print("S647 PyWin32: pythoncom imported successfully")
            
            return True
            
        except ImportError as e:
            print(f"S647 PyWin32: Could not import pywin32 modules: {e}")
            return False
        
    except Exception as e:
        print(f"S647 PyWin32: Setup failed: {e}")
        import traceback
        print(f"S647 PyWin32: Traceback: {traceback.format_exc()}")
        return False


def test_pywin32_functionality():
    """
    Test basic pywin32 functionality
    
    Returns:
        bool: True if pywin32 is working, False otherwise
    """
    try:
        import pywintypes
        import pythoncom
        
        # Test basic functionality
        pythoncom.CoInitialize()
        pythoncom.CoUninitialize()
        
        print("S647 PyWin32: Functionality test passed")
        return True
        
    except Exception as e:
        print(f"S647 PyWin32: Functionality test failed: {e}")
        return False


def get_pywin32_info():
    """
    Get information about pywin32 installation
    
    Returns:
        dict: Information about pywin32 status
    """
    info = {
        'available': False,
        'version': None,
        'modules': [],
        'dll_path': None
    }
    
    try:
        lib_dir = Path(__file__).parent
        
        # Check for pywin32 version
        version_file = lib_dir / "pywin32.version.txt"
        if version_file.exists():
            info['version'] = version_file.read_text().strip()
        
        # Check for DLL directory
        pywin32_system32 = lib_dir / "pywin32_system32"
        if pywin32_system32.exists():
            info['dll_path'] = str(pywin32_system32)
        
        # Check for available modules
        try:
            import pywintypes
            info['modules'].append('pywintypes')
        except ImportError:
            pass
        
        try:
            import pythoncom
            info['modules'].append('pythoncom')
        except ImportError:
            pass
        
        try:
            import win32api
            info['modules'].append('win32api')
        except ImportError:
            pass
        
        info['available'] = len(info['modules']) > 0
        
    except Exception as e:
        print(f"S647 PyWin32: Error getting info: {e}")
    
    return info


# Auto-setup when module is imported
if __name__ != "__main__":
    setup_success = setup_pywin32_environment()
    if setup_success:
        print("S647 PyWin32: Bootstrap completed successfully")
    else:
        print("S647 PyWin32: Bootstrap completed with warnings")


if __name__ == "__main__":
    # Test mode
    print("S647 PyWin32 Bootstrap Test Mode")
    print("=" * 40)
    
    # Setup environment
    setup_success = setup_pywin32_environment()
    print(f"Setup success: {setup_success}")
    
    # Test functionality
    test_success = test_pywin32_functionality()
    print(f"Test success: {test_success}")
    
    # Get info
    info = get_pywin32_info()
    print(f"PyWin32 info: {info}")
