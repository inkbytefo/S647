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
S647 Centralized Prompt Management System
=========================================

This module provides a centralized system for managing all prompts, UI texts,
and messages used throughout the S647 Blender addon.

Features:
- Centralized prompt storage and management
- Template-based dynamic prompt generation
- Mode-specific prompt variations
- Localization support structure
- Type-safe prompt access
- Validation and error handling

Usage:
    from .prompts import PromptManager
    
    # Get system prompt
    prompt = PromptManager.get_system_prompt(mode='chat')
    
    # Get UI text
    text = PromptManager.get_ui_text('send_button', mode='act')
    
    # Get message
    msg = PromptManager.get_message('api_key_missing')
"""

from typing import Dict, Any, Optional, Union
import logging

from .system_prompts import SystemPrompts
from .ui_texts import UITexts
from .messages import Messages
from .templates import TemplateEngine

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Central manager for all prompts, texts, and messages in S647.
    
    This class provides a unified interface for accessing all text content
    used throughout the addon, with support for templates, modes, and
    future localization.
    """
    
    _template_engine = None
    _current_language = 'en'
    
    @classmethod
    def initialize(cls, language: str = 'en') -> None:
        """
        Initialize the prompt manager with specified language.
        
        Args:
            language: Language code (default: 'en')
        """
        cls._current_language = language
        cls._template_engine = TemplateEngine()
        logger.info(f"PromptManager initialized with language: {language}")
    
    @classmethod
    def get_system_prompt(cls,
                         mode: str = 'chat',
                         context: Optional[Dict[str, Any]] = None,
                         **kwargs) -> str:
        """
        Get system prompt for AI with mode-specific variations.

        Args:
            mode: Interaction mode ('chat', 'act', 'hybrid')
            context: Optional context data for template variables
            **kwargs: Additional template variables

        Returns:
            Complete system prompt string
        """
        try:
            # Extract user_request from kwargs if present
            user_request = kwargs.pop('user_request', None)

            # Get complete prompt using SystemPrompts
            full_prompt = SystemPrompts.get_full_prompt(
                mode=mode,
                context=context,
                user_request=user_request
            )

            # Apply additional template processing if needed
            if kwargs:
                full_prompt = cls._apply_template(full_prompt, kwargs)

            return full_prompt

        except Exception as e:
            logger.error(f"Error getting system prompt: {e}")
            return SystemPrompts.get_fallback_prompt()
    
    @classmethod
    def get_ui_text(cls, 
                   key: str, 
                   mode: Optional[str] = None,
                   **kwargs) -> str:
        """
        Get UI text with optional mode-specific variations.
        
        Args:
            key: Text identifier key
            mode: Optional interaction mode for mode-specific text
            **kwargs: Template variables
            
        Returns:
            UI text string
        """
        try:
            text = UITexts.get_text(key, mode)
            
            # Apply template processing if variables provided
            if kwargs:
                text = cls._apply_template(text, kwargs)
            
            return text
            
        except Exception as e:
            logger.error(f"Error getting UI text '{key}': {e}")
            return f"[Missing: {key}]"
    
    @classmethod
    def get_message(cls, 
                   key: str, 
                   level: str = 'info',
                   **kwargs) -> str:
        """
        Get system message (error, warning, info, etc.).
        
        Args:
            key: Message identifier key
            level: Message level ('error', 'warning', 'info', 'success')
            **kwargs: Template variables
            
        Returns:
            Message string
        """
        try:
            message = Messages.get_message(key, level)
            
            # Apply template processing if variables provided
            if kwargs:
                message = cls._apply_template(message, kwargs)
            
            return message
            
        except Exception as e:
            logger.error(f"Error getting message '{key}': {e}")
            return f"[Missing message: {key}]"
    
    @classmethod
    def get_placeholder_text(cls, 
                           context: str, 
                           mode: Optional[str] = None) -> str:
        """
        Get placeholder text for input fields.
        
        Args:
            context: Context identifier ('input', 'search', etc.)
            mode: Optional interaction mode
            
        Returns:
            Placeholder text string
        """
        return UITexts.get_placeholder(context, mode)
    
    @classmethod
    def get_status_text(cls, 
                       status: str, 
                       **kwargs) -> str:
        """
        Get status indicator text.
        
        Args:
            status: Status identifier ('thinking', 'responding', 'error', etc.)
            **kwargs: Template variables
            
        Returns:
            Status text string
        """
        try:
            text = UITexts.get_status_text(status)
            
            if kwargs:
                text = cls._apply_template(text, kwargs)
            
            return text
            
        except Exception as e:
            logger.error(f"Error getting status text '{status}': {e}")
            return f"Status: {status}"
    
    @classmethod
    def _apply_template(cls, text: str, variables: Dict[str, Any]) -> str:
        """
        Apply template processing to text with variables.
        
        Args:
            text: Template text
            variables: Template variables
            
        Returns:
            Processed text
        """
        if not cls._template_engine:
            cls.initialize()
        
        return cls._template_engine.render(text, variables)
    
    @classmethod
    def validate_prompts(cls) -> Dict[str, Any]:
        """
        Validate all prompts and return validation report.
        
        Returns:
            Validation report dictionary
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Validate system prompts
            system_validation = SystemPrompts.validate()
            report['stats']['system_prompts'] = system_validation
            
            # Validate UI texts
            ui_validation = UITexts.validate()
            report['stats']['ui_texts'] = ui_validation
            
            # Validate messages
            message_validation = Messages.validate()
            report['stats']['messages'] = message_validation
            
        except Exception as e:
            report['valid'] = False
            report['errors'].append(f"Validation error: {e}")
        
        return report


# Initialize on import
PromptManager.initialize()

# Export main interface
__all__ = ['PromptManager']
