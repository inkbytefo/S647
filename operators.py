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
S647 Operators Module
=====================

Defines all operators for the S647 addon including AI interaction,
code execution, and utility operations.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty

from . import utils
from .preferences import get_preferences

class S647_OT_SendPrompt(Operator):
    """Send prompt to AI assistant"""
    bl_idname = "s647.send_prompt"
    bl_label = "Send to AI"
    bl_description = "Send the current prompt to the AI assistant"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.scene.s647
        prefs = get_preferences()

        # Check AI configuration using AI Config Manager
        try:
            from .ai_config_manager import get_ai_config_manager
            config_manager = get_ai_config_manager()

            # Initialize from preferences if not already done
            if not config_manager.is_ready():
                success, message = config_manager.initialize_from_preferences()
                if not success:
                    self.report({'ERROR'}, f"AI configuration error: {message}")
                    return {'CANCELLED'}

            # Ensure provider is ready
            if not config_manager.is_ready():
                self.report({'ERROR'}, "AI provider not ready. Check configuration in preferences.")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to initialize AI: {str(e)}")
            return {'CANCELLED'}

        # Check prompt
        if not props.current_prompt.strip():
            self.report({'WARNING'}, "Please enter a prompt first.")
            return {'CANCELLED'}

        # Check if AI engine is available
        try:
            from . import ai_engine

            if not ai_engine.is_available():
                # Try to initialize
                ai_engine.initialize()

                if not ai_engine.is_available():
                    self.report({'ERROR'}, "AI engine not available. Check your API key and internet connection.")
                    return {'CANCELLED'}

        except ImportError:
            self.report({'ERROR'}, "AI engine module not found")
            return {'CANCELLED'}

        # Check if already processing
        if props.ai_status in ['thinking', 'responding']:
            self.report({'WARNING'}, "AI is already processing a request. Please wait.")
            return {'CANCELLED'}

        # Set status to thinking
        props.ai_status = 'thinking'
        props.ai_status_message = "Processing your request..."

        # Add user message to history with thread and intent detection
        props.add_message('user', props.current_prompt)

        # Update the latest message with current thread and detected intent
        if props.conversation_history:
            latest_msg = props.conversation_history[-1]
            latest_msg.thread_id = props.current_thread_id
            latest_msg.intent_type = self.detect_intent(props.current_prompt, props.interaction_mode)

        # Store the prompt and clear input
        current_prompt = props.current_prompt
        props.current_prompt = ""

        # Trigger AI processing
        try:
            ai_engine.process_prompt_async(current_prompt)
            self.report({'INFO'}, "Request sent to AI assistant")
        except Exception as e:
            props.ai_status = 'error'
            props.ai_status_message = f"Error: {str(e)}"
            self.report({'ERROR'}, f"Failed to process request: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def detect_intent(self, prompt: str, mode: str) -> str:
        """Detect user intent from prompt"""
        prompt_lower = prompt.lower()

        # Question indicators
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        question_patterns = ['?', 'explain', 'tell me', 'show me']

        # Command indicators
        command_words = ['create', 'make', 'add', 'delete', 'remove', 'move', 'rotate', 'scale']
        command_patterns = ['please', 'can you', 'could you']

        # Feedback indicators
        feedback_words = ['good', 'bad', 'wrong', 'correct', 'thanks', 'thank you']

        # Check for questions
        if any(word in prompt_lower for word in question_words) or any(pattern in prompt_lower for pattern in question_patterns):
            return 'question'

        # Check for commands
        if any(word in prompt_lower for word in command_words) or (mode == 'act' and any(pattern in prompt_lower for pattern in command_patterns)):
            return 'command'

        # Check for feedback
        if any(word in prompt_lower for word in feedback_words):
            return 'feedback'

        # Default based on mode
        return 'command' if mode == 'act' else 'question'

class S647_OT_ExecuteCode(Operator):
    """Execute AI-generated code"""
    bl_idname = "s647.execute_code"
    bl_label = "Execute Code"
    bl_description = "Execute the pending AI-generated code"
    bl_options = {'REGISTER', 'UNDO'}
    
    code: StringProperty(
        name="Code",
        description="Python code to execute",
        default="",
    )
    
    def execute(self, context):
        props = context.scene.s647
        prefs = get_preferences()

        if not prefs.enable_code_execution:
            self.report({'ERROR'}, "Code execution is disabled. Enable it in addon preferences.")
            return {'CANCELLED'}

        code = self.code or props.pending_code
        if not code.strip():
            self.report({'WARNING'}, "No code to execute.")
            return {'CANCELLED'}

        # Validate code syntax
        is_valid, error_msg = utils.validate_python_code(code)
        if not is_valid:
            self.report({'ERROR'}, f"Invalid Python code: {error_msg}")
            return {'CANCELLED'}

        # Simple execution with minimal safety checks (Blender MCP style)
        try:
            from . import code_executor

            # Execute code directly with simplified approach
            result = code_executor.execute_code(code)

            # Update properties
            props.code_execution_result = result
            props.pending_code = ""
            props.code_executions += 1

            # Mark message as executed if it exists
            if props.conversation_history:
                last_msg = props.conversation_history[-1]
                if last_msg.role == 'assistant' and last_msg.has_code:
                    last_msg.code_executed = True

            # Report success with summary
            if "Error" in result or "blocked" in result:
                self.report({'ERROR'}, "Code execution failed - check output for details")
            elif "Warning" in result:
                self.report({'WARNING'}, "Code executed with warnings - check output")
            else:
                execution_time = "0.000s"
                if "completed in" in result:
                    # Extract execution time from result
                    import re
                    time_match = re.search(r'completed in ([\d.]+)s', result)
                    if time_match:
                        execution_time = time_match.group(1) + "s"

                self.report({'INFO'}, f"Code executed successfully in {execution_time}")

        except Exception as e:
            error_msg = str(e)
            props.code_execution_result = f"Execution Error: {error_msg}"
            self.report({'ERROR'}, f"Code execution failed: {error_msg}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_ClearConversation(Operator):
    """Clear conversation history"""
    bl_idname = "s647.clear_conversation"
    bl_label = "Clear Conversation"
    bl_description = "Clear the conversation history"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.scene.s647
        props.clear_conversation()
        props.ai_status = 'idle'
        props.ai_status_message = "Ready"
        
        self.report({'INFO'}, "Conversation cleared")
        return {'FINISHED'}

class S647_OT_CopyCode(Operator):
    """Copy code to clipboard"""
    bl_idname = "s647.copy_code"
    bl_label = "Copy Code"
    bl_description = "Copy the code to clipboard"
    bl_options = {'REGISTER'}
    
    code: StringProperty(
        name="Code",
        description="Code to copy",
        default="",
    )
    
    def execute(self, context):
        if not self.code:
            self.report({'WARNING'}, "No code to copy")
            return {'CANCELLED'}
        
        # Copy to clipboard
        context.window_manager.clipboard = self.code
        self.report({'INFO'}, "Code copied to clipboard")
        return {'FINISHED'}

class S647_OT_SaveConversation(Operator):
    """Save conversation to file"""
    bl_idname = "s647.save_conversation"
    bl_label = "Save Conversation"
    bl_description = "Save the conversation history to a text file"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="File Path",
        description="Path to save the conversation",
        default="s647_conversation.txt",
        subtype='FILE_PATH',
    )
    
    def execute(self, context):
        props = context.scene.s647
        
        if not props.conversation_history:
            self.report({'WARNING'}, "No conversation to save")
            return {'CANCELLED'}
        
        try:
            import datetime
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(f"S647 Conversation Export\n")
                f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Scene: {context.scene.name}\n")
                f.write("=" * 50 + "\n\n")
                
                for i, msg in enumerate(props.conversation_history):
                    f.write(f"[{msg.timestamp}] {msg.role.upper()}:\n")
                    f.write(f"{msg.content}\n")
                    if msg.has_code:
                        f.write("(Contains executable code)\n")
                    f.write("\n" + "-" * 30 + "\n\n")
            
            self.report({'INFO'}, f"Conversation saved to {self.filepath}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save conversation: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# S647_OT_LoadConversation removed - functionality integrated into unified chat

class S647_OT_ToggleAdvanced(Operator):
    """Toggle advanced options display"""
    bl_idname = "s647.toggle_advanced"
    bl_label = "Toggle Advanced"
    bl_description = "Toggle advanced options visibility"
    bl_options = {'REGISTER'}

    def execute(self, context):
        prefs = get_preferences()
        prefs.show_advanced_options = not prefs.show_advanced_options
        return {'FINISHED'}

class S647_OT_TestConnection(Operator):
    """Test OpenAI API connection"""
    bl_idname = "s647.test_connection"
    bl_label = "Test API Connection"
    bl_description = "Test the connection to OpenAI API"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from .ai_config_manager import get_ai_config_manager
            config_manager = get_ai_config_manager()

            # Initialize from preferences
            success, message = config_manager.initialize_from_preferences()
            if not success:
                self.report({'ERROR'}, f"Configuration error: {message}")
                return {'CANCELLED'}

            # Test connection using config manager
            provider = config_manager.get_current_provider()
            if not provider:
                self.report({'ERROR'}, "No AI provider available")
                return {'CANCELLED'}

            success, message = provider.test_connection()
            if success:
                self.report({'INFO'}, f"✓ {message}")
            else:
                self.report({'ERROR'}, f"✗ {message}")

        except Exception as e:
            self.report({'ERROR'}, f"Connection test failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_DebugAI(Operator):
    """Debug AI engine status"""
    bl_idname = "s647.debug_ai"
    bl_label = "Debug AI Engine"
    bl_description = "Show detailed AI engine debug information"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from . import ai_engine

            # Get status
            status = ai_engine.get_api_status()

            print("=== S647 AI Engine Debug ===")
            print(f"Initialized: {status['initialized']}")
            print(f"OpenAI Available: {status['openai_available']}")
            print(f"Client Ready: {status['client_ready']}")

            # Test imports
            try:
                import openai
                print(f"OpenAI Version: {openai.__version__}")
            except ImportError as e:
                print(f"OpenAI Import Error: {e}")

            # Test preferences
            from .preferences import get_preferences
            prefs = get_preferences()
            print(f"Provider Type: {prefs.provider_type}")
            print(f"API Key Set: {'Yes' if prefs.api_key else 'No'}")
            print(f"Model: {prefs.api_model if prefs.provider_type == 'openai' else prefs.custom_model}")

            self.report({'INFO'}, "Debug info printed to console")

        except Exception as e:
            print(f"Debug error: {e}")
            self.report({'ERROR'}, f"Debug failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_TestAIMessage(Operator):
    """Send a test message to AI"""
    bl_idname = "s647.test_ai_message"
    bl_label = "Test AI Message"
    bl_description = "Send a simple test message to verify AI functionality"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from . import ai_engine

            # Initialize if needed
            if not ai_engine.is_available():
                ai_engine.initialize()

                if not ai_engine.is_available():
                    self.report({'ERROR'}, "AI engine not available")
                    return {'CANCELLED'}

            # Send test message
            success, message = ai_engine.send_simple_test_message()

            if success:
                self.report({'INFO'}, "Test successful!")
                # Update scene properties with the response
                props = context.scene.s647
                props.last_response = message
                props.add_message('user', 'Test message')
                props.add_message('assistant', message)
            else:
                self.report({'ERROR'}, f"Test failed: {message}")

        except Exception as e:
            self.report({'ERROR'}, f"Test error: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_InitializeAI(Operator):
    """Initialize AI engine"""
    bl_idname = "s647.initialize_ai"
    bl_label = "Initialize AI"
    bl_description = "Initialize the AI engine with current settings"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from . import ai_engine
            ai_engine.initialize()

            if ai_engine.is_available():
                self.report({'INFO'}, "AI engine initialized successfully")
            else:
                self.report({'ERROR'}, "AI engine initialization failed")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Initialization failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class S647_OT_ManageMCPServers(Operator):
    """Manage MCP servers"""
    bl_idname = "s647.manage_mcp_servers"
    bl_label = "Manage MCP Servers"
    bl_description = "Open MCP server management interface"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # For now, just show a simple dialog
        # In the future, this could open a more complex UI
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = self.layout

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

            # Server list
            box = layout.box()
            box.label(text="Configured Servers:", icon='NETWORK_DRIVE')

            servers = manager.get_all_servers()
            if not servers:
                box.label(text="No servers configured")
            else:
                for name, config in servers.items():
                    row = box.row()
                    status = manager.get_server_status(name)

                    # Status icon
                    if status.value == "connected":
                        row.label(text="", icon='CHECKMARK')
                    elif status.value == "connecting":
                        row.label(text="", icon='TIME')
                    elif status.value == "error":
                        row.label(text="", icon='ERROR')
                    else:
                        row.label(text="", icon='RADIOBUT_OFF')

                    # Server info
                    row.label(text=f"{name} ({config.command})")

                    # Connect/Disconnect button
                    if status.value == "connected":
                        row.operator("s647.disconnect_mcp_server", text="Disconnect").server_name = name
                    else:
                        row.operator("s647.connect_mcp_server", text="Connect").server_name = name

            # Available tools
            layout.separator()
            box = layout.box()
            box.label(text="Available Tools:", icon='TOOL_SETTINGS')

            tools = manager.get_all_tools()
            if not tools:
                box.label(text="No tools available")
            else:
                for tool_key, tool in list(tools.items())[:10]:  # Show first 10 tools
                    row = box.row()
                    row.label(text=f"{tool.name} ({tool.server_name})")

                if len(tools) > 10:
                    box.label(text=f"... and {len(tools) - 10} more tools")

            # Quick server addition
            layout.separator()
            box = layout.box()
            box.label(text="Quick Add Server:", icon='ADD')
            box.label(text="Use the examples below or add custom servers")

            # Example servers
            examples = [
                ("Sequential Thinking", "npx", "-y @modelcontextprotocol/server-sequential-thinking"),
                ("Weather Server", "python", "weather_server.py"),
                ("File System", "node", "filesystem_server.js"),
                ("Database", "python", "db_server.py"),
            ]

            for name, cmd, script in examples:
                row = box.row()
                row.label(text=f"{name}: {cmd} {script}")
                op = row.operator("s647.add_example_mcp_server", text="Add")
                op.server_name = name
                op.command = cmd
                op.script = script

        except Exception as e:
            layout.label(text=f"Error: {str(e)}", icon='ERROR')


class S647_OT_ConnectMCPServer(Operator):
    """Connect to MCP server"""
    bl_idname = "s647.connect_mcp_server"
    bl_label = "Connect MCP Server"
    bl_description = "Connect to an MCP server"
    bl_options = {'REGISTER'}

    server_name: StringProperty(name="Server Name")

    def execute(self, context):
        try:
            from . import mcp_client

            manager = mcp_client.get_mcp_manager()
            if not manager:
                self.report({'ERROR'}, "MCP Manager not available")
                return {'CANCELLED'}

            success = manager.connect_server(self.server_name)
            if success:
                self.report({'INFO'}, f"Connected to {self.server_name}")
            else:
                self.report({'ERROR'}, f"Failed to connect to {self.server_name}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Connection failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class S647_OT_DisconnectMCPServer(Operator):
    """Disconnect from MCP server"""
    bl_idname = "s647.disconnect_mcp_server"
    bl_label = "Disconnect MCP Server"
    bl_description = "Disconnect from an MCP server"
    bl_options = {'REGISTER'}

    server_name: StringProperty(name="Server Name")

    def execute(self, context):
        try:
            from . import mcp_client

            manager = mcp_client.get_mcp_manager()
            if not manager:
                self.report({'ERROR'}, "MCP Manager not available")
                return {'CANCELLED'}

            success = manager.disconnect_server(self.server_name)
            if success:
                self.report({'INFO'}, f"Disconnected from {self.server_name}")
            else:
                self.report({'ERROR'}, f"Failed to disconnect from {self.server_name}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Disconnection failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class S647_OT_AddExampleMCPServer(Operator):
    """Add example MCP server"""
    bl_idname = "s647.add_example_mcp_server"
    bl_label = "Add Example MCP Server"
    bl_description = "Add an example MCP server configuration"
    bl_options = {'REGISTER'}

    server_name: StringProperty(name="Server Name")
    command: StringProperty(name="Command")
    script: StringProperty(name="Script")

    def execute(self, context):
        try:
            from . import mcp_client

            success = mcp_client.add_mcp_server(
                name=self.server_name,
                command=self.command,
                args=[self.script],
                description=f"Example {self.server_name} server"
            )

            if success:
                self.report({'INFO'}, f"Added server configuration: {self.server_name}")
            else:
                self.report({'ERROR'}, f"Failed to add server: {self.server_name}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to add server: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class S647_OT_ImportMCPConfig(Operator):
    """Import MCP server configuration from JSON"""
    bl_idname = "s647.import_mcp_config"
    bl_label = "Import MCP Configuration"
    bl_description = "Import MCP server configuration from Claude Desktop compatible JSON"
    bl_options = {'REGISTER'}

    config_text: bpy.props.StringProperty(
        name="Configuration JSON",
        description="Paste your MCP configuration JSON here",
        default="",
        maxlen=10000
    )

    def execute(self, context):
        if not self.config_text.strip():
            self.report({'ERROR'}, "No configuration provided")
            return {'CANCELLED'}

        try:
            from . import mcp_config

            # Validate configuration
            validation = mcp_config.validate_mcp_config(self.config_text)

            if not validation["valid"]:
                error_msg = "Configuration validation failed:\n" + "\n".join(validation["errors"])
                self.report({'ERROR'}, error_msg)
                return {'CANCELLED'}

            # Parse and convert configuration
            config_manager = mcp_config.get_config_manager()
            config = config_manager.parse_claude_desktop_config(self.config_text)

            if not config:
                self.report({'ERROR'}, "Failed to parse configuration")
                return {'CANCELLED'}

            # Convert to S647 format and add servers
            server_configs = config_manager.convert_to_s647_format(config)

            from . import mcp_client
            manager = mcp_client.get_mcp_manager()

            if not manager:
                self.report({'ERROR'}, "MCP Manager not available")
                return {'CANCELLED'}

            success_count = 0
            for server_config in server_configs:
                from .mcp_client import MCPServerConfig

                mcp_server_config = MCPServerConfig(
                    name=server_config["name"],
                    command=server_config["command"],
                    args=server_config["args"],
                    env=server_config["env"],
                    enabled=server_config["enabled"],
                    description=server_config["description"],
                    timeout=server_config["timeout"]
                )

                if manager.add_server(mcp_server_config):
                    success_count += 1

            if success_count > 0:
                self.report({'INFO'}, f"Successfully imported {success_count} server configuration(s)")

                # Save to mcp.json
                mcp_config.save_mcp_config(config)
            else:
                self.report({'WARNING'}, "No servers were imported")

        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        # Instructions
        box = layout.box()
        box.label(text="Import MCP Configuration", icon='IMPORT')
        box.label(text="Paste Claude Desktop compatible JSON configuration:")

        # Example format
        example_box = box.box()
        example_box.label(text="Example format:")
        example_lines = [
            '{',
            '  "mcpServers": {',
            '    "server-name": {',
            '      "command": "npx",',
            '      "args": ["-y", "@package/name"]',
            '    }',
            '  }',
            '}'
        ]
        for line in example_lines:
            example_box.label(text=line, icon='NONE')

        # Text input
        layout.separator()
        layout.prop(self, "config_text", text="")

        # Validation info
        if self.config_text.strip():
            try:
                from . import mcp_config
                validation = mcp_config.validate_mcp_config(self.config_text)

                if validation["valid"]:
                    layout.label(text="✓ Configuration is valid", icon='CHECKMARK')
                    if validation["warnings"]:
                        warning_box = layout.box()
                        warning_box.label(text="Warnings:", icon='ERROR')
                        for warning in validation["warnings"]:
                            warning_box.label(text=f"• {warning}")
                else:
                    error_box = layout.box()
                    error_box.label(text="Configuration errors:", icon='ERROR')
                    for error in validation["errors"]:
                        error_box.label(text=f"• {error}")

            except Exception as e:
                layout.label(text=f"Validation error: {str(e)}", icon='ERROR')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)


class S647_OT_LoadMCPConfigFile(Operator):
    """Load MCP configuration from mcp.json file"""
    bl_idname = "s647.load_mcp_config_file"
    bl_label = "Load MCP Config File"
    bl_description = "Load MCP server configuration from mcp.json file"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from . import mcp_config

            success = mcp_config.load_mcp_config()

            if success:
                self.report({'INFO'}, "MCP configuration loaded successfully")
            else:
                self.report({'WARNING'}, "No valid MCP configuration found")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to load configuration: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class S647_OT_ExportMCPConfig(Operator):
    """Export current MCP configuration to JSON"""
    bl_idname = "s647.export_mcp_config"
    bl_label = "Export MCP Configuration"
    bl_description = "Export current MCP server configuration to JSON format"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from . import mcp_client
            import json

            manager = mcp_client.get_mcp_manager()
            if not manager:
                self.report({'ERROR'}, "MCP Manager not available")
                return {'CANCELLED'}

            servers = manager.get_all_servers()
            if not servers:
                self.report({'WARNING'}, "No servers configured")
                return {'CANCELLED'}

            # Convert to Claude Desktop format
            config = {"mcpServers": {}}

            for name, server_config in servers.items():
                config["mcpServers"][name] = {
                    "command": server_config.command,
                    "args": server_config.args,
                    "description": server_config.description,
                    "enabled": server_config.enabled
                }

                if server_config.env:
                    config["mcpServers"][name]["env"] = server_config.env

            # Format JSON for display
            json_text = json.dumps(config, indent=2)

            # Copy to clipboard (if possible)
            try:
                context.window_manager.clipboard = json_text
                self.report({'INFO'}, "Configuration exported to clipboard")
            except:
                self.report({'INFO'}, "Configuration exported (clipboard not available)")

            # Also save to file
            from . import mcp_config
            mcp_config.save_mcp_config(config)

            # Show in console
            print("S647: Exported MCP Configuration:")
            print(json_text)

        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_AnalyzeCode(Operator):
    """Analyze code for safety and potential issues"""
    bl_idname = "s647.analyze_code"
    bl_label = "Analyze Code"
    bl_description = "Analyze the pending code for safety issues and potential problems"
    bl_options = {'REGISTER'}

    code: StringProperty(
        name="Code",
        description="Python code to analyze",
        default="",
    )

    def execute(self, context):
        props = context.scene.s647
        prefs = get_preferences()

        code = self.code or props.pending_code
        if not code.strip():
            self.report({'WARNING'}, "No code to analyze.")
            return {'CANCELLED'}

        try:
            from . import code_executor

            # Simple safety check using new system
            dangerous_operations = [
                'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
                'os.remove', 'os.unlink', 'os.rmdir', 'shutil.rmtree',
                'bpy.ops.wm.quit'
            ]

            # Check for dangerous operations
            found_dangerous = []
            for dangerous_op in dangerous_operations:
                if dangerous_op in code:
                    found_dangerous.append(dangerous_op)

            # Create simplified report
            report_lines = []
            report_lines.append("Code Analysis Report (Simplified)")
            report_lines.append("=" * 40)

            if found_dangerous:
                report_lines.append("⚠️ DANGEROUS OPERATIONS DETECTED:")
                for op in found_dangerous:
                    report_lines.append(f"  - {op}")
                report_lines.append("")
                report_lines.append("❌ Code execution would be BLOCKED")
                is_safe = False
            else:
                report_lines.append("✅ No dangerous operations detected")
                report_lines.append("✅ Code is safe to execute")
                is_safe = True

            report_lines.append("")
            report_lines.append("Note: Using simplified safety system (Blender MCP style)")
            report_lines.append("Only truly dangerous operations are blocked.")

            # Store analysis result
            analysis_report = "\n".join(report_lines)
            props.code_execution_result = analysis_report

            # Report summary
            if found_dangerous:
                self.report({'ERROR'}, f"Analysis found {len(found_dangerous)} dangerous operations")
            else:
                self.report({'INFO'}, "Code analysis complete - safe to execute")

        except Exception as e:
            self.report({'ERROR'}, f"Code analysis failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_SwitchMode(Operator):
    """Switch interaction mode"""
    bl_idname = "s647.switch_mode"
    bl_label = "Switch Mode"
    bl_description = "Switch between Chat and Act modes"
    bl_options = {'REGISTER'}

    mode: StringProperty(
        name="Mode",
        description="Target interaction mode",
        default="chat"
    )

    def execute(self, context):
        props = context.scene.s647

        # Validate mode
        if self.mode not in ['chat', 'act']:
            self.report({'ERROR'}, f"Invalid mode: {self.mode}")
            return {'CANCELLED'}

        props.interaction_mode = self.mode

        # Clear current task if switching away from Act mode
        if self.mode != 'act':
            props.current_task = ""
            props.task_progress = 0
            props.current_step = 0

        self.report({'INFO'}, f"Switched to {self.mode.title()} mode")
        return {'FINISHED'}

class S647_OT_ShowFullHistory(Operator):
    """Show full conversation history"""
    bl_idname = "s647.show_full_history"
    bl_label = "Show Full History"
    bl_description = "Show complete conversation history"
    bl_options = {'REGISTER'}

    def execute(self, context):
        return context.window_manager.invoke_props_dialog(self, width=800)

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647

        # Title
        layout.label(text="Complete Conversation History", icon='OUTLINER')
        layout.separator()

        # Scrollable area for messages
        box = layout.box()
        col = box.column()

        for i, msg in enumerate(props.conversation_history):
            # Message header
            row = col.row()
            if msg.role == 'user':
                row.label(text=f"💬 You ({msg.timestamp})", icon='USER')
            else:
                row.label(text=f"🤖 S647 ({msg.timestamp})", icon='BLENDER')

            # Message content with better formatting
            content_box = col.box()
            content_lines = msg.content.split('\n')

            for line in content_lines:
                if line.strip():
                    # Split long lines for better readability
                    if len(line) > 100:
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) > 100 and current_line:
                                content_box.label(text=current_line.strip())
                                current_line = word + " "
                            else:
                                current_line += word + " "
                        if current_line.strip():
                            content_box.label(text=current_line.strip())
                    else:
                        content_box.label(text=line)
                else:
                    # Add small separator for empty lines
                    content_box.separator(factor=0.3)

            # Code execution button if applicable
            if msg.has_code and not msg.code_executed:
                code_row = content_box.row()
                code_op = code_row.operator("s647.apply_message_code", text="Execute Code", icon='PLAY')
                code_op.message_index = i

            col.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

class S647_OT_ExpandMessage(Operator):
    """Expand a truncated message"""
    bl_idname = "s647.expand_message"
    bl_label = "Expand Message"
    bl_description = "Show full content of a truncated message"
    bl_options = {'REGISTER'}

    message_index: IntProperty(
        name="Message Index",
        description="Index of the message to expand",
        default=0
    )

    def execute(self, context):
        return context.window_manager.invoke_props_dialog(self, width=800)

    def draw(self, context):
        layout = self.layout
        props = context.scene.s647

        if self.message_index < len(props.conversation_history):
            message = props.conversation_history[self.message_index]

            # Message header
            layout.label(text=f"Full Message from {message.role.title()}", icon='TEXT')
            if message.timestamp:
                layout.label(text=f"Time: {message.timestamp}")
            layout.separator()

            # Full message content in a scrollable area
            content_lines = message.content.split('\n')

            # Create a column for better content organization
            col = layout.column()
            col.scale_y = 0.9

            # Show content with proper text wrapping
            for i, line in enumerate(content_lines):
                # Create a box for each paragraph (group of non-empty lines)
                if line.strip():
                    # Split long lines for better readability
                    if len(line) > 80:
                        # Split line into chunks of 80 characters at word boundaries
                        words = line.split(' ')
                        current_line = ""
                        for word in words:
                            if len(current_line + word) > 80 and current_line:
                                row = col.row()
                                row.scale_y = 0.8
                                row.label(text=current_line.strip())
                                current_line = word + " "
                            else:
                                current_line += word + " "
                        if current_line.strip():
                            row = col.row()
                            row.scale_y = 0.8
                            row.label(text=current_line.strip())
                    else:
                        row = col.row()
                        row.scale_y = 0.8
                        row.label(text=line)
                else:
                    # Add small separator for empty lines
                    if i > 0 and i < len(content_lines) - 1:
                        col.separator(factor=0.5)

            # Code execution button if applicable
            if message.has_code and not message.code_executed:
                layout.separator()
                code_op = layout.operator("s647.apply_message_code", text="Execute Code", icon='PLAY')
                code_op.message_index = self.message_index
        else:
            layout.label(text="Message not found", icon='ERROR')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

class S647_OT_ApplyMessageCode(Operator):
    """Apply code from a specific message"""
    bl_idname = "s647.apply_message_code"
    bl_label = "Apply Code"
    bl_description = "Apply code from this AI message"
    bl_options = {'REGISTER'}

    message_index: IntProperty(
        name="Message Index",
        description="Index of the message containing code",
        default=0
    )

    def execute(self, context):
        props = context.scene.s647

        if self.message_index < len(props.conversation_history):
            message = props.conversation_history[self.message_index]
            if message.has_code:
                # Extract and execute code from the message
                from . import utils
                code_blocks = utils.extract_python_code(message.content)

                if code_blocks:
                    # Execute the first code block using safe executor
                    code, _, _ = code_blocks[0]
                    try:
                        from . import code_executor
                        result = code_executor.execute_code(code)

                        # Check if execution was successful
                        if "Code execution blocked" in result:
                            self.report({'ERROR'}, result)
                        elif "Code execution error" in result:
                            self.report({'ERROR'}, result)
                        else:
                            message.code_executed = True
                            self.report({'INFO'}, "Code executed successfully")
                    except Exception as e:
                        self.report({'ERROR'}, f"Code execution failed: {str(e)}")
                else:
                    self.report({'WARNING'}, "No executable code found in message")
            else:
                self.report({'WARNING'}, "Message contains no code")
        else:
            self.report({'ERROR'}, "Invalid message index")

        return {'FINISHED'}

class S647_OT_ExplainCode(Operator):
    """Request explanation for code in a message"""
    bl_idname = "s647.explain_code"
    bl_label = "Explain Code"
    bl_description = "Ask AI to explain the code in this message"
    bl_options = {'REGISTER'}

    message_index: IntProperty(
        name="Message Index",
        description="Index of the message containing code",
        default=0
    )

    def execute(self, context):
        props = context.scene.s647

        if self.message_index < len(props.conversation_history):
            message = props.conversation_history[self.message_index]
            if message.has_code:
                # Set up a follow-up prompt asking for explanation
                props.current_prompt = "Please explain the code you just provided in detail."
                self.report({'INFO'}, "Explanation request prepared")
            else:
                self.report({'WARNING'}, "Message contains no code")
        else:
            self.report({'ERROR'}, "Invalid message index")

        return {'FINISHED'}

class S647_OT_ModifyCode(Operator):
    """Request modification of code in a message"""
    bl_idname = "s647.modify_code"
    bl_label = "Modify Code"
    bl_description = "Ask AI to modify the code in this message"
    bl_options = {'REGISTER'}

    message_index: IntProperty(
        name="Message Index",
        description="Index of the message containing code",
        default=0
    )

    def execute(self, context):
        props = context.scene.s647

        if self.message_index < len(props.conversation_history):
            message = props.conversation_history[self.message_index]
            if message.has_code:
                # Set up a follow-up prompt asking for modification
                props.current_prompt = "Please modify the code you just provided. What changes would you like me to make?"
                self.report({'INFO'}, "Modification request prepared")
            else:
                self.report({'WARNING'}, "Message contains no code")
        else:
            self.report({'ERROR'}, "Invalid message index")

        return {'FINISHED'}

class S647_OT_ShowSuggestions(Operator):
    """Show smart suggestions"""
    bl_idname = "s647.show_suggestions"
    bl_label = "Show Suggestions"
    bl_description = "Show context-aware suggestions"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # This could open a popup with suggestions
        self.report({'INFO'}, "Smart suggestions feature coming soon")
        return {'FINISHED'}

class S647_OT_ManageContext(Operator):
    """Manage conversation context"""
    bl_idname = "s647.manage_context"
    bl_label = "Manage Context"
    bl_description = "Manage conversation context and memory"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # This could open context management interface
        self.report({'INFO'}, "Context management feature coming soon")
        return {'FINISHED'}

class S647_OT_VoiceInput(Operator):
    """Voice input for chat"""
    bl_idname = "s647.voice_input"
    bl_label = "Voice Input"
    bl_description = "Use voice input for chat"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # This could activate voice recognition
        self.report({'INFO'}, "Voice input feature coming soon")
        return {'FINISHED'}

class S647_OT_OpenSettings(Operator):
    """Open S647 settings"""
    bl_idname = "s647.open_settings"
    bl_label = "Open Settings"
    bl_description = "Open S647 addon settings"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Open addon preferences
        bpy.ops.preferences.addon_show(module=__package__)
        return {'FINISHED'}

class S647_OT_SaveContext(Operator):
    """Save current context to persistent memory"""
    bl_idname = "s647.save_context"
    bl_label = "Save Context"
    bl_description = "Save current conversation context to persistent memory"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647

        try:
            import json
            import datetime

            # Gather context data
            context_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "thread_id": props.current_thread_id,
                "thread_title": props.thread_title,
                "interaction_mode": props.interaction_mode,
                "conversation_summary": self.summarize_conversation(props),
                "user_preferences": props.user_preferences_learned,
                "session_context": props.session_context
            }

            # Save to context memory
            props.context_memory = json.dumps(context_data)

            self.report({'INFO'}, "Context saved successfully")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to save context: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def summarize_conversation(self, props):
        """Create a summary of recent conversation"""
        recent_messages = []
        for msg in props.conversation_history[-10:]:  # Last 10 messages
            recent_messages.append(f"{msg.role}: {msg.content[:100]}...")
        return "\n".join(recent_messages)

class S647_OT_LoadContext(Operator):
    """Load context from persistent memory"""
    bl_idname = "s647.load_context"
    bl_label = "Load Context"
    bl_description = "Load conversation context from persistent memory"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647

        try:
            if not props.context_memory:
                self.report({'WARNING'}, "No saved context found")
                return {'CANCELLED'}

            import json
            context_data = json.loads(props.context_memory)

            # Restore context
            props.current_thread_id = context_data.get("thread_id", "main")
            props.thread_title = context_data.get("thread_title", "General Chat")
            props.interaction_mode = context_data.get("interaction_mode", "chat")
            props.user_preferences_learned = context_data.get("user_preferences", "")
            props.session_context = context_data.get("session_context", "")

            self.report({'INFO'}, f"Context loaded from {context_data.get('timestamp', 'unknown time')}")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to load context: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_ClearContext(Operator):
    """Clear all context memory"""
    bl_idname = "s647.clear_context"
    bl_label = "Clear Context"
    bl_description = "Clear all saved context and memory"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647

        # Clear all context
        props.context_memory = ""
        props.session_context = ""
        props.user_preferences_learned = ""
        props.current_thread_id = "main"
        props.thread_title = "General Chat"

        self.report({'INFO'}, "All context cleared")
        return {'FINISHED'}

class S647_OT_ExportContext(Operator):
    """Export context to file"""
    bl_idname = "s647.export_context"
    bl_label = "Export Context"
    bl_description = "Export conversation context to a file"
    bl_options = {'REGISTER'}

    filepath: StringProperty(
        name="File Path",
        description="Path to save the context file",
        default="s647_context.json",
        subtype='FILE_PATH'
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        props = context.scene.s647

        try:
            import json
            import datetime

            # Gather all context data
            export_data = {
                "export_timestamp": datetime.datetime.now().isoformat(),
                "thread_id": props.current_thread_id,
                "thread_title": props.thread_title,
                "interaction_mode": props.interaction_mode,
                "context_memory": props.context_memory,
                "session_context": props.session_context,
                "user_preferences": props.user_preferences_learned,
                "conversation_history": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "thread_id": msg.thread_id,
                        "intent_type": msg.intent_type,
                        "has_code": msg.has_code
                    }
                    for msg in props.conversation_history
                ]
            }

            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.report({'INFO'}, f"Context exported to {self.filepath}")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to export context: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_CreateThread(Operator):
    """Create a new conversation thread"""
    bl_idname = "s647.create_thread"
    bl_label = "Create Thread"
    bl_description = "Create a new conversation thread"
    bl_options = {'REGISTER'}

    thread_title: StringProperty(
        name="Thread Title",
        description="Title for the new thread",
        default="New Thread"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        props = context.scene.s647

        # Generate unique thread ID
        import uuid
        thread_id = str(uuid.uuid4())[:8]

        # Switch to new thread
        props.switch_thread(thread_id, self.thread_title)

        self.report({'INFO'}, f"Created new thread: {self.thread_title}")
        return {'FINISHED'}

class S647_OT_SwitchThread(Operator):
    """Switch to a different conversation thread"""
    bl_idname = "s647.switch_thread"
    bl_label = "Switch Thread"
    bl_description = "Switch to a different conversation thread"
    bl_options = {'REGISTER'}

    thread_id: StringProperty(
        name="Thread ID",
        description="ID of the thread to switch to",
        default="main"
    )

    thread_title: StringProperty(
        name="Thread Title",
        description="Title of the thread",
        default="Main Thread"
    )

    def execute(self, context):
        props = context.scene.s647
        props.switch_thread(self.thread_id, self.thread_title)

        self.report({'INFO'}, f"Switched to thread: {self.thread_title}")
        return {'FINISHED'}

class S647_OT_RenameThread(Operator):
    """Rename the current conversation thread"""
    bl_idname = "s647.rename_thread"
    bl_label = "Rename Thread"
    bl_description = "Rename the current conversation thread"
    bl_options = {'REGISTER'}

    new_title: StringProperty(
        name="New Title",
        description="New title for the thread",
        default=""
    )

    def invoke(self, context, event):
        props = context.scene.s647
        self.new_title = props.thread_title
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        props = context.scene.s647

        if not self.new_title.strip():
            self.report({'WARNING'}, "Thread title cannot be empty")
            return {'CANCELLED'}

        old_title = props.thread_title
        props.thread_title = self.new_title.strip()

        self.report({'INFO'}, f"Thread renamed from '{old_title}' to '{self.new_title}'")
        return {'FINISHED'}

class S647_OT_StartTask(Operator):
    """Start a new task in Act mode"""
    bl_idname = "s647.start_task"
    bl_label = "Start Task"
    bl_description = "Start a new task with step breakdown"
    bl_options = {'REGISTER'}

    task_description: StringProperty(
        name="Task Description",
        description="Description of the task to perform",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        props = context.scene.s647

        if not self.task_description.strip():
            self.report({'WARNING'}, "Task description cannot be empty")
            return {'CANCELLED'}

        # Set current task
        props.set_current_task(self.task_description.strip())

        # Switch to Act mode if not already
        if props.interaction_mode != 'act':
            props.interaction_mode = 'act'

        self.report({'INFO'}, f"Started task: {self.task_description}")
        return {'FINISHED'}

class S647_OT_CompleteTask(Operator):
    """Mark current task as complete"""
    bl_idname = "s647.complete_task"
    bl_label = "Complete Task"
    bl_description = "Mark the current task as complete"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647

        if not props.current_task:
            self.report({'WARNING'}, "No active task to complete")
            return {'CANCELLED'}

        completed_task = props.current_task

        # Clear task
        props.current_task = ""
        props.task_progress = 0
        props.current_step = 0
        props.task_steps = ""

        self.report({'INFO'}, f"Task completed: {completed_task}")
        return {'FINISHED'}

class S647_OT_NextStep(Operator):
    """Move to next step in current task"""
    bl_idname = "s647.next_step"
    bl_label = "Next Step"
    bl_description = "Move to the next step in the current task"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647

        if not props.current_task:
            self.report({'WARNING'}, "No active task")
            return {'CANCELLED'}

        steps = props.get_task_steps()
        if not steps:
            self.report({'WARNING'}, "No steps defined for current task")
            return {'CANCELLED'}

        if props.current_step >= len(steps):
            self.report({'INFO'}, "Already at the last step")
            return {'CANCELLED'}

        # Move to next step
        props.current_step += 1

        # Update progress
        progress = int((props.current_step / len(steps)) * 100)
        props.task_progress = progress

        self.report({'INFO'}, f"Moved to step {props.current_step}/{len(steps)}")
        return {'FINISHED'}

class S647_OT_PreviousStep(Operator):
    """Move to previous step in current task"""
    bl_idname = "s647.previous_step"
    bl_label = "Previous Step"
    bl_description = "Move to the previous step in the current task"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647

        if not props.current_task:
            self.report({'WARNING'}, "No active task")
            return {'CANCELLED'}

        if props.current_step <= 1:
            self.report({'INFO'}, "Already at the first step")
            return {'CANCELLED'}

        # Move to previous step
        props.current_step -= 1

        # Update progress
        steps = props.get_task_steps()
        if steps:
            progress = int((props.current_step / len(steps)) * 100)
            props.task_progress = progress

        self.report({'INFO'}, f"Moved to step {props.current_step}")
        return {'FINISHED'}

class S647_OT_CancelTask(Operator):
    """Cancel the current task"""
    bl_idname = "s647.cancel_task"
    bl_label = "Cancel Task"
    bl_description = "Cancel the current task"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        props = context.scene.s647

        if not props.current_task:
            self.report({'WARNING'}, "No active task to cancel")
            return {'CANCELLED'}

        cancelled_task = props.current_task

        # Clear task
        props.current_task = ""
        props.task_progress = 0
        props.current_step = 0
        props.task_steps = ""

        self.report({'INFO'}, f"Task cancelled: {cancelled_task}")
        return {'FINISHED'}

class S647_OT_ApplySuggestion(Operator):
    """Apply a smart suggestion"""
    bl_idname = "s647.apply_suggestion"
    bl_label = "Apply Suggestion"
    bl_description = "Apply the selected smart suggestion"
    bl_options = {'REGISTER'}

    suggestion_text: StringProperty(
        name="Suggestion",
        description="The suggestion prompt to apply",
        default=""
    )

    def execute(self, context):
        props = context.scene.s647

        if not self.suggestion_text:
            self.report({'WARNING'}, "No suggestion text provided")
            return {'CANCELLED'}

        # Set the suggestion as current prompt
        props.current_prompt = self.suggestion_text

        # Trigger AI processing
        bpy.ops.s647.send_prompt()

        self.report({'INFO'}, "Applied suggestion")
        return {'FINISHED'}

class S647_OT_RefreshSuggestions(Operator):
    """Refresh smart suggestions"""
    bl_idname = "s647.refresh_suggestions"
    bl_label = "Refresh Suggestions"
    bl_description = "Refresh the smart suggestions based on current context"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Force UI refresh by updating a property
        props = context.scene.s647
        current_mode = props.interaction_mode
        props.interaction_mode = current_mode  # Trigger refresh

        self.report({'INFO'}, "Suggestions refreshed")
        return {'FINISHED'}

class S647_OT_ToggleSuggestions(Operator):
    """Toggle smart suggestions visibility"""
    bl_idname = "s647.toggle_suggestions"
    bl_label = "Toggle Suggestions"
    bl_description = "Toggle smart suggestions panel visibility"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.s647
        props.show_smart_suggestions = not props.show_smart_suggestions

        status = "enabled" if props.show_smart_suggestions else "disabled"
        self.report({'INFO'}, f"Smart suggestions {status}")
        return {'FINISHED'}

# S647_OT_GenerateContextSuggestions removed - functionality integrated into smart suggestions

# List of all operator classes for registration
classes = [
    S647_OT_SendPrompt,
    S647_OT_ExecuteCode,
    S647_OT_ClearConversation,
    S647_OT_CopyCode,
    S647_OT_SaveConversation,
    # S647_OT_LoadConversation removed - integrated into unified chat
    S647_OT_ToggleAdvanced,
    S647_OT_TestConnection,
    S647_OT_DebugAI,
    S647_OT_TestAIMessage,
    S647_OT_InitializeAI,
    S647_OT_AnalyzeCode,
    S647_OT_SwitchMode,
    # New unified chat operators
    S647_OT_ShowFullHistory,
    S647_OT_ExpandMessage,
    S647_OT_ApplyMessageCode,
    S647_OT_ExplainCode,
    S647_OT_ModifyCode,
    S647_OT_ShowSuggestions,
    S647_OT_ManageContext,
    S647_OT_VoiceInput,
    S647_OT_OpenSettings,
    S647_OT_SaveContext,
    S647_OT_LoadContext,
    S647_OT_ClearContext,
    S647_OT_ExportContext,
    S647_OT_CreateThread,
    S647_OT_SwitchThread,
    S647_OT_RenameThread,
    S647_OT_StartTask,
    S647_OT_CompleteTask,
    S647_OT_NextStep,
    S647_OT_PreviousStep,
    S647_OT_CancelTask,
    S647_OT_ApplySuggestion,
    S647_OT_RefreshSuggestions,
    S647_OT_ToggleSuggestions,
    # S647_OT_GenerateContextSuggestions removed - integrated into smart suggestions
    # MCP Operators
    S647_OT_ManageMCPServers,
    S647_OT_ConnectMCPServer,
    S647_OT_DisconnectMCPServer,
    S647_OT_AddExampleMCPServer,
    S647_OT_ImportMCPConfig,
    S647_OT_LoadMCPConfigFile,
    S647_OT_ExportMCPConfig,
]

class S647_OT_TestAIConfig(Operator):
    """Test AI configuration using AI Config Manager"""
    bl_idname = "s647.test_ai_config"
    bl_label = "Test AI Configuration"
    bl_description = "Test the current AI provider configuration"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from .ai_config_manager import get_ai_config_manager

            config_manager = get_ai_config_manager()

            # Initialize from preferences
            success, message = config_manager.initialize_from_preferences()

            if success:
                # Test connection
                test_success, test_message = config_manager.test_current_provider()

                if test_success:
                    self.report({'INFO'}, f"✓ Configuration test successful: {test_message}")

                    # Show available models
                    models = config_manager.get_available_models()
                    if models:
                        self.report({'INFO'}, f"Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                else:
                    self.report({'ERROR'}, f"✗ Connection test failed: {test_message}")
            else:
                self.report({'ERROR'}, f"✗ Configuration failed: {message}")

        except Exception as e:
            self.report({'ERROR'}, f"Test failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_ReinitializeAI(Operator):
    """Reinitialize AI engine with current settings"""
    bl_idname = "s647.reinitialize_ai"
    bl_label = "Reinitialize AI"
    bl_description = "Reinitialize the AI engine with current preferences"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from . import ai_engine
            from .ai_config_manager import reset_ai_config_manager

            # Reset the config manager
            reset_ai_config_manager()

            # Reinitialize
            ai_engine.initialize()

            if ai_engine.is_available():
                self.report({'INFO'}, "✓ AI engine reinitialized successfully")
            else:
                self.report({'WARNING'}, "AI engine reinitialized but not ready")

        except Exception as e:
            self.report({'ERROR'}, f"Reinitialization failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

class S647_OT_TestMCPIntegration(Operator):
    """Test MCP Integration"""
    bl_idname = "s647.test_mcp_integration"
    bl_label = "Test MCP Integration"
    bl_description = "Run comprehensive tests for MCP integration"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            # Import and run the test module
            import test_mcp_integration

            # Capture test output
            import io
            import sys

            # Redirect stdout to capture test output
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

            try:
                # Run all tests
                success = test_mcp_integration.run_all_tests()

                # Get the output
                test_output = captured_output.getvalue()

            finally:
                # Restore stdout
                sys.stdout = old_stdout

            # Print results to Blender console
            print("S647 MCP Integration Test Results:")
            print("-" * 50)
            print(test_output)

            if success:
                self.report({'INFO'}, "MCP Integration tests passed! Check console for details.")
            else:
                self.report({'WARNING'}, "Some MCP Integration tests failed. Check console for details.")

        except Exception as e:
            error_msg = f"MCP Integration test failed: {str(e)}"
            print(f"S647 Error: {error_msg}")
            self.report({'ERROR'}, error_msg)

        return {'FINISHED'}

# Add new operators to the classes list
classes.extend([
    S647_OT_TestAIConfig,
    S647_OT_ReinitializeAI,
    S647_OT_TestMCPIntegration,
])

def register():
    """Register all operators"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all operators"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
