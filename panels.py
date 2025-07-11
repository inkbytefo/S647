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
S647 Panels Module
==================

Defines the user interface panels for the S647 addon in Blender's sidebar.
"""

import bpy
from bpy.types import Panel

from .preferences import get_preferences

class S647_PT_MainPanel(Panel):
    """Main S647 panel with chat interface and essential controls"""
    bl_label = "S647 AI Assistant"
    bl_idname = "S647_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_context = "objectmode"

    def _get_ui_text(self, key: str, mode: str = None, **kwargs) -> str:
        """Get UI text using centralized prompt system with fallback"""
        try:
            from .prompts import PromptManager
            return PromptManager.get_ui_text(key, mode=mode, **kwargs)
        except (ImportError, Exception):
            # Comprehensive fallback texts
            fallback_texts = {
                'interaction_mode': "Interaction Mode",
                'send': {'chat': "💬 Chat", 'act': "⚡ Act"},
                'mode_description_chat': "💬 Educational Focus - Learn and explore Blender",
                'mode_description_act': "⚡ Action Focus - Get things done quickly",
                'conversation': "💬 Conversation",
                'welcome_main': "👋 Welcome to S647!",
                'welcome_chat': "💬 Ask me anything about Blender - I'm here to help you learn!",
                'welcome_act': "⚡ Tell me what you want to do and I'll help you accomplish it!",
                'quick_start': "Try: 'Create a cube' or 'How do I add materials?'",
                'message_header': "✍️ Message",
                'placeholder_chat': "💬 Ask me anything about Blender...",
                'placeholder_act': "⚡ Tell me what to do in Blender...",
                'character_count': "📝 {count} characters",
                # Removed unused quick action text keys
                'settings': "⚙️ Settings",
                'clear': "🗑️ Clear",
                'save': "💾 Save",
                'message_count': "💬 {count} messages in conversation"
            }

            if mode and key in fallback_texts and isinstance(fallback_texts[key], dict):
                return fallback_texts[key].get(mode, f"[{key}]")
            return fallback_texts.get(key, f"[{key}]")

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647
        prefs = get_preferences()

        # Check AI configuration using AI Config Manager
        ai_ready = False
        api_key_missing = True
        config_error_message = ""

        try:
            from .ai_config_manager import get_ai_config_manager
            config_manager = get_ai_config_manager()

            # Initialize from preferences if not already done
            if not config_manager.is_ready():
                success, message = config_manager.initialize_from_preferences()
                if not success:
                    config_error_message = message

            # Check if AI is ready
            ai_ready = config_manager.is_ready()
            api_key_missing = not ai_ready

        except Exception as e:
            # Fallback to old method if AI config manager fails
            api_key_missing = not prefs.api_key or prefs.api_key.strip() == ""
            ai_ready = not api_key_missing
            config_error_message = f"Config manager error: {str(e)}"

        # Header with modern mode pills
        self.draw_mode_pills(layout, props)

        # Status indicator (compact)
        self.draw_status_indicator(layout, props)

        # Main chat stream
        self.draw_chat_stream(layout, props, context)

        # Inline context controls (simplified)
        self.draw_inline_context_controls(layout, props)

        # Smart input section
        self.draw_smart_input(layout, props, api_key_missing, ai_ready, config_error_message)

        # Utility actions bar
        self.draw_utility_actions(layout, props)

    def draw_mode_pills(self, layout, props):
        """Draw modern pill-style mode selector with enhanced styling"""
        # Mode pills container with modern styling
        pills_container = layout.box()
        pills_container.use_property_split = False

        # Add subtle header
        header_row = pills_container.row()
        header_row.scale_y = 0.7
        header_row.label(text=self._get_ui_text("interaction_mode"), icon='SETTINGS')

        pills_row = pills_container.row(align=True)
        pills_row.scale_y = 1.1  # Slightly larger for better touch targets

        # Chat mode pill with enhanced styling
        chat_op = pills_row.operator("s647.switch_mode",
                                   text=self._get_ui_text("send", mode="chat"),
                                   depress=(props.interaction_mode == 'chat'))
        chat_op.mode = 'chat'
        if props.interaction_mode == 'chat':
            # Add visual feedback for active mode
            pills_row.enabled = True

        # Act mode pill
        act_op = pills_row.operator("s647.switch_mode",
                                  text=self._get_ui_text("send", mode="act"),
                                  depress=(props.interaction_mode == 'act'))
        act_op.mode = 'act'

        # Mode description with smooth transition effect
        desc_row = pills_container.row()
        desc_row.scale_y = 0.8

        current_desc = self._get_ui_text(f"mode_description_{props.interaction_mode}")
        if current_desc:
            desc_row.label(text=current_desc)

    def draw_status_indicator(self, layout, props):
        """Draw compact status indicator"""
        if props.ai_status != 'idle':
            status_row = layout.row()
            status_row.scale_y = 0.8

            if props.ai_status == 'thinking':
                status_row.label(text="🤖 S647 is thinking...", icon='TIME')
            elif props.ai_status == 'responding':
                status_row.label(text="🤖 S647 is responding...", icon='EXPORT')
            elif props.ai_status == 'error':
                status_row.label(text="❌ Error occurred", icon='ERROR')
                if props.ai_status_message != "Ready":
                    status_row = layout.row()
                    status_row.scale_y = 0.7
                    status_row.label(text=props.ai_status_message)

    def draw_chat_stream(self, layout, props, context):
        """Draw unified chat stream with messages and modern styling"""
        # Chat container with enhanced styling
        chat_box = layout.box()
        chat_box.use_property_split = False

        # Chat header
        header_row = chat_box.row()
        header_row.scale_y = 0.8
        header_row.label(text=self._get_ui_text("conversation"), icon='OUTLINER')

        if not props.conversation_history:
            # Enhanced welcome message with better visual hierarchy
            welcome_container = chat_box.box()
            welcome_container.use_property_split = False

            # Main welcome
            welcome_row = welcome_container.row()
            welcome_row.scale_y = 1.2
            welcome_row.label(text=self._get_ui_text("main"), icon='BLENDER')

            # Mode-specific tips with better formatting
            tip_row = welcome_container.row()
            tip_row.scale_y = 0.9
            tip_text = self._get_ui_text(props.interaction_mode)
            tip_row.label(text=tip_text)

            # Quick start suggestions
            suggestions_row = welcome_container.row()
            suggestions_row.scale_y = 0.8
            suggestions_row.label(text=self._get_ui_text("quick_start"))
            return

        # Message stream with improved spacing
        messages_container = chat_box.box()
        messages_container.use_property_split = False

        # Auto-scroll behavior: Show more recent messages as conversation grows
        total_messages = len(props.conversation_history)

        # Dynamic message display count based on conversation length
        if total_messages <= 5:
            # Show all messages for short conversations
            recent_messages = list(props.conversation_history)
            show_more_indicator = False
        elif total_messages <= 15:
            # Show last 8 messages for medium conversations
            recent_messages = list(props.conversation_history)[-8:]
            show_more_indicator = total_messages > 8
        else:
            # Show last 10 messages for long conversations (better scroll feel)
            recent_messages = list(props.conversation_history)[-10:]
            show_more_indicator = True

        for i, msg in enumerate(recent_messages):
            # Calculate actual message index in full conversation
            actual_index = total_messages - len(recent_messages) + i
            is_latest = i == len(recent_messages) - 1
            is_recent = i >= len(recent_messages) - 3  # Last 3 messages are "recent"

            self.draw_message_bubble(messages_container, msg, props, is_latest, actual_index, is_recent)

            # Add subtle separator between messages
            if i < len(recent_messages) - 1:
                sep_row = messages_container.row()
                sep_row.scale_y = 0.3
                sep_row.separator()

        # Show more indicator with better styling and scroll info
        if show_more_indicator:
            more_container = chat_box.box()
            more_row = more_container.row()
            more_row.scale_y = 0.8
            hidden_count = total_messages - len(recent_messages)
            more_row.label(text=f"↑ {hidden_count} earlier messages", icon='TRIA_UP')
            more_row.operator("s647.show_full_history", text="Show All", icon='TRIA_DOWN')

    def draw_message_bubble(self, chat_box, msg, props, is_latest, message_index, is_recent=True):
        """Draw individual message bubble with modern chat-like styling and auto-scroll effect"""
        # Create message container with enhanced styling
        msg_container = chat_box.box()
        msg_container.use_property_split = False

        # Apply scaling for auto-scroll effect - older messages get smaller
        if not is_recent:
            msg_container.scale_y = 0.7  # Make older messages more compact
        elif is_latest:
            msg_container.scale_y = 1.1  # Emphasize the latest message
        else:
            msg_container.scale_y = 0.9  # Recent but not latest

        # Message header with improved layout
        header_row = msg_container.row()
        header_row.scale_y = 0.9

        if msg.role == 'user':
            # User message with right-aligned feel
            user_text = "💬 You"
            if is_latest:
                user_text += " ✨"  # Latest message indicator
            header_row.label(text=user_text, icon='USER')
            header_row.separator()  # Push timestamp to right
            if msg.timestamp:
                time_label = header_row.row()
                time_label.scale_x = 0.6
                time_label.alignment = 'RIGHT'
                time_label.label(text=msg.timestamp)
        else:
            # AI message with left-aligned feel
            ai_text = "🤖 S647"
            if is_latest:
                ai_text += " ✨"  # Latest message indicator
            header_row.label(text=ai_text, icon='BLENDER')
            header_row.separator()
            if msg.timestamp:
                time_label = header_row.row()
                time_label.scale_x = 0.6
                time_label.alignment = 'RIGHT'
                time_label.label(text=msg.timestamp)

        # Message content with better typography
        content_container = msg_container.box()
        content_container.use_property_split = False

        content_lines = msg.content.split('\n')
        displayed_lines = 0

        # Dynamic max lines based on message age for auto-scroll effect
        if not is_recent:
            max_lines = 3  # Compact older messages
        elif is_latest:
            max_lines = 15  # Show more of the latest message
        else:
            max_lines = 8  # Normal display for recent messages

        for line in content_lines:
            if displayed_lines >= max_lines:
                break
            if line.strip():
                content_row = content_container.row()
                content_row.scale_y = 0.95
                # Split long lines for better readability in chat
                if len(line) > 80:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) > 80 and current_line:
                            content_row.label(text=f"  {current_line.strip()}")
                            displayed_lines += 1
                            if displayed_lines >= max_lines:
                                break
                            content_row = content_container.row()
                            content_row.scale_y = 0.95
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    if current_line.strip() and displayed_lines < max_lines:
                        content_row.label(text=f"  {current_line.strip()}")
                        displayed_lines += 1
                else:
                    # Add subtle indentation for better readability
                    content_row.label(text=f"  {line}")
                    displayed_lines += 1

        # Truncation indicator with expand option (auto-scroll friendly)
        if len(content_lines) > max_lines:
            more_content = content_container.row()
            more_content.scale_y = 0.7
            if not is_recent:
                # For older messages, just show truncation indicator
                more_content.label(text=f"... ({len(content_lines) - max_lines} more lines)", icon='TRIA_DOWN')
            else:
                # For recent messages, allow expansion
                more_content.label(text=f"... ({len(content_lines) - max_lines} more lines)")
                expand_op = more_content.operator("s647.expand_message", text="Show More", icon='TRIA_DOWN')
                expand_op.message_index = message_index

        # Enhanced action buttons for AI messages with code
        if msg.role == 'assistant' and msg.has_code:
            # Actions container with modern styling
            actions_container = msg_container.box()
            actions_container.use_property_split = False

            # Action buttons with improved layout
            actions_row = actions_container.row(align=True)
            actions_row.scale_y = 1.0

            # Mode-specific action buttons
            if props.interaction_mode == 'chat':
                # Chat mode: Show all options for learning
                apply_op = actions_row.operator("s647.apply_message_code", text="▶ Apply", icon='PLAY')
                apply_op.message_index = len(props.conversation_history) - 1

                explain_op = actions_row.operator("s647.explain_code", text="❓ Explain", icon='QUESTION')
                explain_op.message_index = len(props.conversation_history) - 1

                modify_op = actions_row.operator("s647.modify_code", text="✏️ Modify", icon='GREASEPENCIL')
                modify_op.message_index = len(props.conversation_history) - 1
            else:
                # Act mode: Minimal buttons since code auto-executes
                if not msg.code_executed:
                    # Only show manual apply if auto-execution failed
                    apply_op = actions_row.operator("s647.apply_message_code", text="⚡ Execute", icon='PLAY')
                    apply_op.message_index = len(props.conversation_history) - 1

                # Always show modify option for tweaking
                modify_op = actions_row.operator("s647.modify_code", text="✏️ Modify", icon='GREASEPENCIL')
                modify_op.message_index = len(props.conversation_history) - 1

            # Execution status with enhanced feedback
            if msg.code_executed:
                status_row = actions_container.row()
                status_row.scale_y = 0.8
                if props.interaction_mode == 'act':
                    status_row.label(text="✅ Auto-executed in Act mode", icon='CHECKMARK')
                else:
                    status_row.label(text="✅ Code executed successfully", icon='CHECKMARK')
            else:
                # Show code preview indicator with mode-specific text
                preview_row = actions_container.row()
                preview_row.scale_y = 0.7
                if props.interaction_mode == 'act':
                    preview_row.label(text="⚡ Ready for auto-execution", icon='SCRIPT')
                else:
                    preview_row.label(text="📝 Contains executable code", icon='SCRIPT')

    def draw_smart_input(self, layout, props, api_key_missing, ai_ready, config_error_message=""):
        """Draw smart input section with modern chat interface styling"""
        # Input container with enhanced styling
        input_container = layout.box()
        input_container.use_property_split = False

        # Input header
        header_row = input_container.row()
        header_row.scale_y = 0.8
        header_row.label(text=self._get_ui_text("message"), icon='GREASEPENCIL')

        # Dynamic placeholder based on mode with enhanced text
        placeholder = self._get_ui_text("input", mode=props.interaction_mode)

        # Main input field with improved styling
        input_field_container = input_container.box()
        input_field_container.use_property_split = False

        input_row = input_field_container.row()
        input_row.scale_y = 1.2  # Larger input field for better UX
        input_row.prop(props, "current_prompt", text="", placeholder=placeholder)

        # Disable input if API key missing or AI not ready
        if api_key_missing or not ai_ready:
            input_row.enabled = False

            # Show helpful error message with specific details
            error_row = input_field_container.row()
            error_row.scale_y = 0.8
            if config_error_message:
                # Show specific error from AI config manager
                error_row.label(text=f"⚠️ {config_error_message}", icon='ERROR')
            elif api_key_missing:
                error_row.label(text="⚠️ Configure AI provider in preferences", icon='ERROR')
            else:
                error_row.label(text="⚠️ AI engine not ready", icon='ERROR')

        # Enhanced send button row with better layout
        send_container = input_container.box()
        send_container.use_property_split = False

        send_row = send_container.row(align=True)
        send_row.scale_y = 1.1

        # Send button with mode-specific text and enhanced icons
        send_texts = {
            'chat': "💬 Send",
            'act': "⚡ Execute",
            'hybrid': "🧠 Process"
        }
        send_icons = {
            'chat': 'QUESTION',
            'act': 'PLAY',
            'hybrid': 'COMMUNITY'
        }

        send_text = send_texts.get(props.interaction_mode, "Send")
        send_icon = send_icons.get(props.interaction_mode, 'QUESTION')

        # Primary send button
        send_op = send_row.operator("s647.send_prompt", text=send_text, icon=send_icon)

        # Character count indicator (if prompt is long)
        if len(props.current_prompt) > 100:
            char_row = send_container.row()
            char_row.scale_y = 0.7
            char_count = len(props.current_prompt)
            char_row.label(text=self._get_ui_text("character_count", count=char_count))

        # Enable/disable logic with visual feedback
        is_enabled = (not api_key_missing and ai_ready and
                     bool(props.current_prompt.strip()) and props.ai_status == 'idle')
        send_row.enabled = is_enabled

        if not is_enabled and props.current_prompt.strip():
            status_row = send_container.row()
            status_row.scale_y = 0.7
            if props.ai_status != 'idle':
                status_row.label(text="⏳ AI is busy...", icon='TIME')
            else:
                status_row.label(text="⚠️ Check configuration", icon='ERROR')

    def draw_utility_actions(self, layout, props):
        """Draw utility actions bar with save, settings, and clear"""
        # Utility actions container
        utility_container = layout.box()
        utility_container.use_property_split = False

        # Actions row
        actions_row = utility_container.row(align=True)
        actions_row.scale_y = 0.9

        # Save conversation (markdown format)
        actions_row.operator("s647.save_conversation",
                           text=self._get_ui_text("save"),
                           icon='FILE_TICK')

        # Settings
        actions_row.operator("s647.open_settings",
                           text=self._get_ui_text("settings"),
                           icon='PREFERENCES')

        # Clear conversation
        actions_row.operator("s647.clear_conversation",
                           text=self._get_ui_text("clear"),
                           icon='TRASH')

        # Show conversation count if there are messages
        if props.conversation_history:
            count_row = utility_container.row()
            count_row.scale_y = 0.6
            msg_count = len(props.conversation_history)
            count_row.label(text=self._get_ui_text("message_count", count=msg_count))

    def draw_inline_context_controls(self, layout, props):
        """Draw simplified inline context controls"""
        if not props.show_context_panel:
            return

        # Compact context controls
        context_container = layout.box()
        context_container.use_property_split = False

        # Context header (collapsible style)
        header_row = context_container.row()
        header_row.scale_y = 0.8
        header_row.label(text="Context", icon='SCENE')

        # Quick context mode selector
        mode_row = context_container.row()
        mode_row.scale_y = 0.9
        mode_row.prop(props, "context_mode", text="")

        # Thread info (compact)
        if props.current_thread_id:
            thread_row = context_container.row()
            thread_row.scale_y = 0.7
            thread_row.label(text=f"Thread: {props.thread_title or props.current_thread_id[:8]}")
            thread_row.operator("s647.create_thread", text="", icon='ADD')


# Legacy panels removed - now using streamlined interface

class S647_PT_ToolsPanel(Panel):
    """Combined tools panel for MCP integration and code execution"""
    bl_label = "Tools & Execution"
    bl_idname = "S647_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647
        prefs = get_preferences()

        # Code Execution Section
        if props.pending_code or props.code_execution_result:
            self.draw_code_execution_section(layout, props, prefs)
            layout.separator()

        # MCP Integration Section
        if prefs.enable_mcp:
            self.draw_mcp_section(layout, prefs)
        else:
            # MCP disabled indicator
            mcp_box = layout.box()
            mcp_box.label(text="MCP Integration", icon='NETWORK_DRIVE')
            mcp_box.label(text="Disabled in preferences", icon='INFO')

    def draw_code_execution_section(self, layout, props, prefs):
        """Draw code execution controls"""
        code_box = layout.box()
        code_box.label(text="Code Execution", icon='CONSOLE')

        # Pending code preview
        if props.pending_code:
            preview_box = code_box.box()
            preview_box.label(text="Pending Code:", icon='SCRIPT')

            # Show first few lines of code
            code_lines = props.pending_code.split('\n')
            for i, line in enumerate(code_lines[:5]):
                if line.strip():
                    preview_box.label(text=f"  {line}")

            if len(code_lines) > 5:
                preview_box.label(text=f"... ({len(code_lines) - 5} more lines)")

            # Execution controls
            controls_row = code_box.row(align=True)
            controls_row.operator("s647.execute_code", text="Execute", icon='PLAY')
            controls_row.operator("s647.copy_code", text="Copy", icon='COPYDOWN')

        # Execution result
        if props.code_execution_result:
            result_box = code_box.box()
            result_box.label(text="Last Result:", icon='CHECKMARK')

            result_lines = props.code_execution_result.split('\n')
            for line in result_lines[:3]:  # Show first 3 lines
                if line.strip():
                    result_box.label(text=f"  {line}")

            if len(result_lines) > 3:
                result_box.label(text=f"... ({len(result_lines) - 3} more lines)")

    def draw_mcp_section(self, layout, prefs):
        """Draw simplified MCP integration controls"""
        try:
            from . import mcp_client

            if not mcp_client.is_mcp_available():
                mcp_box = layout.box()
                mcp_box.label(text="MCP Integration", icon='NETWORK_DRIVE')
                mcp_box.label(text="MCP SDK not available", icon='ERROR')
                return

            manager = mcp_client.get_mcp_manager()
            if not manager:
                mcp_box = layout.box()
                mcp_box.label(text="MCP Integration", icon='NETWORK_DRIVE')
                mcp_box.label(text="Manager not initialized", icon='ERROR')
                return

            mcp_box = layout.box()
            mcp_box.label(text="MCP Integration", icon='NETWORK_DRIVE')

            # Server status (simplified)
            servers = manager.get_all_servers()
            if servers:
                status_row = mcp_box.row()
                connected_count = sum(1 for name in servers.keys()
                                    if manager.get_server_status(name).value == "connected")
                status_row.label(text=f"Servers: {connected_count}/{len(servers)} connected")

                # Quick management
                mgmt_row = mcp_box.row(align=True)
                mgmt_row.operator("s647.manage_mcp_servers", text="Manage", icon='SETTINGS')
                mgmt_row.operator("s647.load_mcp_config_file", text="Reload", icon='FILE_REFRESH')
            else:
                mcp_box.label(text="No servers configured")
                mcp_box.operator("s647.manage_mcp_servers", text="Add Servers", icon='ADD')

            # Tools summary
            tools = manager.get_all_tools()
            if tools:
                tools_row = mcp_box.row()
                tools_row.scale_y = 0.8
                tools_row.label(text=f"Available tools: {len(tools)}")

        except Exception as e:
            mcp_box = layout.box()
            mcp_box.label(text="MCP Integration", icon='NETWORK_DRIVE')
            mcp_box.label(text=f"Error: {str(e)}", icon='ERROR')


# Legacy Context Panel removed - functionality integrated into main panel

# Legacy Smart Suggestions Panel removed - functionality can be integrated into main panel if needed

class S647_PT_AdvancedPanel(Panel):
    """Advanced options panel - streamlined for power users"""
    bl_label = "Advanced Options"
    bl_idname = "S647_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = get_preferences()
        return prefs.show_advanced_options

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647
        prefs = get_preferences()

        # Context settings
        context_box = layout.box()
        context_box.label(text="Context Settings:", icon='SCENE')
        context_box.prop(props, "context_mode")

        if props.context_mode in ['detailed', 'full']:
            context_box.prop(props, "include_object_data")
            context_box.prop(props, "include_material_data")
            context_box.prop(props, "include_modifier_data")

        # AI Model settings - Moved to Preferences
        # Use preferences to configure AI model, temperature, and max_tokens
        ai_info_box = layout.box()
        ai_info_box.label(text="AI Configuration:", icon='INFO')

        # Show current model info (read-only)
        if prefs.provider_type == 'openai':
            ai_info_box.label(text=f"Model: {prefs.api_model}")
        elif prefs.provider_type == 'custom':
            ai_info_box.label(text=f"Model: {prefs.custom_model}")

        ai_info_box.label(text=f"Temperature: {prefs.temperature:.2f}")
        ai_info_box.label(text=f"Max Tokens: {prefs.max_tokens}")

        # Link to preferences for changes
        pref_row = ai_info_box.row()
        pref_row.operator("preferences.addon_show", text="Configure in Preferences", icon='TOOL_SETTINGS').module = __package__



        # System Status (simplified)
        status_box = layout.box()
        status_box.label(text="System Status:", icon='INFO')

        try:
            from . import ai_engine
            api_status = ai_engine.get_api_status()

            # Simple status display
            status_row = status_box.row()
            if api_status['initialized']:
                status_row.label(text="✓ AI Engine Ready", icon='CHECKMARK')
            else:
                status_row.label(text="✗ AI Engine Not Ready", icon='X')
                # Only show reinitialize if there's a problem
                reinit_row = status_box.row()
                reinit_row.operator("s647.initialize_ai", text="Reinitialize", icon='FILE_REFRESH')

        except ImportError:
            status_box.label(text="✗ AI Engine Error", icon='ERROR')

        # Usage Statistics (compact)
        if props.total_requests > 0:
            stats_box = layout.box()
            stats_box.label(text="Session Stats:", icon='GRAPH')

            # Compact stats display
            stats_row = stats_box.row()
            stats_row.label(text=f"Requests: {props.total_requests}")

            if props.total_requests > 0:
                success_rate = (props.successful_requests / props.total_requests) * 100
                stats_row.label(text=f"Success: {success_rate:.0f}%")

            if props.code_executions > 0:
                exec_row = stats_box.row()
                exec_row.label(text=f"Code Executions: {props.code_executions}")

# Legacy Code Execution Panel removed - functionality moved to Tools panel


# Legacy MCP Panel removed - functionality moved to Tools panel


# List of all panel classes for registration - Streamlined hierarchy
classes = [
    S647_PT_MainPanel,             # Main chat panel with essential controls
    S647_PT_ToolsPanel,            # Combined tools: MCP + Code execution
    S647_PT_AdvancedPanel,         # Advanced options (collapsed by default)
]

def register():
    """Register all panels"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all panels"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
