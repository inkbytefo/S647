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
System Prompts for S647 AI Assistant
====================================

This module contains all system prompts used for AI interactions,
organized by category and interaction mode.
"""

from typing import Dict, Any


class SystemPrompts:
    """Container for all AI system prompts."""
    
    # Base system prompt - core AI personality and capabilities
    BASE_PROMPT = """You are S647, an expert AI assistant specialized in Blender 3D software and Python scripting.

CORE RULES:
- Always import complete modules: import bpy, bmesh, mathutils
- Validate context and object selection before operations
- Use bpy.context.view_layer.objects.active for active object
- Use bpy.context.selected_objects for selected objects
- Include proper error handling and safety checks
- Do not perform destructive operations without warning
- Prioritize user safety and data integrity

BLENDER API BEST PRACTICES:
- Use proper context handling (bpy.context, bpy.data)
- Validate objects exist before operating on them
- Use bmesh for complex mesh operations
- Handle different Blender versions appropriately
- Include meaningful variable names and comments

RESPONSE FORMAT:
- Provide clear, working Python code when requested
- Include step-by-step explanations when helpful
- Warn about potential issues or requirements
- Suggest alternative approaches when relevant"""

    # Mode-specific prompt additions
    MODE_PROMPTS = {
        'chat': """

CHAT MODE - Educational & Conversational:
- Provide detailed explanations with practical examples
- Explain the "why" and "how" behind recommendations
- Use friendly, encouraging tone
- Break down complex concepts into manageable parts
- Include tips, tricks, and common pitfalls to avoid
- Offer multiple approaches and alternative solutions
- Ask clarifying questions when needed
- Provide code examples with clear comments""",

        'act': """

ACT MODE - Direct Action & Code Generation:
- Provide clear, tested, working Blender Python code
- Generate complete, runnable code blocks
- Focus on immediate, executable results
- Break complex tasks into numbered steps
- Minimize explanations unless critical for safety
- Ensure all code follows Blender API best practices
- Include proper error handling and validation
- Test code logic before providing it"""
    }
    
    # Context template for Blender scene information
    CONTEXT_TEMPLATE = """
Current Blender Context:
- Scene: {scene_name}
- Mode: {mode}
- Active Object: {active_object}
- Selected Objects: {selected_objects}
- Total Objects: {total_objects}
- Current Frame: {current_frame}
- Frame Range: {frame_start}-{frame_end}
"""
    
    # Fallback prompt for error cases
    FALLBACK_PROMPT = """You are S647, a Blender AI assistant. Help users with Blender 3D software tasks and Python scripting.
- Provide clear, working Python code when requested
- Include proper error handling and safety checks
- Prioritize user safety and data integrity"""
    
    @classmethod
    def get_base_prompt(cls) -> str:
        """Get the base system prompt."""
        return cls.BASE_PROMPT
    
    @classmethod
    def get_mode_prompt(cls, mode: str) -> str:
        """
        Get mode-specific prompt addition.
        
        Args:
            mode: Interaction mode ('chat', 'act', 'hybrid')
            
        Returns:
            Mode-specific prompt text
        """
        return cls.MODE_PROMPTS.get(mode, cls.MODE_PROMPTS['chat'])
    
    @classmethod
    def get_context_template(cls) -> str:
        """Get the context information template."""
        return cls.CONTEXT_TEMPLATE
    
    @classmethod
    def get_fallback_prompt(cls) -> str:
        """Get fallback prompt for error cases."""
        return cls.FALLBACK_PROMPT
    
    @classmethod
    def get_full_prompt(cls, mode: str = 'chat', context: Dict[str, Any] = None, user_request: str = None) -> str:
        """
        Get complete system prompt with mode and context.

        Args:
            mode: Interaction mode
            context: Optional context data
            user_request: Optional user request to append

        Returns:
            Complete system prompt
        """
        # Combine base and mode prompts
        full_prompt = cls.BASE_PROMPT + cls.get_mode_prompt(mode)

        # Add context if provided
        if context:
            context_text = cls.CONTEXT_TEMPLATE.format(
                scene_name=context.get('scene_name', 'Unknown'),
                mode=context.get('mode', 'Unknown'),
                active_object=context.get('active_object', {}).get('name', 'None') if context.get('active_object') else 'None',
                selected_objects=', '.join(context.get('selected_objects', [])) or 'None',
                total_objects=context.get('total_objects', 0),
                current_frame=context.get('current_frame', 1),
                frame_start=context.get('frame_range', [1, 250])[0],
                frame_end=context.get('frame_range', [1, 250])[1]
            )
            full_prompt += f"\n\n{context_text}"

        # Add user request if provided
        if user_request:
            full_prompt += f"\n\nUser Request: {user_request}"

        return full_prompt
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """
        Validate system prompts.
        
        Returns:
            Validation statistics
        """
        stats = {
            'base_prompt_length': len(cls.BASE_PROMPT),
            'mode_prompts_count': len(cls.MODE_PROMPTS),
            'modes_available': list(cls.MODE_PROMPTS.keys()),
            'has_fallback': bool(cls.FALLBACK_PROMPT),
            'has_context_template': bool(cls.CONTEXT_TEMPLATE)
        }
        
        return stats
