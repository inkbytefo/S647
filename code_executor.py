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
# ##### END GPL LICENSE BLOCK #####

"""
S647 Simplified Code Executor Module
====================================

Simple and effective code execution inspired by Blender MCP.
Minimal restrictions for better AI code compatibility.
"""

try:
    import bpy
except ImportError:
    # Mock bpy for testing outside Blender
    bpy = None

import io
import contextlib
from typing import Optional

def execute_code(code: str, sandbox: bool = False, strict_mode: bool = False) -> str:
    """
    Execute Python code with minimal restrictions (Blender MCP style)
    
    This approach prioritizes functionality over excessive security restrictions.
    Only blocks truly dangerous operations like system commands and file deletion.

    Args:
        code: Python code to execute
        sandbox: Whether to run in sandboxed environment (simplified)
        strict_mode: Whether to use strict safety checks (simplified)

    Returns:
        Execution result or error message
    """
    if not code.strip():
        return "No code to execute"

    # Simple safety check - only block truly dangerous operations
    dangerous_operations = [
        'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
        'os.remove', 'os.unlink', 'os.rmdir', 'shutil.rmtree',
        'bpy.ops.wm.quit'
    ]
    
    # Check for dangerous operations
    for dangerous_op in dangerous_operations:
        if dangerous_op in code:
            return f"Code execution blocked: Dangerous operation '{dangerous_op}' detected"

    # Simple execution with minimal overhead (Blender MCP style)
    try:
        # Create a simple namespace with Blender access
        namespace = {
            "__builtins__": __builtins__
        }
        
        # Add bpy if available (in Blender environment)
        if bpy is not None:
            namespace["bpy"] = bpy

        # Capture stdout during execution
        capture_buffer = io.StringIO()
        with contextlib.redirect_stdout(capture_buffer):
            exec(code, namespace)
        
        captured_output = capture_buffer.getvalue()
        
        # Return output or success message
        if captured_output.strip():
            return captured_output
        else:
            return "Code executed successfully (no output)"
            
    except Exception as e:
        return f"Code execution error: {str(e)}"
