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
S647 Preferences Module
=======================

Handles addon preferences including OpenAI API configuration,
safety settings, and user interface options.
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    IntProperty,
    FloatProperty,
)

class S647AddonPreferences(AddonPreferences):
    """S647 Addon Preferences"""
    bl_idname = __package__

    def _get_ui_text(self, key: str, **kwargs) -> str:
        """Get UI text using centralized prompt system with fallback"""
        try:
            from .prompts import PromptManager
            return PromptManager.get_ui_text(key, **kwargs)
        except (ImportError, Exception):
            # Fallback texts for preferences
            fallback_texts = {
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
            return fallback_texts.get(key, f"[{key}]")
    
    # AI Provider Settings
    provider_type: EnumProperty(
        name="AI Provider",
        description="Choose the AI provider to use",
        items=[
            ('openai', 'OpenAI', 'Use OpenAI API (GPT models)'),
            ('custom', 'Custom OpenAI-Compatible', 'Use custom OpenAI-compatible API'),
        ],
        default='openai',
    )

    # OpenAI API Settings
    api_key: StringProperty(
        name="API Key",
        description="Your API key for accessing AI models",
        default="",
        subtype='PASSWORD',
    )

    api_model: EnumProperty(
        name="AI Model",
        description="Choose the OpenAI model to use",
        items=[
            ('gpt-4o', 'GPT-4o', 'Latest GPT-4 Optimized model (Recommended)'),
            ('gpt-4o-mini', 'GPT-4o Mini', 'Faster, cost-effective model'),
            ('gpt-4-turbo', 'GPT-4 Turbo', 'Previous generation GPT-4'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo', 'Fast and economical'),
        ],
        default='gpt-4o',
    )

    # Custom Provider Settings
    custom_base_url: StringProperty(
        name="Base URL",
        description="Base URL for custom OpenAI-compatible API (e.g., https://api.anthropic.com/v1)",
        default="",
    )

    custom_model: StringProperty(
        name="Model Name",
        description="Model name for custom provider (e.g., claude-3-5-sonnet-20241022)",
        default="",
    )

    custom_api_key: StringProperty(
        name="Custom API Key",
        description="API key for custom provider",
        default="",
        subtype='PASSWORD',
    )
    
    max_tokens: IntProperty(
        name="Max Tokens",
        description="Maximum number of tokens for AI responses",
        default=2000,
        min=100,
        max=8000,
    )
    
    temperature: FloatProperty(
        name="Temperature",
        description="Controls randomness in AI responses (0.0 = deterministic, 1.0 = creative)",
        default=0.7,
        min=0.0,
        max=1.0,
        precision=2,
    )
    
    # Code Execution (simplified)
    enable_code_execution: BoolProperty(
        name="Enable Code Execution",
        description="Allow AI to execute Python code in Blender (safe operations only)",
        default=True,
    )
    
    # UI Settings
    show_advanced_options: BoolProperty(
        name="Show Advanced Options",
        description="Display advanced AI and execution settings in the panel",
        default=False,
    )
    
    auto_save_conversations: BoolProperty(
        name="Auto-save Conversations",
        description="Automatically save conversation history",
        default=True,
    )
    
    conversation_history_limit: IntProperty(
        name="Conversation History Limit",
        description="Maximum number of messages to keep in history",
        default=50,
        min=10,
        max=200,
    )

    # Mode Settings
    default_interaction_mode: EnumProperty(
        name="Default Interaction Mode",
        description="Default mode when starting S647",
        items=[
            ('chat', 'Chat Mode', 'Start in conversational mode'),
            ('act', 'Act Mode', 'Start in action-oriented mode'),
        ],
        default='chat',
    )



    # MCP Settings
    enable_mcp: BoolProperty(
        name="Enable MCP Integration",
        description="Enable Model Context Protocol server integration",
        default=True,
    )

    mcp_auto_connect: BoolProperty(
        name="Auto-connect MCP Servers",
        description="Automatically connect to enabled MCP servers on startup",
        default=True,
    )

    mcp_server_configs: StringProperty(
        name="MCP Server Configurations",
        description="JSON configuration for MCP servers",
        default="{}",
    )

    mcp_tool_confirmation: BoolProperty(
        name="Require Tool Confirmation",
        description="Require user confirmation before executing MCP tools",
        default=False,
    )


    
    def draw(self, context):
        """Draw the preferences UI"""
        layout = self.layout
        
        # AI Provider Configuration Section
        box = layout.box()
        box.label(text=self._get_ui_text("ai_provider_config"), icon='NETWORK_DRIVE')

        col = box.column()
        col.prop(self, "provider_type")

        # OpenAI Settings
        if self.provider_type == 'openai':
            col.separator()
            col.label(text=self._get_ui_text("openai_settings"))
            col.prop(self, "api_key")

            if not self.api_key:
                col.label(text=self._get_ui_text("api_key_required"), icon='ERROR')
                col.label(text=self._get_ui_text("get_api_key"))

            col.prop(self, "api_model")

        # Custom Provider Settings
        elif self.provider_type == 'custom':
            col.separator()
            col.label(text=self._get_ui_text("custom_provider_settings"))
            col.prop(self, "custom_base_url")
            col.prop(self, "custom_model")
            col.prop(self, "custom_api_key")

            if not self.custom_base_url or not self.custom_model or not self.custom_api_key:
                col.label(text=self._get_ui_text("custom_fields_required"), icon='ERROR')

            # Examples
            col.separator()
            col.label(text="Examples:", icon='INFO')
            col.label(text="• Anthropic: https://api.anthropic.com/v1")
            col.label(text="• Groq: https://api.groq.com/openai/v1")
            col.label(text="• Local Ollama: http://localhost:11434/v1")

        col.separator()
        row = col.row(align=True)
        row.prop(self, "max_tokens")
        row.prop(self, "temperature")

        # AI Config Manager Test Section
        col.separator()
        test_box = col.box()
        test_box.label(text=self._get_ui_text("connection_test"), icon='NETWORK_DRIVE')

        test_row = test_box.row(align=True)
        test_row.operator("s647.test_ai_config", text="Test Configuration", icon='PLAY')
        test_row.operator("s647.reinitialize_ai", text="Reinitialize", icon='FILE_REFRESH')

        # Show current status if available
        try:
            from . import ai_engine
            status = ai_engine.get_api_status()
            if status.get('initialized'):
                status_box = test_box.box()
                status_box.label(text=self._get_ui_text("ai_engine_ready"), icon='CHECKMARK')
                if 'provider_status' in status:
                    status_box.label(text=f"Status: {status['provider_status']}")
                if 'provider_message' in status:
                    status_box.label(text=f"Message: {status['provider_message']}")
            else:
                status_box = test_box.box()
                status_box.label(text=self._get_ui_text("ai_engine_not_ready"), icon='ERROR')
        except Exception:
            pass
        

        
        # UI Settings Section
        box = layout.box()
        box.label(text="Interface Settings", icon='TOOL_SETTINGS')
        
        col = box.column()
        col.prop(self, "show_advanced_options")
        col.prop(self, "auto_save_conversations")
        col.prop(self, "conversation_history_limit")

        # Mode Settings Section (simplified)
        box = layout.box()
        box.label(text="Interaction Modes", icon='SETTINGS')

        col = box.column()
        col.prop(self, "default_interaction_mode")

        # MCP Settings Section
        box = layout.box()
        box.label(text="Model Context Protocol (MCP)", icon='NETWORK_DRIVE')

        col = box.column()
        col.prop(self, "enable_mcp")
        col.prop(self, "mcp_tool_confirmation")

        if self.enable_mcp:

            # MCP Status
            try:
                from . import mcp_client
                if mcp_client.is_mcp_available():
                    col.label(text="✓ MCP SDK available", icon='CHECKMARK')

                    manager = mcp_client.get_mcp_manager()
                    if manager:
                        servers = manager.get_all_servers()
                        tools = manager.get_all_tools()
                        col.label(text=f"Servers: {len(servers)}, Tools: {len(tools)}")
                    else:
                        col.label(text="MCP Manager not initialized")
                else:
                    col.label(text="⚠️ MCP SDK not available", icon='ERROR')
                    col.label(text="Install with: pip install mcp")
            except ImportError:
                col.label(text="⚠️ MCP module not found", icon='ERROR')

            # Configuration management
            layout.separator()
            config_box = col.box()
            config_box.label(text="Configuration Management:", icon='SETTINGS')

            config_row = config_box.row()
            config_row.operator("s647.import_mcp_config", text="Import JSON Config", icon='IMPORT')
            config_row.operator("s647.export_mcp_config", text="Export Config", icon='EXPORT')

            config_row2 = config_box.row()
            config_row2.operator("s647.load_mcp_config_file", text="Load mcp.json", icon='FILE_REFRESH')
            config_row2.operator("s647.manage_mcp_servers", text="Manage Servers", icon='SETTINGS')
        else:
            col.label(text="MCP integration disabled")
        
        # Status and Info Section
        box = layout.box()
        box.label(text="Status & Information", icon='INFO')
        
        col = box.column()

        # Provider status
        col.label(text=f"Provider: {self.provider_type.upper()}")

        if self.provider_type == 'openai':
            if self.api_key:
                col.label(text="✓ OpenAI API Key configured", icon='CHECKMARK')
            else:
                col.label(text="✗ OpenAI API Key not configured", icon='X')
            col.label(text=f"Model: {self.api_model}")

        elif self.provider_type == 'custom':
            if self.custom_base_url and self.custom_model and self.custom_api_key:
                col.label(text="✓ Custom provider configured", icon='CHECKMARK')
                col.label(text=f"URL: {self.custom_base_url}")
                col.label(text=f"Model: {self.custom_model}")
            else:
                col.label(text="✗ Custom provider not fully configured", icon='X')

        col.label(text=f"Code Execution: {'✓ Enabled' if self.enable_code_execution else '✗ Disabled'}")

def get_preferences():
    """Get the addon preferences"""
    return bpy.context.preferences.addons[__package__].preferences

def register():
    """Register preferences"""
    bpy.utils.register_class(S647AddonPreferences)

def unregister():
    """Unregister preferences"""
    bpy.utils.unregister_class(S647AddonPreferences)
