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
System Messages for S647 Blender Addon
=======================================

This module contains all system messages including errors, warnings,
information messages, and notifications used throughout the addon.
"""

from typing import Dict, Any


class Messages:
    """Container for all system messages."""
    
    # Error messages
    ERROR_MESSAGES = {
        'api_key_missing': "⚠️ Configure AI provider in preferences",
        'api_key_invalid': "⚠️ Invalid API key format",
        'ai_engine_not_ready': "⚠️ AI engine not ready",
        'connection_failed': "❌ Failed to connect to AI service",
        'request_failed': "❌ AI request failed",
        'code_execution_blocked': "🚫 Code execution blocked due to safety concerns",
        'code_execution_failed': "❌ Code execution failed",
        'file_not_found': "❌ File not found: {filename}",
        'invalid_configuration': "❌ Invalid configuration",
        'mcp_not_available': "❌ MCP SDK not available",
        'mcp_manager_not_initialized': "❌ MCP Manager not initialized",
        'server_connection_failed': "❌ Failed to connect to server",
        'validation_failed': "❌ Validation failed",
        'unknown_error': "❌ An unknown error occurred"
    }
    
    # Warning messages
    WARNING_MESSAGES = {
        'api_key_missing_openai': "⚠️ API key required for S647 to function",
        'custom_provider_incomplete': "⚠️ All custom provider fields are required",
        'automatic_execution_dangerous': "⚠️ Automatic code execution can be dangerous!",
        'safety_warnings_detected': "⚠️ Safety Warnings:",
        'code_execution_disabled': "⚠️ Code execution disabled",
        'no_suggestions_available': "⚠️ No suggestions available",
        'context_memory_full': "⚠️ Context memory approaching limit",
        'conversation_limit_reached': "⚠️ Conversation history limit reached",
        'mcp_sdk_missing': "⚠️ MCP SDK not available",
        'voice_not_available': "⚠️ Voice input not available",
        'feature_coming_soon': "⚠️ Feature coming soon"
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        'connection_successful': "✅ Connection successful",
        'code_executed_successfully': "✅ Code executed successfully",
        'file_saved': "✅ File saved successfully",
        'configuration_updated': "✅ Configuration updated",
        'context_saved': "✅ Context saved",
        'context_loaded': "✅ Context loaded",
        'context_cleared': "✅ All context cleared",
        'conversation_saved': "✅ Conversation saved",
        'conversation_cleared': "✅ Conversation cleared",
        'suggestion_applied': "✅ Applied suggestion",
        'server_connected': "✅ Server connected",
        'server_disconnected': "✅ Server disconnected",
        'import_successful': "✅ Import successful",
        'export_successful': "✅ Export successful"
    }
    
    # Information messages
    INFO_MESSAGES = {
        'ai_engine_ready': "✓ AI Engine Ready",
        'ai_engine_initializing': "🔄 Initializing AI engine...",
        'processing_request': "🔄 Processing request...",
        'analyzing_context': "🔍 Analyzing Blender context...",
        'generating_response': "💭 Generating response...",
        'executing_code': "⚙️ Executing code...",
        'saving_context': "💾 Saving context...",
        'loading_context': "📂 Loading context...",
        'connecting_server': "🔗 Connecting to server...",
        'mcp_integration_disabled': "ℹ️ MCP integration disabled",
        'no_servers_configured': "ℹ️ No servers configured",
        'debug_info_printed': "ℹ️ Debug info printed to console",
        'feature_disabled': "ℹ️ Feature disabled in preferences"
    }
    
    # Configuration messages
    CONFIG_MESSAGES = {
        'openai_api_key_format': "Invalid OpenAI API key format (should start with 'sk-')",
        'openai_quota_exceeded': "OpenAI quota exceeded or billing issue",
        'openai_rate_limit': "OpenAI rate limit exceeded",
        'openai_model_not_found': "Requested model not available",
        'network_connection_error': "Network connection error",
        'custom_provider_configured': "✓ Custom provider configured",
        'openai_provider_configured': "✓ OpenAI API Key configured",
        'provider_not_configured': "✗ Provider not fully configured",
        'mcp_sdk_available': "✓ MCP SDK available",
        'configuration_valid': "✓ Configuration valid"
    }
    
    # Status messages
    STATUS_MESSAGES = {
        'idle': "Ready",
        'thinking': "Thinking...",
        'responding': "Responding...",
        'error': "Error",
        'connecting': "Connecting...",
        'connected': "Connected",
        'disconnected': "Disconnected",
        'initializing': "Initializing...",
        'processing': "Processing...",
        'executing': "Executing...",
        'completed': "Completed",
        'failed': "Failed",
        'cancelled': "Cancelled"
    }
    
    # Help and guidance messages
    HELP_MESSAGES = {
        'get_api_key_openai': "Get your API key from: https://platform.openai.com/api-keys",
        'install_mcp_sdk': "Install with: pip install mcp",
        'enable_in_preferences': "Enable in Preferences",
        'configure_in_preferences': "Configure in Preferences",
        'check_configuration': "Check configuration",
        'contact_support': "Contact support if the problem persists",
        'backup_recommended': "Backup recommended before proceeding",
        'restart_blender': "Restart Blender to apply changes"
    }
    
    @classmethod
    def get_message(cls, key: str, level: str = 'info') -> str:
        """
        Get message by key and level.
        
        Args:
            key: Message identifier
            level: Message level ('error', 'warning', 'success', 'info', 'config', 'status', 'help')
            
        Returns:
            Message string
        """
        message_dict = {
            'error': cls.ERROR_MESSAGES,
            'warning': cls.WARNING_MESSAGES,
            'success': cls.SUCCESS_MESSAGES,
            'info': cls.INFO_MESSAGES,
            'config': cls.CONFIG_MESSAGES,
            'status': cls.STATUS_MESSAGES,
            'help': cls.HELP_MESSAGES
        }.get(level, cls.INFO_MESSAGES)
        
        return message_dict.get(key, f"[Missing {level}: {key}]")
    
    @classmethod
    def get_error(cls, key: str) -> str:
        """Get error message by key."""
        return cls.get_message(key, 'error')
    
    @classmethod
    def get_warning(cls, key: str) -> str:
        """Get warning message by key."""
        return cls.get_message(key, 'warning')
    
    @classmethod
    def get_success(cls, key: str) -> str:
        """Get success message by key."""
        return cls.get_message(key, 'success')
    
    @classmethod
    def get_info(cls, key: str) -> str:
        """Get info message by key."""
        return cls.get_message(key, 'info')
    
    @classmethod
    def get_config(cls, key: str) -> str:
        """Get configuration message by key."""
        return cls.get_message(key, 'config')
    
    @classmethod
    def get_status(cls, key: str) -> str:
        """Get status message by key."""
        return cls.get_message(key, 'status')
    
    @classmethod
    def get_help(cls, key: str) -> str:
        """Get help message by key."""
        return cls.get_message(key, 'help')
    
    @classmethod
    def validate(cls) -> Dict[str, int]:
        """
        Validate messages and return statistics.
        
        Returns:
            Validation statistics
        """
        return {
            'error_messages': len(cls.ERROR_MESSAGES),
            'warning_messages': len(cls.WARNING_MESSAGES),
            'success_messages': len(cls.SUCCESS_MESSAGES),
            'info_messages': len(cls.INFO_MESSAGES),
            'config_messages': len(cls.CONFIG_MESSAGES),
            'status_messages': len(cls.STATUS_MESSAGES),
            'help_messages': len(cls.HELP_MESSAGES)
        }
