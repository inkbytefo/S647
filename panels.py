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
from . import utils

class S647_PT_UnifiedChatPanel(Panel):
    """Modern unified chat interface inspired by Augment Code & Cline"""
    bl_label = "S647 AI Assistant"
    bl_idname = "S647_PT_unified_chat_panel"
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
                'quick_actions': "🚀 Quick Actions",
                'suggestions': "🎯 Suggestions",
                'context': "📎 Context",
                'voice': "🎤 Voice",
                'voice_soon': "🎤 Voice (Soon)",
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

        # Smart input section
        self.draw_smart_input(layout, props, api_key_missing, ai_ready, config_error_message)

        # Quick actions footer
        self.draw_quick_actions(layout, props)

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

            # Apply code button (primary action)
            apply_op = actions_row.operator("s647.apply_message_code", text="▶ Apply", icon='PLAY')
            apply_op.message_index = len(props.conversation_history) - 1

            # Secondary actions
            explain_op = actions_row.operator("s647.explain_code", text="❓ Explain", icon='QUESTION')
            explain_op.message_index = len(props.conversation_history) - 1

            modify_op = actions_row.operator("s647.modify_code", text="✏️ Modify", icon='GREASEPENCIL')
            modify_op.message_index = len(props.conversation_history) - 1

            # Execution status with enhanced feedback
            if msg.code_executed:
                status_row = actions_container.row()
                status_row.scale_y = 0.8
                status_row.label(text="✅ Code executed successfully", icon='CHECKMARK')
            else:
                # Show code preview indicator
                preview_row = actions_container.row()
                preview_row.scale_y = 0.7
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

    def draw_quick_actions(self, layout, props):
        """Draw modern quick actions footer with enhanced UX"""
        # Quick actions container with modern styling
        actions_container = layout.box()
        actions_container.use_property_split = False

        # Actions header
        header_row = actions_container.row()
        header_row.scale_y = 0.7
        header_row.label(text=self._get_ui_text("quick_actions"), icon='TOOL_SETTINGS')

        # Primary actions row
        primary_row = actions_container.row(align=True)
        primary_row.scale_y = 0.9

        # Smart suggestions with enhanced styling
        primary_row.operator("s647.show_suggestions",
                           text=self._get_ui_text("suggestions"),
                           icon='HELP')

        # Context manager
        primary_row.operator("s647.manage_context",
                           text=self._get_ui_text("context"),
                           icon='OUTLINER')

        # Secondary actions row
        secondary_row = actions_container.row(align=True)
        secondary_row.scale_y = 0.8

        # Voice input (if available) with better integration
        if hasattr(props, 'voice_input_available') and props.voice_input_available:
            secondary_row.operator("s647.voice_input",
                                 text=self._get_ui_text("voice"),
                                 icon='SOUND')
        else:
            # Placeholder for voice (coming soon)
            voice_placeholder = secondary_row.row()
            voice_placeholder.enabled = False
            voice_placeholder.operator("s647.voice_input",
                                     text=self._get_ui_text("voice_soon"),
                                     icon='SOUND')

        # Settings with better icon
        secondary_row.operator("s647.open_settings",
                             text=self._get_ui_text("settings"),
                             icon='PREFERENCES')

        # Additional helpful actions
        help_row = actions_container.row(align=True)
        help_row.scale_y = 0.7

        # Clear conversation
        help_row.operator("s647.clear_conversation",
                        text=self._get_ui_text("clear"),
                        icon='TRASH')

        # Save conversation
        help_row.operator("s647.save_conversation",
                        text=self._get_ui_text("save"),
                        icon='FILE_TICK')

        # Show conversation count
        if props.conversation_history:
            count_row = actions_container.row()
            count_row.scale_y = 0.6
            msg_count = len(props.conversation_history)
            count_row.label(text=self._get_ui_text("message_count", count=msg_count))


# Legacy panels removed - now using unified chat interface

# Legacy Response and Conversation panels removed - functionality moved to unified chat

class S647_PT_ContextPanel(Panel):
    """Panel for context management and memory"""
    bl_label = "Context & Memory"
    bl_idname = "S647_PT_context_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_unified_chat_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.s647
        return props.show_context_panel

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647

        # Thread Management
        thread_box = layout.box()
        thread_box.label(text="Conversation Thread:", icon='OUTLINER')

        thread_row = thread_box.row()
        thread_row.prop(props, "current_thread_id", text="ID")
        thread_row.prop(props, "thread_title", text="Title")

        # Thread Actions
        thread_actions = thread_box.row(align=True)
        thread_actions.operator("s647.create_thread", text="New", icon='ADD')
        thread_actions.operator("s647.rename_thread", text="Rename", icon='GREASEPENCIL')

        # Show thread info
        thread_info = thread_box.column()
        thread_count = len(set(msg.thread_id for msg in props.conversation_history))
        current_thread_msgs = len([msg for msg in props.conversation_history if msg.thread_id == props.current_thread_id])
        thread_info.label(text=f"Total threads: {thread_count}")
        thread_info.label(text=f"Messages in current: {current_thread_msgs}")

        # Context Memory Status
        memory_box = layout.box()
        memory_box.label(text="Memory Status:", icon='MEMORY')

        if props.context_memory:
            memory_box.label(text="✓ Persistent context available")
        else:
            memory_box.label(text="○ No persistent context")

        if props.session_context:
            memory_box.label(text="✓ Session context active")
        else:
            memory_box.label(text="○ No session context")

        # Memory Management Actions
        actions_box = layout.box()
        actions_box.label(text="Memory Actions:", icon='TOOL_SETTINGS')

        actions_row1 = actions_box.row(align=True)
        actions_row1.operator("s647.save_context", text="Save Context", icon='FILE_TICK')
        actions_row1.operator("s647.load_context", text="Load Context", icon='FILE_FOLDER')

        actions_row2 = actions_box.row(align=True)
        actions_row2.operator("s647.clear_context", text="Clear Context", icon='TRASH')
        actions_row2.operator("s647.export_context", text="Export", icon='EXPORT')

class S647_PT_SmartSuggestionsPanel(Panel):
    """Panel for AI-generated smart suggestions"""
    bl_label = "Smart Suggestions"
    bl_idname = "S647_PT_smart_suggestions_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_unified_chat_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.s647
        return props.show_smart_suggestions

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647

        # Mode-specific suggestions
        suggestions_box = layout.box()
        suggestions_box.label(text=f"Suggestions for {props.interaction_mode.title()} Mode:", icon='HELP')

        # Generate suggestions based on current context
        suggestions = self.get_smart_suggestions(context)

        if suggestions:
            for suggestion in suggestions[:5]:  # Show max 5 suggestions
                suggestion_row = suggestions_box.row()
                suggestion_row.operator("s647.apply_suggestion", text=suggestion['text'], icon=suggestion['icon'])
                suggestion_row.operator_context = 'INVOKE_DEFAULT'
                # Store suggestion data in operator
                op = suggestion_row.operator("s647.apply_suggestion", text="", icon='PLAY')
                op.suggestion_text = suggestion['prompt']
        else:
            suggestions_box.label(text="No suggestions available", icon='INFO')

        # Suggestion controls
        controls_box = layout.box()
        controls_box.label(text="Suggestion Controls:", icon='TOOL_SETTINGS')

        controls_row = controls_box.row(align=True)
        controls_row.operator("s647.refresh_suggestions", text="Refresh", icon='FILE_REFRESH')
        controls_row.operator("s647.toggle_suggestions", text="Toggle", icon='HIDE_OFF')

    def get_smart_suggestions(self, context):
        """Generate smart suggestions based on current context"""
        props = context.scene.s647
        suggestions = []

        # Get current Blender context safely
        active_obj = getattr(context, 'active_object', None)
        selected_objs = getattr(context, 'selected_objects', [])
        mode = getattr(context, 'mode', 'UNKNOWN')

        if props.interaction_mode == 'chat':
            # Educational suggestions for Chat mode
            if active_obj:
                suggestions.append({
                    'text': f"Learn about {active_obj.type.lower()} objects",
                    'prompt': f"Explain {active_obj.type.lower()} objects in Blender and their properties",
                    'icon': 'QUESTION'
                })

            if mode == 'EDIT_MESH':
                suggestions.append({
                    'text': "Mesh editing techniques",
                    'prompt': "What are the best mesh editing techniques in Blender?",
                    'icon': 'QUESTION'
                })

            suggestions.append({
                'text': "Blender workflow tips",
                'prompt': "Give me some workflow tips for efficient Blender usage",
                'icon': 'QUESTION'
            })

        elif props.interaction_mode == 'act':
            # Action suggestions for Act mode
            if active_obj:
                suggestions.append({
                    'text': f"Add modifier to {active_obj.name}",
                    'prompt': f"Add a subdivision surface modifier to {active_obj.name}",
                    'icon': 'MODIFIER'
                })

                suggestions.append({
                    'text': f"Create material for {active_obj.name}",
                    'prompt': f"Create a basic material for {active_obj.name}",
                    'icon': 'MATERIAL'
                })

            if len(selected_objs) > 1:
                suggestions.append({
                    'text': f"Join {len(selected_objs)} objects",
                    'prompt': f"Join the {len(selected_objs)} selected objects",
                    'icon': 'OBJECT_DATAMODE'
                })

            suggestions.append({
                'text': "Create basic scene setup",
                'prompt': "Create a basic scene with lighting and camera",
                'icon': 'SCENE_DATA'
            })

        else:  # hybrid mode
            # Mixed suggestions for Hybrid mode
            if active_obj:
                suggestions.append({
                    'text': f"Improve {active_obj.name}",
                    'prompt': f"How can I improve {active_obj.name} and what should I do next?",
                    'icon': 'COMMUNITY'
                })

            suggestions.append({
                'text': "Optimize current scene",
                'prompt': "Analyze my current scene and suggest optimizations",
                'icon': 'COMMUNITY'
            })

        return suggestions

class S647_PT_AdvancedPanel(Panel):
    """Advanced options panel"""
    bl_label = "Advanced Options"
    bl_idname = "S647_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_unified_chat_panel"
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

        # Safety settings
        safety_box = layout.box()
        safety_box.label(text="Safety Settings:", icon='LOCKED')
        safety_box.prop(prefs, "enable_code_execution")

        if prefs.enable_code_execution:
            safety_box.prop(prefs, "confirm_before_execution")
            safety_box.prop(prefs, "sandbox_mode")

        # API Status and Testing
        api_box = layout.box()
        api_box.label(text="API Status:", icon='NETWORK_DRIVE')

        try:
            from . import ai_engine
            api_status = ai_engine.get_api_status()

            status_row = api_box.row()
            if api_status['initialized']:
                status_row.label(text="✓ Connected", icon='CHECKMARK')
            else:
                status_row.label(text="✗ Not Connected", icon='X')

            test_row = api_box.row(align=True)
            test_row.operator("s647.test_connection", text="Test Connection", icon='NETWORK_DRIVE')
            test_row.operator("s647.initialize_ai", text="Reinitialize", icon='FILE_REFRESH')

            debug_row = api_box.row()
            debug_row.operator("s647.debug_ai", text="Debug Info", icon='CONSOLE')

            test_row = api_box.row()
            test_row.operator("s647.test_ai_message", text="Test AI Message", icon='PLAY')

            # MCP Integration Test
            mcp_row = api_box.row()
            mcp_row.operator("s647.test_mcp_integration", text="Test MCP Integration", icon='PLUGIN')

        except ImportError:
            api_box.label(text="AI Engine Error", icon='ERROR')

        # Statistics
        stats_box = layout.box()
        stats_box.label(text="Statistics:", icon='INFO')
        stats_box.label(text=f"Total Requests: {props.total_requests}")
        stats_box.label(text=f"Successful: {props.successful_requests}")
        stats_box.label(text=f"Code Executions: {props.code_executions}")

        if props.total_requests > 0:
            success_rate = (props.successful_requests / props.total_requests) * 100
            stats_box.label(text=f"Success Rate: {success_rate:.1f}%")

class S647_PT_CodeExecutionPanel(Panel):
    """Panel for code execution preview and control"""
    bl_label = "Code Execution"
    bl_idname = "S647_PT_code_execution_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_unified_chat_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.s647
        return bool(props.pending_code or props.code_execution_result)

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647
        prefs = get_preferences()

        # Pending code section
        if props.pending_code:
            pending_box = layout.box()
            pending_box.label(text="Pending Code:", icon='SCRIPT')

            # Show code preview
            code_lines = props.pending_code.split('\n')
            for line in code_lines[:5]:  # Show first 5 lines
                if line.strip():
                    pending_box.label(text=line, icon='DOT')

            if len(code_lines) > 5:
                pending_box.label(text=f"... ({len(code_lines) - 5} more lines)")

            # Safety check
            is_safe, warnings = utils.is_safe_code(props.pending_code)
            if not is_safe:
                warning_box = pending_box.box()
                warning_box.label(text="⚠️ Safety Warnings:", icon='ERROR')
                for warning in warnings:
                    warning_box.label(text=f"• {warning}")

            # Execution controls
            exec_row = pending_box.row(align=True)
            if prefs.enable_code_execution:
                exec_row.operator("s647.execute_code", text="Execute", icon='PLAY')
            else:
                exec_row.label(text="Code execution disabled")

            # Analysis and copy controls
            analysis_row = pending_box.row(align=True)
            analysis_row.operator("s647.analyze_code", text="Analyze", icon='VIEWZOOM').code = props.pending_code
            analysis_row.operator("s647.copy_code", text="Copy", icon='COPYDOWN').code = props.pending_code

        # Execution result section
        if props.code_execution_result:
            result_box = layout.box()
            result_box.label(text="Last Execution Result:", icon='CONSOLE')

            result_lines = props.code_execution_result.split('\n')
            for line in result_lines[:10]:  # Show first 10 lines
                if line.strip():
                    result_box.label(text=line)

            if len(result_lines) > 10:
                result_box.label(text=f"... ({len(result_lines) - 10} more lines)")


class S647_PT_MCPPanel(Panel):
    """Panel for MCP server management and status"""
    bl_label = "MCP Integration"
    bl_idname = "S647_PT_mcp_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "S647"
    bl_parent_id = "S647_PT_unified_chat_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences()

        if not prefs.enable_mcp:
            layout.label(text="MCP integration disabled", icon='INFO')
            layout.operator("screen.userpref_show", text="Enable in Preferences", icon='TOOL_SETTINGS')
            return

        try:
            from . import mcp_client

            if not mcp_client.is_mcp_available():
                layout.label(text="MCP SDK not available", icon='ERROR')
                layout.label(text="Install with: pip install mcp")
                return

            manager = mcp_client.get_mcp_manager()
            if not manager:
                layout.label(text="MCP Manager not initialized", icon='ERROR')
                return

            # Server status section
            box = layout.box()
            box.label(text="Server Status:", icon='NETWORK_DRIVE')

            servers = manager.get_all_servers()
            if not servers:
                box.label(text="No servers configured")
                box.operator("s647.manage_mcp_servers", text="Add Servers", icon='ADD')
            else:
                for name, config in servers.items():
                    row = box.row()
                    status = manager.get_server_status(name)

                    # Status indicator
                    if status.value == "connected":
                        row.label(text="", icon='CHECKMARK')
                        row.label(text=name)
                        row.operator("s647.disconnect_mcp_server", text="", icon='X').server_name = name
                    elif status.value == "connecting":
                        row.label(text="", icon='TIME')
                        row.label(text=f"{name} (connecting...)")
                    elif status.value == "error":
                        row.label(text="", icon='ERROR')
                        row.label(text=f"{name} (error)")
                        row.operator("s647.connect_mcp_server", text="", icon='CHECKMARK').server_name = name
                    else:
                        row.label(text="", icon='RADIOBUT_OFF')
                        row.label(text=name)
                        row.operator("s647.connect_mcp_server", text="", icon='CHECKMARK').server_name = name

            # Available tools section
            tools = manager.get_all_tools()
            if tools:
                layout.separator()
                box = layout.box()
                box.label(text=f"Available Tools ({len(tools)}):", icon='TOOL_SETTINGS')

                # Show first few tools
                for i, (tool_key, tool) in enumerate(tools.items()):
                    if i >= 5:  # Limit display
                        break
                    row = box.row()
                    row.label(text=f"• {tool.name}")
                    row.label(text=f"({tool.server_name})")

                if len(tools) > 5:
                    box.label(text=f"... and {len(tools) - 5} more")

            # Available resources section
            resources = manager.get_all_resources()
            if resources:
                layout.separator()
                box = layout.box()
                box.label(text=f"Available Resources ({len(resources)}):", icon='FILE_FOLDER')

                # Show first few resources
                for i, (resource_key, resource) in enumerate(resources.items()):
                    if i >= 3:  # Limit display
                        break
                    row = box.row()
                    row.label(text=f"• {resource.name}")
                    row.label(text=f"({resource.server_name})")

                if len(resources) > 3:
                    box.label(text=f"... and {len(resources) - 3} more")

            # Management buttons
            layout.separator()

            # Configuration management
            config_box = layout.box()
            config_box.label(text="Configuration:", icon='SETTINGS')

            config_row1 = config_box.row()
            config_row1.operator("s647.import_mcp_config", text="Import JSON", icon='IMPORT')
            config_row1.operator("s647.load_mcp_config_file", text="Load File", icon='FILE_REFRESH')

            config_row2 = config_box.row()
            config_row2.operator("s647.export_mcp_config", text="Export", icon='EXPORT')
            config_row2.operator("s647.manage_mcp_servers", text="Manage", icon='SETTINGS')

        except Exception as e:
            layout.label(text=f"MCP Error: {str(e)}", icon='ERROR')


# List of all panel classes for registration
classes = [
    S647_PT_UnifiedChatPanel,      # New unified chat panel (primary)
    S647_PT_ContextPanel,          # Context management
    S647_PT_SmartSuggestionsPanel, # Smart suggestions
    S647_PT_AdvancedPanel,         # Advanced options
    S647_PT_CodeExecutionPanel,    # Code execution
    S647_PT_MCPPanel,              # MCP integration
]

def register():
    """Register all panels"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all panels"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
