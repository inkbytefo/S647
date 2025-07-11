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
S647 Utilities Module
=====================

Common utility functions for the S647 addon including Blender context
extraction, code parsing, and helper functions.
"""

import bpy
import bmesh
import json
import re
from typing import Dict, List, Any, Optional, Tuple

def get_blender_context_info(context_mode: str = 'standard') -> Dict[str, Any]:
    """
    Extract Blender context information for AI processing
    
    Args:
        context_mode: Level of detail ('minimal', 'standard', 'detailed', 'full')
    
    Returns:
        Dictionary containing context information
    """
    import datetime

    context_info = {
        "blender_version": bpy.app.version_string,
        "scene_name": bpy.context.scene.name,
        "mode": bpy.context.mode,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    }
    
    if context_mode == 'minimal':
        return context_info
    
    # Standard context
    scene = bpy.context.scene
    context_info.update({
        "active_object": get_object_info(bpy.context.active_object) if bpy.context.active_object else None,
        "selected_objects": [obj.name for obj in bpy.context.selected_objects],
        "total_objects": len(scene.objects),
        "current_frame": scene.frame_current,
        "frame_range": [scene.frame_start, scene.frame_end],
    })
    
    if context_mode in ['detailed', 'full']:
        # Detailed context
        context_info.update({
            "scene_objects": [get_object_info(obj, detailed=True) for obj in scene.objects],
            "collections": [col.name for col in scene.collection.children],
            "render_engine": scene.render.engine,
            "world_settings": get_world_info(scene.world) if scene.world else None,
        })
    
    if context_mode == 'full':
        # Full context (can be heavy)
        context_info.update({
            "materials": [get_material_info(mat) for mat in bpy.data.materials],
            "textures": [tex.name for tex in bpy.data.textures],
            "cameras": [get_object_info(obj) for obj in scene.objects if obj.type == 'CAMERA'],
            "lights": [get_object_info(obj) for obj in scene.objects if obj.type == 'LIGHT'],
        })
    
    return context_info

def get_object_info(obj: bpy.types.Object, detailed: bool = False) -> Optional[Dict[str, Any]]:
    """Get information about a Blender object"""
    if not obj:
        return None
    
    info = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": obj.visible_get(),
    }
    
    if detailed:
        info.update({
            "dimensions": list(obj.dimensions),
            "parent": obj.parent.name if obj.parent else None,
            "children": [child.name for child in obj.children],
            "modifiers": [mod.name for mod in obj.modifiers],
            "materials": [mat.name for mat in obj.data.materials] if hasattr(obj.data, 'materials') else [],
        })
        
        # Mesh-specific info
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            info.update({
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "faces": len(mesh.polygons),
                "has_uv": len(mesh.uv_layers) > 0,
                "has_vertex_colors": len(mesh.vertex_colors) > 0,
            })
    
    return info

def get_material_info(material: bpy.types.Material) -> Dict[str, Any]:
    """Get information about a material"""
    return {
        "name": material.name,
        "use_nodes": material.use_nodes,
        "diffuse_color": list(material.diffuse_color) if hasattr(material, 'diffuse_color') else None,
        "metallic": getattr(material, 'metallic', None),
        "roughness": getattr(material, 'roughness', None),
    }

def get_world_info(world: bpy.types.World) -> Dict[str, Any]:
    """Get information about world settings"""
    return {
        "name": world.name,
        "use_nodes": world.use_nodes,
        "color": list(world.color) if hasattr(world, 'color') else None,
    }

def extract_python_code(text: str) -> List[Tuple[str, int, int]]:
    """
    Extract Python code blocks from text
    
    Returns:
        List of tuples (code, start_pos, end_pos)
    """
    code_blocks = []
    
    # Pattern for code blocks with ```python or ```
    pattern = r'```(?:python)?\s*\n(.*?)\n```'
    matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        code = match.group(1).strip()
        if code:
            code_blocks.append((code, match.start(), match.end()))
    
    # Also look for inline code with single backticks if it looks like Python
    inline_pattern = r'`([^`\n]+)`'
    inline_matches = re.finditer(inline_pattern, text)
    
    for match in inline_matches:
        code = match.group(1).strip()
        # Simple heuristic to detect Python code
        if any(keyword in code for keyword in ['bpy.', 'import ', 'def ', 'class ', 'for ', 'if ']):
            code_blocks.append((code, match.start(), match.end()))
    
    return code_blocks

def validate_python_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python code syntax
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        compile(code, '<string>', 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def is_safe_code(code: str) -> Tuple[bool, List[str]]:
    """
    Enhanced safety check for code execution

    Returns:
        Tuple of (is_safe, list_of_warnings)
    """
    try:
        # Use the enhanced code executor analysis
        from . import code_executor
        analysis = code_executor.analyze_code_safety(code, strict_mode=True)

        warnings = []
        for warning in analysis['warnings']:
            warnings.append(warning['description'])

        for error in analysis['errors']:
            warnings.append(f"CRITICAL: {error['description']}")

        return analysis['is_safe'], warnings

    except ImportError:
        # Fallback to basic check if code_executor not available
        warnings = []
        dangerous_patterns = [
            (r'\bos\b', "Uses 'os' module - file system access"),
            (r'\bsubprocess\b', "Uses 'subprocess' - system command execution"),
            (r'\beval\b', "Uses 'eval' - arbitrary code execution"),
            (r'\bexec\b', "Uses 'exec' - arbitrary code execution"),
            (r'\b__import__\b', "Uses '__import__' - dynamic imports"),
            (r'\bopen\s*\(', "File operations detected"),
            (r'\bfile\s*\(', "File operations detected"),
            (r'\bdelete\b', "Potential destructive operation"),
            (r'\bremove\b', "Potential destructive operation"),
            (r'\bclear\b', "Potential destructive operation"),
        ]

        for pattern, warning in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(warning)

        is_safe = len(warnings) == 0
        return is_safe, warnings

def format_code_for_display(code: str, max_lines: int = 20) -> str:
    """Format code for display in UI"""
    lines = code.split('\n')
    
    if len(lines) <= max_lines:
        return code
    
    # Truncate and add indicator
    truncated = '\n'.join(lines[:max_lines])
    remaining = len(lines) - max_lines
    truncated += f'\n... ({remaining} more lines)'
    
    return truncated

def create_system_prompt(interaction_mode: str = 'chat') -> str:
    """Create system prompt for AI with Blender context"""
    base_prompt = """You are S647, an expert AI assistant specialized in Blender 3D software and Python scripting. You provide professional-grade assistance with:

🎯 CORE EXPERTISE:
• Blender Python API (bpy) scripting and automation
• 3D modeling, sculpting, and mesh operations
• Material creation, shader nodes, and texturing
• Animation, rigging, and character setup
• Rendering engines (Cycles, Eevee) and lighting
• Add-on development and Blender customization
• Geometry nodes and procedural workflows

💻 CODE GUIDELINES:
• Always use proper bpy syntax and best practices
• Include comprehensive error handling with try/except blocks
• Add clear, educational comments explaining each step
• Prefer non-destructive operations when possible
• Validate object existence before operations
• Use context-aware code (check active objects, modes, etc.)
• Format all executable code in ```python blocks

🔍 CONTEXT AWARENESS:
• Analyze the provided Blender scene context carefully
• Consider current mode, selected objects, and scene state
• Suggest context-appropriate solutions
• Warn about potential issues or requirements

📚 RESPONSE STYLE:
• Provide step-by-step explanations
• Include both code and conceptual guidance
• Suggest alternative approaches when relevant
• Reference official Blender documentation when helpful

Always prioritize user safety and data integrity. When in doubt, suggest backup procedures."""

    # Add mode-specific instructions
    if interaction_mode == 'chat':
        base_prompt += """

🗣️ CHAT MODE - EDUCATIONAL FOCUS:
• Prioritize learning and understanding
• Provide detailed explanations with examples
• Ask clarifying questions when needed
• Encourage exploration and experimentation
• Use conversational, friendly tone
• Break down complex concepts into digestible parts"""

    elif interaction_mode == 'act':
        base_prompt += """

⚡ ACT MODE - ACTION FOCUS:
• Prioritize direct action and results
• Provide clear, executable steps
• Minimize explanations unless critical for safety
• Use imperative language and action verbs
• Break complex tasks into numbered steps
• Focus on efficiency and task completion"""

    elif interaction_mode == 'hybrid':
        base_prompt += """

🧠 HYBRID MODE - ADAPTIVE RESPONSE:
• Analyze user intent to determine response style
• Use educational approach for questions and learning
• Use action-oriented approach for tasks and commands
• Seamlessly switch between modes within responses
• Adapt detail level based on user's apparent expertise"""

    return base_prompt

def show_message_box(message: str, title: str = "S647", icon: str = 'INFO'):
    """Show a message box to the user"""
    def draw(self, context):
        self.layout.label(text=message)
    
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def log_message(message: str, level: str = 'INFO'):
    """Log a message with timestamp"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[S647 {timestamp}] {level}: {message}")

# Global constants
BLENDER_PYTHON_DOCS_URL = "https://docs.blender.org/api/current/"
OPENAI_MODELS = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
MAX_CONTEXT_LENGTH = 8000  # Conservative limit for context
