# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
S647 - AI-Powered Blender Assistant
====================================

An advanced Blender addon that integrates OpenAI's powerful language models
to assist with 3D modeling, scripting, and automation tasks within Blender.

Features:
- AI-powered Python code generation for Blender
- Safe code execution environment
- Interactive chat interface
- Blender-specific AI assistance
- Integration with OpenAI's latest models

Author: S647 Development Team
Version: 1.0.0
Blender: 4.4+
"""

bl_info = {
    "name": "S647 - AI-Powered Blender Assistant",
    "author": "S647 Development Team",
    "version": (1, 0, 0),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > S647 Tab",
    "description": "AI-powered assistant for Blender using OpenAI integration",
    "warning": "Requires OpenAI API key and internet connection",
    "doc_url": "https://github.com/s647/blender-ai-assistant",
    "category": "Development",
    "support": "COMMUNITY",
}

import bpy
import sys
import os
from pathlib import Path

# Add the addon directory and lib directory to Python path for imports
addon_dir = Path(__file__).parent
lib_dir = addon_dir / "lib"

# Add addon directory to path
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))

# Enhanced lib directory setup for MCP and dependencies
if lib_dir.exists():
    # Add lib directory to path for dependencies
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))
        print(f"S647: Added lib directory to path: {lib_dir}")

    # Handle pywin32 on Windows with enhanced setup
    if os.name == 'nt':
        # Add pywin32 DLL directory
        pywin32_system32 = lib_dir / "pywin32_system32"
        if pywin32_system32.exists():
            try:
                os.add_dll_directory(str(pywin32_system32))
                print("S647: Added pywin32 DLL directory")
            except (OSError, AttributeError):
                # add_dll_directory might not be available on older Python versions
                pass

        # Add win32 subdirectories to path for pywin32
        win32_dirs = [
            lib_dir / "win32",
            lib_dir / "win32" / "lib",
            lib_dir / "Pythonwin"
        ]
        for win32_dir in win32_dirs:
            if win32_dir.exists() and str(win32_dir) not in sys.path:
                sys.path.insert(0, str(win32_dir))
                print(f"S647: Added win32 directory to path: {win32_dir}")

        # Set up pywin32 bootstrap if available
        try:
            import pywin32_bootstrap
            print("S647: pywin32_bootstrap loaded successfully")
        except ImportError:
            print("S647: pywin32_bootstrap not found, continuing without it")

    # Add MCP specific paths
    mcp_dir = lib_dir / "mcp"
    if mcp_dir.exists() and str(mcp_dir) not in sys.path:
        sys.path.insert(0, str(mcp_dir))
        print(f"S647: Added MCP directory to path: {mcp_dir}")

    print(f"S647: Library setup complete. Total paths added: {len([p for p in sys.path if str(lib_dir) in p])}")
else:
    print(f"S647: Warning - lib directory not found: {lib_dir}")

# Import addon modules
try:
    from . import (
        preferences,
        operators,
        panels,
        properties,
        ai_engine,
        code_executor,
        utils,
        mcp_client,
        mcp_config,
    )
except ImportError as e:
    print(f"S647: Error importing modules: {e}")
    # Create placeholder modules if they don't exist yet
    preferences = None
    operators = None
    panels = None
    properties = None
    ai_engine = None
    code_executor = None
    utils = None
    mcp_client = None
    mcp_config = None

# Global addon state
_addon_registered = False

def register():
    """Register all addon components"""
    global _addon_registered
    
    if _addon_registered:
        return
    
    print("S647: Registering addon...")
    
    try:
        # Register preferences first
        if preferences:
            preferences.register()
        
        # Register properties
        if properties:
            properties.register()
        
        # Register operators
        if operators:
            operators.register()
        
        # Register panels
        if panels:
            panels.register()
        
        # Initialize AI engine (includes MCP initialization)
        if ai_engine:
            ai_engine.initialize()

        # Check MCP availability
        try:
            if mcp_client and mcp_client.is_mcp_available():
                print("S647: MCP integration available")
            else:
                print("S647: MCP integration not available (install with: pip install mcp)")
        except Exception as e:
            print(f"S647: MCP check failed: {e}")

        _addon_registered = True
        print("S647: Successfully registered!")
        
    except Exception as e:
        print(f"S647: Error during registration: {e}")
        # Try to unregister what was registered
        unregister()
        raise

def unregister():
    """Unregister all addon components"""
    global _addon_registered
    
    if not _addon_registered:
        return
    
    print("S647: Unregistering addon...")
    
    try:
        # Cleanup AI engine (includes MCP cleanup)
        if ai_engine:
            ai_engine.cleanup()

        # Cleanup MCP if available
        try:
            if mcp_client:
                mcp_client.shutdown_mcp()
        except Exception as e:
            print(f"S647: MCP cleanup failed: {e}")
        
        # Unregister in reverse order
        if panels:
            panels.unregister()
        
        if operators:
            operators.unregister()
        
        if properties:
            properties.unregister()
        
        if preferences:
            preferences.unregister()
        
        _addon_registered = False
        print("S647: Successfully unregistered!")
        
    except Exception as e:
        print(f"S647: Error during unregistration: {e}")

# Allow running the script directly for development
if __name__ == "__main__":
    register()
