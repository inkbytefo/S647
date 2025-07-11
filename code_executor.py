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
S647 Ultra-Simple Code Executor
===============================

Ultra-simple code execution that works exactly like Blender console.
No complex context handling, no namespace manipulation - just pure exec().
"""

try:
    import bpy
except ImportError:
    bpy = None

def execute_code(code: str) -> str:
    """
    Execute Python code exactly like Blender console does.

    This is the simplest possible implementation that mirrors
    how Blender's own console executes code.

    Args:
        code: Python code to execute

    Returns:
        Execution result message
    """
    if not code.strip():
        return "No code to execute"

    # Basic safety check - block only truly dangerous operations
    dangerous_operations = [
        'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
        'os.remove', 'os.unlink', 'os.rmdir', 'shutil.rmtree',
        'bpy.ops.wm.quit', 'sys.exit', 'quit()', 'exit()'
    ]

    for dangerous_op in dangerous_operations:
        if dangerous_op in code:
            return f"Code execution blocked: Dangerous operation '{dangerous_op}' detected"

    # Execute code exactly like Blender console
    try:
        # Log what we're executing
        print(f"S647: Executing code: {code}")

        # Count objects before execution
        pre_count = 0
        if bpy is not None and hasattr(bpy, 'context') and bpy.context.scene:
            pre_count = len(bpy.context.scene.objects)
            print(f"S647: Objects before execution: {pre_count}")

        # Execute code with proper context override for Blender operators
        if bpy is not None:
            # Ensure we're in the right context for mesh operations
            try:
                # Make sure we're in object mode
                if bpy.context.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')

                # Execute code in global namespace (like Blender console)
                exec(code, globals())

            except Exception as context_error:
                # If context fails, try with context override
                print(f"S647: Context error, trying override: {context_error}")

                # Try to override context for the operation
                override_context = bpy.context.copy()

                # Ensure we have a valid area and region
                for window in bpy.context.window_manager.windows:
                    screen = window.screen
                    for area in screen.areas:
                        if area.type == 'VIEW_3D':
                            for region in area.regions:
                                if region.type == 'WINDOW':
                                    override_context['window'] = window
                                    override_context['screen'] = screen
                                    override_context['area'] = area
                                    override_context['region'] = region
                                    break
                            break
                    break

                # Execute with context override
                with bpy.context.temp_override(**override_context):
                    exec(code, globals())
        else:
            # Execute code in global namespace (like Blender console)
            exec(code, globals())

        # Count objects after execution
        post_count = 0
        if bpy is not None and hasattr(bpy, 'context') and bpy.context.scene:
            post_count = len(bpy.context.scene.objects)
            print(f"S647: Objects after execution: {post_count}")

            if post_count > pre_count:
                print(f"S647: Successfully added {post_count - pre_count} objects")

        print("S647: Code execution completed successfully")
        return f"Code executed successfully (Scene has {post_count} objects)"

    except Exception as e:
        error_msg = f"Code execution error: {str(e)}"
        print(f"S647: {error_msg}")
        return error_msg
