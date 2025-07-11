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
    
    # Safety Settings
    enable_code_execution: BoolProperty(
        name="Enable Code Execution",
        description="Allow the AI to execute Python code in Blender (CAUTION: Only enable if you trust the AI responses)",
        default=False,
    )
    
    confirm_before_execution: BoolProperty(
        name="Confirm Before Execution",
        description="Show confirmation dialog before executing AI-generated code",
        default=True,
    )
    
    sandbox_mode: BoolProperty(
        name="Sandbox Mode",
        description="Run code in restricted environment (limits some Blender operations)",
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
            ('hybrid', 'Hybrid Mode', 'Start in intelligent switching mode'),
        ],
        default='chat',
    )

    enable_smart_mode_switching: BoolProperty(
        name="Smart Mode Switching",
        description="Allow AI to automatically switch modes based on context",
        default=True,
    )

    enable_context_persistence: BoolProperty(
        name="Context Persistence",
        description="Save and restore conversation context between sessions",
        default=True,
    )

    max_context_memory_size: IntProperty(
        name="Max Context Memory (KB)",
        description="Maximum size of persistent context memory in kilobytes",
        default=100,
        min=10,
        max=1000,
    )

    # MCP Settings
    enable_mcp: BoolProperty(
        name="Enable MCP Integration",
        description="Enable Model Context Protocol server integration",
        default=True,
    )

    mcp_server_configs: StringProperty(
        name="MCP Server Configurations",
        description="JSON configuration for MCP servers",
        default="{}",
    )

    mcp_auto_connect: BoolProperty(
        name="Auto-connect MCP Servers",
        description="Automatically connect to configured MCP servers on startup",
        default=False,
    )

    mcp_tool_confirmation: BoolProperty(
        name="Confirm MCP Tool Calls",
        description="Show confirmation dialog before executing MCP tools",
        default=True,
    )
    
    def draw(self, context):
        """Draw the preferences UI"""
        layout = self.layout
        
        # AI Provider Configuration Section
        box = layout.box()
        box.label(text="AI Provider Configuration", icon='NETWORK_DRIVE')

        col = box.column()
        col.prop(self, "provider_type")

        # OpenAI Settings
        if self.provider_type == 'openai':
            col.separator()
            col.label(text="OpenAI Settings:")
            col.prop(self, "api_key")

            if not self.api_key:
                col.label(text="⚠️ API key required for S647 to function", icon='ERROR')
                col.label(text="Get your API key from: https://platform.openai.com/api-keys")

            col.prop(self, "api_model")

        # Custom Provider Settings
        elif self.provider_type == 'custom':
            col.separator()
            col.label(text="Custom Provider Settings:")
            col.prop(self, "custom_base_url")
            col.prop(self, "custom_model")
            col.prop(self, "custom_api_key")

            if not self.custom_base_url or not self.custom_model or not self.custom_api_key:
                col.label(text="⚠️ All custom provider fields are required", icon='ERROR')

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
        test_box.label(text="Connection Test:", icon='NETWORK_DRIVE')

        test_row = test_box.row(align=True)
        test_row.operator("s647.test_ai_config", text="Test Configuration", icon='PLAY')
        test_row.operator("s647.reinitialize_ai", text="Reinitialize", icon='FILE_REFRESH')

        # Show current status if available
        try:
            from . import ai_engine
            status = ai_engine.get_api_status()
            if status.get('initialized'):
                status_box = test_box.box()
                status_box.label(text="✓ AI Engine Ready", icon='CHECKMARK')
                if 'provider_status' in status:
                    status_box.label(text=f"Status: {status['provider_status']}")
                if 'provider_message' in status:
                    status_box.label(text=f"Message: {status['provider_message']}")
            else:
                status_box = test_box.box()
                status_box.label(text="⚠️ AI Engine Not Ready", icon='ERROR')
        except Exception:
            pass
        
        # Safety Settings Section
        box = layout.box()
        box.label(text="Safety & Execution Settings", icon='LOCKED')
        
        col = box.column()
        col.prop(self, "enable_code_execution")
        
        if self.enable_code_execution:
            col.prop(self, "confirm_before_execution")
            col.prop(self, "sandbox_mode")
            
            if not self.confirm_before_execution:
                col.label(text="⚠️ Automatic code execution can be dangerous!", icon='ERROR')
        
        # UI Settings Section
        box = layout.box()
        box.label(text="Interface Settings", icon='TOOL_SETTINGS')
        
        col = box.column()
        col.prop(self, "show_advanced_options")
        col.prop(self, "auto_save_conversations")
        col.prop(self, "conversation_history_limit")

        # Mode Settings Section
        box = layout.box()
        box.label(text="Interaction Modes", icon='SETTINGS')

        col = box.column()
        col.prop(self, "default_interaction_mode")
        col.prop(self, "enable_smart_mode_switching")
        col.prop(self, "enable_context_persistence")
        col.prop(self, "max_context_memory_size")

        # MCP Settings Section
        box = layout.box()
        box.label(text="Model Context Protocol (MCP)", icon='NETWORK_DRIVE')

        col = box.column()
        col.prop(self, "enable_mcp")

        if self.enable_mcp:
            col.prop(self, "mcp_auto_connect")
            col.prop(self, "mcp_tool_confirmation")

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

        col.label(text=f"Code Execution: {'Enabled' if self.enable_code_execution else 'Disabled'}")

def get_preferences():
    """Get the addon preferences"""
    return bpy.context.preferences.addons[__package__].preferences

def register():
    """Register preferences"""
    bpy.utils.register_class(S647AddonPreferences)

def unregister():
    """Unregister preferences"""
    bpy.utils.unregister_class(S647AddonPreferences)
