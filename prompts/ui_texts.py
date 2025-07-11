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
UI Texts for S647 Blender Addon
===============================

This module contains all user interface texts, labels, and descriptions
used throughout the S647 addon interface.
"""

from typing import Dict, Optional


class UITexts:
    """Container for all UI texts and labels."""
    
    # Panel titles and headers
    PANEL_TITLES = {
        'main_panel': "S647 AI Assistant",
        'context_panel': "Context & Memory",
        'suggestions_panel': "Smart Suggestions",
        'advanced_panel': "Advanced Options",
        'code_execution_panel': "Code Execution",
        'mcp_panel': "MCP Integration"
    }
    
    # Button texts with mode variations
    BUTTON_TEXTS = {
        'send': {
            'chat': "💬 Send",
            'act': "⚡ Execute",
            'default': "Send"
        },
        'clear': "🗑️ Clear",
        'save': "💾 Save",
        'copy': "📋 Copy",
        'execute': "▶ Apply",
        'explain': "❓ Explain",
        'modify': "✏️ Modify",
        # Removed unused quick action buttons
        'settings': "⚙️ Settings",
        'test_connection': "Test Connection",
        'reinitialize': "Reinitialize",
        'debug': "Debug Info",
        'refresh': "Refresh",
        'toggle': "Toggle",
        'new_thread': "New",
        'rename_thread': "Rename",
        'import': "Import",
        'export': "Export",
        'manage': "Manage",
        'connect': "Connect",
        'disconnect': "Disconnect"
    }
    
    # Input placeholders with mode variations
    PLACEHOLDERS = {
        'input': {
            'chat': "💬 Ask me anything about Blender...",
            'act': "⚡ Tell me what to do in Blender...",
            'default': "Type your message..."
        },
        'search': "🔍 Search...",
        'filename': "Enter filename...",
        'url': "Enter URL...",
        'api_key': "Enter API key..."
    }
    
    # Status indicators
    STATUS_TEXTS = {
        'thinking': "🤖 S647 is thinking...",
        'responding': "🤖 S647 is responding...",
        'error': "❌ Error occurred",
        'ready': "✅ Ready",
        'idle': "💤 Idle",
        'busy': "⏳ AI is busy...",
        'connected': "✓ Connected",
        'disconnected': "✗ Not Connected",
        'connecting': "⏳ Connecting...",
        'code_executed': "✅ Code executed successfully",
        'code_pending': "📝 Contains executable code"
    }
    
    # Mode descriptions
    MODE_DESCRIPTIONS = {
        'chat': "💬 Educational Focus - Learn, discuss, and manually execute code",
        'act': "⚡ Action Focus - Direct execution with auto-running code"
    }

    # Welcome messages
    WELCOME_MESSAGES = {
        'main': "👋 Welcome to S647!",
        'chat': "💬 Ask me anything about Blender - I'll explain and provide code for you to review!",
        'act': "⚡ Tell me what to do in Blender - I'll generate and auto-execute safe code!",
        'quick_start': "Try: 'Create a cube' or 'How do I add materials?'"
    }
    
    # Section headers
    SECTION_HEADERS = {
        'interaction_mode': "Interaction Mode",
        'conversation': "💬 Conversation",
        'message': "✍️ Message",
        # 'quick_actions' removed - functionality simplified
        'thread_management': "Conversation Thread:",
        'memory_status': "Memory Status:",
        'memory_actions': "Memory Actions:",
        'suggestion_controls': "Suggestion Controls:",
        'context_settings': "Context Settings:",
        'ai_configuration': "AI Configuration:",
        'safety_settings': "Safety Settings:",
        'api_status': "API Status:",
        'statistics': "Statistics:",
        'pending_code': "Pending Code:",
        'execution_result': "Last Execution Result:",
        'server_status': "Server Status:",
        'configuration': "Configuration:",
        'connection_test': "Connection Test:"
    }
    
    # Information and help texts
    INFO_TEXTS = {
        'character_count': "📝 {count} characters",
        'message_count': "💬 {count} messages in conversation",
        'more_lines': "... ({count} more lines)",
        'more_messages': "... and {count} more messages",
        'total_threads': "Total threads: {count}",
        'current_thread_messages': "Messages in current: {count}",
        'available_tools': "Available Tools ({count}):",
        'available_resources': "Available Resources ({count}):",
        'servers_tools_count': "Servers: {servers}, Tools: {tools}",
        'success_rate': "Success Rate: {rate:.1f}%"
    }

    # Additional UI texts for preferences and other components
    PREFERENCE_TEXTS = {
        'ai_provider_config': "AI Provider Configuration",
        'openai_settings': "OpenAI Settings:",
        'custom_provider_settings': "Custom Provider Settings:",
        'connection_test': "Connection Test:",
        'safety_execution_settings': "Safety & Execution Settings",
        'interface_settings': "Interface Settings",
        'interaction_modes': "Interaction Modes",
        'mcp_protocol': "Model Context Protocol (MCP)",
        'status_information': "Status & Information",
        'configuration_management': "Configuration Management:",
        'api_key_required': "⚠️ API key required for S647 to function",
        'get_api_key': "Get your API key from: https://platform.openai.com/api-keys",
        'custom_fields_required': "⚠️ All custom provider fields are required",
        'automatic_execution_dangerous': "⚠️ Automatic code execution can be dangerous!",
        'ai_engine_ready': "✓ AI Engine Ready",
        'ai_engine_not_ready': "⚠️ AI Engine Not Ready",
        'mcp_sdk_available': "✓ MCP SDK available",
        'mcp_sdk_not_available': "⚠️ MCP SDK not available",
        'install_mcp': "Install with: pip install mcp",
        'mcp_integration_disabled': "MCP integration disabled",
        'openai_configured': "✓ OpenAI API Key configured",
        'openai_not_configured': "✗ OpenAI API Key not configured",
        'custom_provider_configured': "✓ Custom provider configured",
        'custom_provider_not_configured': "✗ Custom provider not fully configured",
        'code_execution_enabled': "Enabled",
        'code_execution_disabled': "Disabled"
    }
    
    @classmethod
    def get_text(cls, key: str, mode: Optional[str] = None) -> str:
        """
        Get UI text by key with optional mode variation.

        Args:
            key: Text identifier
            mode: Optional interaction mode

        Returns:
            UI text string
        """
        # Handle mode description pattern: mode_description_{mode}
        if key.startswith('mode_description_'):
            mode_name = key.replace('mode_description_', '')
            if mode_name in cls.MODE_DESCRIPTIONS:
                return cls.MODE_DESCRIPTIONS[mode_name]

        # Check for mode-specific variations first
        if mode and key in cls.BUTTON_TEXTS:
            mode_texts = cls.BUTTON_TEXTS[key]
            if isinstance(mode_texts, dict):
                return mode_texts.get(mode, mode_texts.get('default', key))

        # Check for mode-specific placeholders
        if mode and key in cls.PLACEHOLDERS:
            placeholder = cls.PLACEHOLDERS[key]
            if isinstance(placeholder, dict):
                return placeholder.get(mode, placeholder.get('default', ''))

        # Check button texts
        if key in cls.BUTTON_TEXTS:
            text = cls.BUTTON_TEXTS[key]
            return text if isinstance(text, str) else text.get('default', key)

        # Check placeholders
        if key in cls.PLACEHOLDERS:
            placeholder = cls.PLACEHOLDERS[key]
            return placeholder if isinstance(placeholder, str) else placeholder.get('default', '')
        
        # Check panel titles
        if key in cls.PANEL_TITLES:
            return cls.PANEL_TITLES[key]
        
        # Check section headers
        if key in cls.SECTION_HEADERS:
            return cls.SECTION_HEADERS[key]
        
        # Check status texts
        if key in cls.STATUS_TEXTS:
            return cls.STATUS_TEXTS[key]
        
        # Check mode descriptions
        if key in cls.MODE_DESCRIPTIONS:
            return cls.MODE_DESCRIPTIONS[key]
        
        # Check welcome messages
        if key in cls.WELCOME_MESSAGES:
            return cls.WELCOME_MESSAGES[key]
        
        # Check info texts
        if key in cls.INFO_TEXTS:
            return cls.INFO_TEXTS[key]

        # Check preference texts
        if key in cls.PREFERENCE_TEXTS:
            return cls.PREFERENCE_TEXTS[key]

        # Fallback
        return f"[Missing: {key}]"
    
    @classmethod
    def get_placeholder(cls, context: str, mode: Optional[str] = None) -> str:
        """
        Get placeholder text for input fields.
        
        Args:
            context: Placeholder context ('input', 'search', etc.)
            mode: Optional interaction mode
            
        Returns:
            Placeholder text
        """
        if context in cls.PLACEHOLDERS:
            placeholder = cls.PLACEHOLDERS[context]
            if isinstance(placeholder, dict) and mode:
                return placeholder.get(mode, placeholder.get('default', ''))
            return placeholder if isinstance(placeholder, str) else ''
        
        return ''
    
    @classmethod
    def get_status_text(cls, status: str) -> str:
        """
        Get status indicator text.
        
        Args:
            status: Status identifier
            
        Returns:
            Status text
        """
        return cls.STATUS_TEXTS.get(status, f"Status: {status}")
    
    @classmethod
    def validate(cls) -> Dict[str, int]:
        """
        Validate UI texts and return statistics.
        
        Returns:
            Validation statistics
        """
        return {
            'panel_titles': len(cls.PANEL_TITLES),
            'button_texts': len(cls.BUTTON_TEXTS),
            'placeholders': len(cls.PLACEHOLDERS),
            'status_texts': len(cls.STATUS_TEXTS),
            'mode_descriptions': len(cls.MODE_DESCRIPTIONS),
            'welcome_messages': len(cls.WELCOME_MESSAGES),
            'section_headers': len(cls.SECTION_HEADERS),
            'info_texts': len(cls.INFO_TEXTS),
            'preference_texts': len(cls.PREFERENCE_TEXTS)
        }
