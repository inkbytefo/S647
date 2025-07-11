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
S647 Properties Module
======================

Defines runtime properties for the S647 addon including conversation state,
AI interaction data, and temporary variables.
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    IntProperty,
    CollectionProperty,
    PointerProperty,
)

class S647ConversationMessage(PropertyGroup):
    """Individual message in conversation history"""
    
    role: EnumProperty(
        name="Role",
        items=[
            ('user', 'User', 'Message from user'),
            ('assistant', 'Assistant', 'Message from AI assistant'),
            ('system', 'System', 'System message'),
        ],
        default='user',
    )
    
    content: StringProperty(
        name="Content",
        description="Message content",
        default="",
    )
    
    timestamp: StringProperty(
        name="Timestamp",
        description="When the message was created",
        default="",
    )
    
    has_code: BoolProperty(
        name="Has Code",
        description="Whether this message contains executable code",
        default=False,
    )
    
    code_executed: BoolProperty(
        name="Code Executed",
        description="Whether the code in this message was executed",
        default=False,
    )

    thread_id: StringProperty(
        name="Thread ID",
        description="ID of the conversation thread this message belongs to",
        default="main",
    )

    intent_type: EnumProperty(
        name="Intent Type",
        description="Detected intent of the message",
        items=[
            ('question', 'Question', 'User is asking a question'),
            ('command', 'Command', 'User is requesting an action'),
            ('feedback', 'Feedback', 'User is providing feedback'),
            ('clarification', 'Clarification', 'User is clarifying something'),
            ('unknown', 'Unknown', 'Intent could not be determined'),
        ],
        default='unknown',
    )

class S647Properties(PropertyGroup):
    """Main properties for S647 addon"""

    # Interaction Mode
    interaction_mode: EnumProperty(
        name="Interaction Mode",
        description="Choose how to interact with the AI assistant",
        items=[
            ('chat', 'Chat Mode', 'Conversational, educational, and exploratory interactions'),
            ('act', 'Act Mode', 'Task-focused, direct action and automation'),
            ('hybrid', 'Hybrid Mode', 'Intelligent mode switching based on context'),
        ],
        default='chat',
    )

    # Current conversation state
    current_prompt: StringProperty(
        name="Prompt",
        description="Current user input for the AI",
        default="",
        maxlen=2000,
    )
    
    last_response: StringProperty(
        name="Last Response",
        description="Last AI response",
        default="",
    )
    
    # Conversation history
    conversation_history: CollectionProperty(
        type=S647ConversationMessage,
        name="Conversation History",
    )

    # Conversation Threading
    current_thread_id: StringProperty(
        name="Current Thread ID",
        description="ID of the currently active conversation thread",
        default="main",
    )

    thread_title: StringProperty(
        name="Thread Title",
        description="Title of the current conversation thread",
        default="General Chat",
    )

    # Context Management
    context_memory: StringProperty(
        name="Context Memory",
        description="Persistent context information across sessions",
        default="",
    )

    session_context: StringProperty(
        name="Session Context",
        description="Context information for current session",
        default="",
    )

    user_preferences_learned: StringProperty(
        name="Learned Preferences",
        description="AI-learned user preferences and patterns",
        default="",
    )
    
    # AI Status
    ai_status: EnumProperty(
        name="AI Status",
        items=[
            ('idle', 'Idle', 'AI is ready for requests'),
            ('thinking', 'Thinking', 'AI is processing request'),
            ('responding', 'Responding', 'AI is generating response'),
            ('error', 'Error', 'AI encountered an error'),
        ],
        default='idle',
    )
    
    ai_status_message: StringProperty(
        name="Status Message",
        description="Detailed status information",
        default="Ready",
    )
    
    # Code execution state
    pending_code: StringProperty(
        name="Pending Code",
        description="Code waiting for execution approval",
        default="",
    )

    code_execution_result: StringProperty(
        name="Execution Result",
        description="Result of last code execution",
        default="",
    )

    # Task Management (for Act Mode)
    current_task: StringProperty(
        name="Current Task",
        description="Description of the current task being executed",
        default="",
    )

    task_progress: IntProperty(
        name="Task Progress",
        description="Progress of current task (0-100)",
        default=0,
        min=0,
        max=100,
    )

    task_steps: StringProperty(
        name="Task Steps",
        description="JSON string containing task breakdown steps",
        default="",
    )

    current_step: IntProperty(
        name="Current Step",
        description="Index of current step being executed",
        default=0,
    )
    
    # UI State (simplified for unified chat)
    show_code_preview: BoolProperty(
        name="Show Code Preview",
        description="Show code preview before execution",
        default=True,
    )

    auto_scroll_history: BoolProperty(
        name="Auto Scroll",
        description="Automatically scroll to latest message",
        default=True,
    )

    show_smart_suggestions: BoolProperty(
        name="Show Smart Suggestions",
        description="Show AI-generated smart suggestions",
        default=True,
    )
    
    # Panel visibility controls
    show_context_panel: BoolProperty(
        name="Show Context Panel",
        description="Show the context and memory management panel",
        default=True,
    )

    # Advanced options
    context_mode: EnumProperty(
        name="Context Mode",
        description="How much Blender context to include in AI requests",
        items=[
            ('minimal', 'Minimal', 'Basic scene information only'),
            ('standard', 'Standard', 'Selected objects and basic scene data'),
            ('detailed', 'Detailed', 'Comprehensive scene and object information'),
            ('full', 'Full', 'Complete scene dump (may be slow)'),
        ],
        default='standard',
    )
    
    include_object_data: BoolProperty(
        name="Include Object Data",
        description="Include detailed object data in AI context",
        default=True,
    )
    
    include_material_data: BoolProperty(
        name="Include Material Data",
        description="Include material information in AI context",
        default=False,
    )
    
    include_modifier_data: BoolProperty(
        name="Include Modifier Data",
        description="Include modifier information in AI context",
        default=False,
    )
    
    # Statistics
    total_requests: IntProperty(
        name="Total Requests",
        description="Total number of AI requests made",
        default=0,
    )
    
    successful_requests: IntProperty(
        name="Successful Requests",
        description="Number of successful AI requests",
        default=0,
    )
    
    code_executions: IntProperty(
        name="Code Executions",
        description="Number of code executions performed",
        default=0,
    )
    
    def add_message(self, role, content, has_code=False, thread_id=None, intent_type='unknown'):
        """Add a message to conversation history"""
        import datetime

        message = self.conversation_history.add()
        message.role = role
        message.content = content
        message.has_code = has_code
        message.timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message.thread_id = thread_id or self.current_thread_id
        message.intent_type = intent_type

        # Limit history size based on preferences
        try:
            from .preferences import get_preferences
            prefs = get_preferences()
            max_history = prefs.conversation_history_limit

            while len(self.conversation_history) > max_history:
                self.conversation_history.remove(0)
        except:
            # Fallback if preferences not available
            while len(self.conversation_history) > 50:
                self.conversation_history.remove(0)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.last_response = ""
        self.current_prompt = ""
    
    def get_conversation_context(self, thread_id=None):
        """Get conversation history as context for AI"""
        context = []
        target_thread = thread_id or self.current_thread_id

        for msg in self.conversation_history:
            if msg.thread_id == target_thread:
                context.append({
                    "role": msg.role,
                    "content": msg.content,
                    "intent": msg.intent_type
                })
        return context

    def switch_thread(self, thread_id, title=None):
        """Switch to a different conversation thread"""
        self.current_thread_id = thread_id
        if title:
            self.thread_title = title

    def get_mode_specific_prompt(self, user_prompt):
        """Get mode-specific system prompt based on interaction mode"""
        base_prompt = user_prompt

        if self.interaction_mode == 'chat':
            return f"[CHAT MODE] Please respond in a conversational, educational manner. Help the user understand concepts and explore ideas. User says: {base_prompt}"
        elif self.interaction_mode == 'act':
            return f"[ACT MODE] Please focus on direct action and task completion. Provide clear, executable steps. User requests: {base_prompt}"
        elif self.interaction_mode == 'hybrid':
            return f"[HYBRID MODE] Analyze the user's intent and respond appropriately - conversational for questions, action-oriented for tasks. User input: {base_prompt}"

        return base_prompt

    def update_task_progress(self, progress, current_step=None):
        """Update task progress for Act mode"""
        self.task_progress = max(0, min(100, progress))
        if current_step is not None:
            self.current_step = current_step

    def set_current_task(self, task_description, steps=None):
        """Set current task for Act mode"""
        self.current_task = task_description
        self.task_progress = 0
        self.current_step = 0

        if steps:
            import json
            self.task_steps = json.dumps(steps)

    def get_task_steps(self):
        """Get task steps as list"""
        if self.task_steps:
            import json
            try:
                return json.loads(self.task_steps)
            except:
                return []
        return []

    # New unified chat properties
    show_full_history: BoolProperty(
        name="Show Full History",
        description="Show complete conversation history instead of recent messages",
        default=False,
    )



    voice_input_available: BoolProperty(
        name="Voice Input Available",
        description="Whether voice input is available on this system",
        default=False,
    )

    chat_scroll_position: IntProperty(
        name="Chat Scroll Position",
        description="Current scroll position in chat",
        default=0,
    )

    smart_suggestions_enabled: BoolProperty(
        name="Smart Suggestions Enabled",
        description="Enable context-aware smart suggestions",
        default=True,
    )

def register():
    """Register properties"""
    bpy.utils.register_class(S647ConversationMessage)
    bpy.utils.register_class(S647Properties)
    
    # Add properties to scene
    bpy.types.Scene.s647 = PointerProperty(type=S647Properties)

def unregister():
    """Unregister properties"""
    # Remove properties from scene
    del bpy.types.Scene.s647
    
    bpy.utils.unregister_class(S647Properties)
    bpy.utils.unregister_class(S647ConversationMessage)
