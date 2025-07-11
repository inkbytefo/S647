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
S647 AI Engine Module
=====================

Handles communication with OpenAI API and manages AI interactions.
Provides real-time AI assistance for Blender workflows.
"""

import bpy
import threading
import time
import json
import traceback
from typing import Optional, Dict, Any, List

# Global state - now managed by AI Config Manager
_config_manager = None

# Ensure lib directory is in path for dependencies
try:
    import sys
    import os
    from pathlib import Path

    # Ensure lib directory is in path
    addon_dir = Path(__file__).parent
    lib_dir = addon_dir / "lib"

    print(f"S647 AI Debug: Addon dir: {addon_dir}")
    print(f"S647 AI Debug: Lib dir: {lib_dir}")
    print(f"S647 AI Debug: Lib dir exists: {lib_dir.exists()}")

    if lib_dir.exists():
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
            print(f"S647 AI Debug: Added {lib_dir} to sys.path")
        else:
            print(f"S647 AI Debug: {lib_dir} already in sys.path")

    print("S647: Library path setup complete")
except Exception as e:
    print(f"S647: Library path setup error: {e}")

# Try to import MCP client
try:
    from . import mcp_client
    _mcp_available = True
    print("S647: MCP client module found")
except ImportError as e:
    print(f"S647: MCP client module not found: {e}")
    _mcp_available = False

def initialize():
    """Initialize the AI engine using AI Config Manager"""
    global _config_manager

    print("S647: AI Engine initializing...")

    # Initialize MCP client if available
    if _mcp_available:
        try:
            mcp_client.initialize_mcp()
            print("S647: MCP client initialized")
        except Exception as e:
            print(f"S647: MCP client initialization failed: {e}")

    try:
        # Import and initialize AI Config Manager
        from .ai_config_manager import get_ai_config_manager
        _config_manager = get_ai_config_manager()

        # Initialize from preferences
        success, message = _config_manager.initialize_from_preferences()

        if success:
            print(f"S647: AI Engine initialized successfully - {message}")

            # Initialize MCP if available
            if _mcp_available:
                try:
                    mcp_client.initialize_mcp()
                    print("S647: MCP client initialized")
                except Exception as e:
                    print(f"S647: MCP initialization failed: {e}")
        else:
            print(f"S647: AI Engine initialization failed - {message}")

    except Exception as e:
        print(f"S647: AI Engine initialization failed: {e}")
        print(f"S647: Traceback: {traceback.format_exc()}")
        _config_manager = None

def cleanup():
    """Cleanup AI engine resources"""
    global _config_manager

    print("S647: AI Engine cleaning up...")

    # Cleanup MCP client if available
    if _mcp_available:
        try:
            mcp_client.shutdown_mcp()
            print("S647: MCP client shutdown")
        except Exception as e:
            print(f"S647: MCP client shutdown failed: {e}")

    # Reset config manager
    if _config_manager:
        _config_manager.reset()
    _config_manager = None

def is_available() -> bool:
    """Check if AI engine is available"""
    return _config_manager is not None and _config_manager.is_ready()

def process_prompt_async(prompt: str):
    """
    Process a prompt asynchronously using OpenAI API
    """
    def _process_in_thread():
        try:
            # Get scene properties
            scene = bpy.context.scene
            props = scene.s647

            # Update status
            def set_status(status, message):
                def update():
                    props.ai_status = status
                    props.ai_status_message = message
                bpy.app.timers.register(update, first_interval=0.1)

            set_status('thinking', 'Analyzing Blender context...')

            # Get Blender context
            context_info = get_blender_context_for_ai()

            set_status('thinking', 'Sending request to AI...')

            # Create mode-specific prompt
            mode_specific_prompt = props.get_mode_specific_prompt(prompt)

            # Create AI prompt with context
            full_prompt = create_ai_prompt(mode_specific_prompt, context_info, props.interaction_mode)

            # Make API request
            response_text = _make_api_request(full_prompt, context_info, props.interaction_mode)

            set_status('responding', 'Processing AI response...')

            # Update properties on main thread
            def update_ui():
                props.last_response = response_text
                props.ai_status = 'idle'
                props.ai_status_message = "Ready"

                # Debug: Log response length
                print(f"S647: AI response length: {len(response_text)} characters")

                # Add assistant message with current thread
                from . import utils
                has_code = bool(utils.extract_python_code(response_text))
                props.add_message('assistant', response_text, has_code=has_code,
                                thread_id=props.current_thread_id, intent_type='response')

                # Debug: Verify message was saved correctly
                if props.conversation_history:
                    last_msg = props.conversation_history[-1]
                    print(f"S647: Saved message length: {len(last_msg.content)} characters")
                    if len(last_msg.content) != len(response_text):
                        print(f"S647: WARNING - Message truncated during save!")
                        print(f"S647: Original: {len(response_text)}, Saved: {len(last_msg.content)}")

                props.successful_requests += 1
                props.total_requests += 1

                # Extract and set pending code
                from . import utils
                code_blocks = utils.extract_python_code(response_text)
                if code_blocks:
                    props.pending_code = code_blocks[0][0]  # First code block

                # Handle mode-specific post-processing
                if props.interaction_mode == 'act':
                    _handle_act_mode_response(props, response_text)
                elif props.interaction_mode == 'chat':
                    _handle_chat_mode_response(props, response_text)

            # Schedule UI update on main thread
            bpy.app.timers.register(update_ui, first_interval=0.1)

        except Exception as e:
            # Capture exception information immediately
            error_message = str(e)
            error_traceback = traceback.format_exc()

            def update_error():
                props = bpy.context.scene.s647
                props.ai_status = 'error'
                props.ai_status_message = f"Error: {error_message}"
                props.total_requests += 1
                print(f"S647: AI processing error: {error_message}")
                print(f"S647: Traceback: {error_traceback}")

            bpy.app.timers.register(update_error, first_interval=0.1)

    # Start processing in background thread
    thread = threading.Thread(target=_process_in_thread)
    thread.daemon = True
    thread.start()

def get_blender_context_for_ai() -> Dict[str, Any]:
    """
    Get Blender context information for AI processing

    This will be expanded when implementing the full AI integration.
    """
    from . import utils

    try:
        # Safely get scene and properties
        scene = getattr(bpy.context, 'scene', None)
        if not scene:
            print("S647: Warning - No scene available in context")
            return {
                "error": "No scene available",
                "blender_version": bpy.app.version_string,
                "scene_name": "No Scene",
                "mode": "UNKNOWN",
                "active_object": None,
                "selected_objects": [],
                "total_objects": 0
            }

        props = getattr(scene, 's647', None)
        if not props:
            print("S647: Warning - S647 properties not available")
            # Use default context mode
            context_mode = 'standard'
        else:
            context_mode = getattr(props, 'context_mode', 'standard')

        context_info = utils.get_blender_context_info(context_mode)

        # Add conversation history if props available
        if props:
            try:
                context_info['conversation_history'] = props.get_conversation_context()
            except Exception as e:
                print(f"S647: Error getting conversation context: {e}")
                context_info['conversation_history'] = []

        # Add MCP resources if available
        if _mcp_available:
            try:
                manager = mcp_client.get_mcp_manager()
                if manager:
                    resources = manager.get_all_resources()
                    if resources:
                        context_info['mcp_resources'] = {
                            key: {
                                'name': resource.name,
                                'description': resource.description,
                                'uri': resource.uri,
                                'server': resource.server_name
                            } for key, resource in resources.items()
                        }
                        print(f"S647: Added {len(resources)} MCP resources to context")
            except Exception as e:
                print(f"S647: Error getting MCP resources: {e}")

        return context_info
    except Exception as e:
        print(f"S647: Error getting Blender context: {e}")
        import traceback
        print(f"S647: Traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "blender_version": bpy.app.version_string,
            "scene_name": "Error",
            "mode": "UNKNOWN",
            "active_object": None,
            "selected_objects": [],
            "total_objects": 0
        }

def create_ai_prompt(user_prompt: str, context_info: Dict[str, Any], interaction_mode: str = 'chat') -> str:
    """
    Create a complete prompt for the AI including system instructions and context
    """
    try:
        from .prompts import PromptManager

        # Get system prompt with context using centralized system
        return PromptManager.get_system_prompt(
            mode=interaction_mode,
            context=context_info,
            user_request=user_prompt
        )
    except ImportError:
        # Fallback to legacy method
        return _create_legacy_ai_prompt(user_prompt, context_info, interaction_mode)


def _create_legacy_ai_prompt(user_prompt: str, context_info: Dict[str, Any], interaction_mode: str = 'chat') -> str:
    """Legacy AI prompt creation (fallback)"""
    from . import utils

    # Get mode-specific system prompt
    system_prompt = utils.create_system_prompt(interaction_mode)

    # Format context information
    context_text = f"""
Current Blender Context:
- Scene: {context_info.get('scene_name', 'Unknown')}
- Mode: {context_info.get('mode', 'Unknown')}
- Active Object: {context_info.get('active_object', {}).get('name', 'None') if context_info.get('active_object') else 'None'}
- Selected Objects: {', '.join(context_info.get('selected_objects', [])) or 'None'}
- Total Objects: {context_info.get('total_objects', 0)}
"""

    full_prompt = f"{system_prompt}\n\n{context_text}\n\nUser Request: {user_prompt}"

    return full_prompt


def _create_mode_specific_system_prompt(interaction_mode: str) -> str:
    """Create system prompt based on interaction mode"""
    from . import utils

    # Use the updated create_system_prompt with mode support
    return utils.create_system_prompt(interaction_mode)

def _handle_act_mode_response(props, response_text: str):
    """Handle Act mode specific response processing"""
    import json
    import re

    # Try to extract task breakdown from response
    task_pattern = r'(?:TASK|STEPS?):\s*(.*?)(?:\n\n|\Z)'
    task_match = re.search(task_pattern, response_text, re.IGNORECASE | re.DOTALL)

    if task_match:
        task_description = task_match.group(1).strip()
        props.set_current_task(task_description)

        # Try to extract numbered steps
        steps_pattern = r'(\d+\..*?)(?=\d+\.|$)'
        steps = re.findall(steps_pattern, response_text, re.MULTILINE)

        if steps:
            clean_steps = [step.strip() for step in steps]
            props.set_current_task(task_description, clean_steps)
            props.update_task_progress(0, 1)  # Start with first step

    # AUTO-EXECUTE CODE IN ACT MODE
    # In Act mode, automatically execute safe code blocks
    from . import utils
    from .preferences import get_preferences

    prefs = get_preferences()
    print(f"S647: Act mode auto-execute check - Code execution enabled: {prefs.enable_code_execution}")

    if prefs.enable_code_execution:
        code_blocks = utils.extract_python_code(response_text)
        print(f"S647: Found {len(code_blocks)} code blocks in response")

        if code_blocks:
            # Get the first code block
            code, _, _ = code_blocks[0]
            print(f"S647: First code block: {code}")

            # Check if code is safe for auto-execution
            is_safe, warnings = utils.is_safe_code(code)
            print(f"S647: Code safety check - Safe: {is_safe}, Warnings: {warnings}")

            if is_safe:
                # Auto-execute the code in Act mode
                try:
                    from . import code_executor
                    print("S647: About to execute code in Act mode...")
                    print(f"S647: Code to execute: '{code}'")

                    result = code_executor.execute_code(code)
                    print(f"S647: Code execution result: '{result}'")

                    # Update execution result
                    props.code_execution_result = f"Auto-executed: {result}"
                    props.pending_code = ""  # Clear pending code since it's executed
                    props.code_executions += 1

                    # Mark the last message as executed
                    if props.conversation_history:
                        last_msg = props.conversation_history[-1]
                        if last_msg.role == 'assistant' and last_msg.has_code:
                            last_msg.code_executed = True

                    print(f"S647: Auto-executed code in Act mode: {result}")

                except Exception as e:
                    print(f"S647: Auto-execution failed: {str(e)}")
                    import traceback
                    print(f"S647: Traceback: {traceback.format_exc()}")
                    # Keep code as pending if auto-execution fails
                    props.pending_code = code
            else:
                # Code is not safe for auto-execution, keep as pending
                props.pending_code = code
                print(f"S647: Code not auto-executed due to safety concerns: {warnings}")
        else:
            print("S647: No code blocks found in response")
    else:
        print("S647: Code execution disabled in preferences")

def _handle_chat_mode_response(props, response_text: str):
    """Handle Chat mode specific response processing"""
    # In chat mode, we might want to extract learning points or topics
    # For now, just update session context with key topics

    # Simple keyword extraction for context building
    keywords = _extract_keywords(response_text)
    if keywords:
        current_context = props.session_context
        new_context = f"{current_context}\nDiscussed: {', '.join(keywords)}" if current_context else f"Discussed: {', '.join(keywords)}"
        props.session_context = new_context[:1000]  # Limit context size

    # MANUAL CODE EXECUTION IN CHAT MODE
    # In Chat mode, codes are NOT auto-executed, they remain as pending
    # This allows users to review and understand the code before execution
    from . import utils

    code_blocks = utils.extract_python_code(response_text)
    if code_blocks:
        # Keep code as pending for manual execution
        code, _, _ = code_blocks[0]
        props.pending_code = code
        print(f"S647: Code available for manual execution in Chat mode")

def _extract_keywords(text: str) -> list:
    """Extract key Blender-related terms from text"""
    blender_terms = [
        'object', 'mesh', 'material', 'texture', 'modifier', 'animation',
        'keyframe', 'render', 'shader', 'node', 'vertex', 'edge', 'face',
        'camera', 'light', 'scene', 'collection', 'armature', 'bone'
    ]

    found_terms = []
    text_lower = text.lower()

    for term in blender_terms:
        if term in text_lower:
            found_terms.append(term)

    return found_terms[:5]  # Return max 5 terms

def _make_api_request(prompt: str, context: Dict[str, Any], interaction_mode: str = 'chat') -> str:
    """Make API request using AI Config Manager"""
    global _config_manager

    if not _config_manager or not _config_manager.is_ready():
        raise Exception("AI client not initialized")

    ai_client = _config_manager.get_client()
    if not ai_client:
        raise Exception("AI client not available")

    try:
        from .preferences import get_preferences
        prefs = get_preferences()

        # Prepare conversation history
        messages = []

        # Add system message
        system_message = {
            "role": "system",
            "content": _create_system_message(context)
        }
        messages.append(system_message)

        # Add conversation history (last 10 messages to stay within token limits)
        conversation_history = context.get('conversation_history', [])

        # Get available MCP tools
        mcp_tools = []
        if _mcp_available:
            try:
                available_tools = mcp_client.get_mcp_tools()
                for tool_key, tool in available_tools.items():
                    mcp_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": f"[MCP:{tool.server_name}] {tool.description}",
                            "parameters": tool.input_schema
                        }
                    })
                print(f"S647: Found {len(mcp_tools)} MCP tools available")
            except Exception as e:
                print(f"S647: Error getting MCP tools: {e}")
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        messages.extend(recent_history)

        # Add current user message
        messages.append({
            "role": "user",
            "content": prompt
        })

        # Determine model based on provider type
        if prefs.provider_type == 'openai':
            model = prefs.api_model
        elif prefs.provider_type == 'custom':
            model = prefs.custom_model
        else:
            raise Exception(f"Unknown provider type: {prefs.provider_type}")

        # Prepare API call parameters
        api_params = {
            "model": model,
            "messages": messages,
            "max_tokens": prefs.max_tokens,
            "temperature": prefs.temperature,
            "stream": False
        }

        # Add tools if available
        if mcp_tools:
            api_params["tools"] = mcp_tools
            api_params["tool_choice"] = "auto"

        # Make API call
        response = ai_client.chat.completions.create(**api_params)

        # Handle tool calls if present
        message = response.choices[0].message
        if hasattr(message, 'tool_calls') and message.tool_calls:
            return _handle_tool_calls(message, messages, api_params)

        return message.content

    except Exception as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")

def _handle_tool_calls(message, messages, api_params) -> str:
    """Handle MCP tool calls from AI response"""
    if not _mcp_available:
        return "MCP tools not available"

    # Get AI client from config manager
    global _config_manager
    if not _config_manager or not _config_manager.is_ready():
        return "AI client not available"

    ai_client = _config_manager.get_client()
    if not ai_client:
        return "AI client not available"

    try:
        # Add the assistant's message with tool calls
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                } for tool_call in message.tool_calls
            ]
        })

        # Execute each tool call
        tool_results = []
        for tool_call in message.tool_calls:
            try:
                # Parse arguments
                import json
                arguments = json.loads(tool_call.function.arguments)

                # Call MCP tool - bypass user confirmation for AI calls
                result = mcp_client.call_mcp_tool(tool_call.function.name, arguments, user_confirmation=False)

                if result and result.get("success"):
                    content = result.get("content", [])
                    if isinstance(content, list):
                        content_text = "\n".join(str(item) for item in content)
                    else:
                        content_text = str(content)

                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": content_text
                    })
                else:
                    error_msg = result.get("error", "Tool execution failed") if result else "No result"
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": f"Error: {error_msg}"
                    })

            except Exception as e:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": f"Error executing tool: {str(e)}"
                })

        # Add tool results to messages
        messages.extend(tool_results)

        # Get final response from AI
        final_response = ai_client.chat.completions.create(**api_params)
        return final_response.choices[0].message.content

    except Exception as e:
        print(f"S647: Error handling tool calls: {e}")
        return f"Error processing tool calls: {str(e)}"

def _create_system_message(context: Dict[str, Any]) -> str:
    """Create system message with Blender context and safety guidelines"""
    from . import utils

    base_prompt = utils.create_system_prompt()

    # Add current context information
    context_text = f"""
Current Blender Session:
- Blender Version: {context.get('blender_version', 'Unknown')}
- Scene: {context.get('scene_name', 'Unknown')}
- Mode: {context.get('mode', 'Unknown')}
- Active Object: {context.get('active_object', {}).get('name', 'None') if context.get('active_object') else 'None'}
- Selected Objects: {', '.join(context.get('selected_objects', [])) or 'None'}
- Total Objects: {context.get('total_objects', 0)}
- Current Frame: {context.get('current_frame', 1)}
"""

    # Add MCP resources information if available
    mcp_resources = context.get('mcp_resources', {})
    if mcp_resources:
        context_text += f"\nAvailable MCP Resources ({len(mcp_resources)}):\n"
        for key, resource in list(mcp_resources.items())[:5]:  # Show first 5
            context_text += f"- {resource['name']}: {resource['description']} (Server: {resource['server']})\n"
        if len(mcp_resources) > 5:
            context_text += f"... and {len(mcp_resources) - 5} more resources\n"

    # Add object details if available
    if context.get('active_object'):
        obj_info = context['active_object']
        context_text += f"""
Active Object Details:
- Type: {obj_info.get('type', 'Unknown')}
- Location: {obj_info.get('location', [0, 0, 0])}
- Rotation: {obj_info.get('rotation', [0, 0, 0])}
- Scale: {obj_info.get('scale', [1, 1, 1])}
"""

    # Add safety guidelines for code generation
    safety_guidelines = """
IMPORTANT SAFETY GUIDELINES FOR CODE GENERATION:
🔒 SECURITY REQUIREMENTS:
- Never use file system operations (open, read, write files)
- Avoid system modules (os, sys, subprocess)
- Don't use network operations (urllib, requests, socket)
- Avoid destructive operations without clear user intent
- Use only Blender-safe modules: bpy, bmesh, mathutils, bpy_extras

⚠️ BLENDER SAFETY:
- Prefer non-destructive operations when possible
- Always check if objects exist before operating on them
- Use try/except blocks for error handling
- Avoid bpy.ops.wm.quit, bpy.ops.wm.save without explicit request
- Be cautious with bpy.data.*.remove() operations

✅ RECOMMENDED PRACTICES:
- Use bpy.context.active_object and bpy.context.selected_objects
- Validate object types before operations
- Include helpful comments in generated code
- Prefer bpy.data operations over bpy.ops when possible
- Use mathutils for vector/matrix operations
"""

    return f"{base_prompt}\n{context_text}\n{safety_guidelines}"

def get_api_status() -> Dict[str, Any]:
    """Get current API status and statistics"""
    if not _config_manager:
        return {
            "initialized": False,
            "openai_available": False,
            "client_ready": False,
        }

    status = _config_manager.get_provider_status()
    return {
        "initialized": _config_manager.is_ready(),
        "openai_available": True,  # If we have a config manager, dependencies are available
        "client_ready": _config_manager.get_client() is not None,
        "provider_status": status.status.value if status else 'unknown',
        "provider_message": status.message if status else 'No provider'
    }

def test_api_connection() -> tuple[bool, str]:
    """Test API connection with a simple request"""
    if not _config_manager:
        return False, "AI engine not initialized"

    return _config_manager.test_current_provider()



def send_simple_test_message() -> tuple[bool, str]:
    """Send a simple test message to verify AI functionality"""
    if not _config_manager or not _config_manager.is_ready():
        return False, "AI engine not initialized"

    try:
        # Create a simple test prompt
        test_prompt = "Hello! Please respond with 'AI is working correctly' to confirm the connection."

        # Get basic context
        context_info = {
            'scene_name': 'Test Scene',
            'mode': 'OBJECT',
            'active_object': None,
            'selected_objects': [],
            'total_objects': 0
        }

        # Make API request
        response = _make_api_request(test_prompt, context_info, 'chat')

        return True, f"AI Response: {response}"

    except Exception as e:
        return False, f"Test message failed: {str(e)}"
