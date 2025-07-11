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
S647 MCP Client Module
======================

Manages Model Context Protocol (MCP) server connections and integrations.
Provides a bridge between S647's AI engine and external MCP servers.
"""

import asyncio
import json
import threading
import traceback
from typing import Dict, List, Optional, Any, Callable
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from enum import Enum

import bpy

try:
    # Ensure lib directory is in path for MCP imports
    import sys
    from pathlib import Path

    addon_dir = Path(__file__).parent
    lib_dir = addon_dir / "lib"

    print(f"S647 Debug: Addon dir: {addon_dir}")
    print(f"S647 Debug: Lib dir: {lib_dir}")
    print(f"S647 Debug: Lib dir exists: {lib_dir.exists()}")

    if lib_dir.exists():
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
            print(f"S647 Debug: Added {lib_dir} to sys.path")
        else:
            print(f"S647 Debug: {lib_dir} already in sys.path")

        # List contents of lib directory
        try:
            lib_contents = list(lib_dir.iterdir())
            print(f"S647 Debug: Lib directory contents: {[p.name for p in lib_contents]}")
        except Exception as e:
            print(f"S647 Debug: Error listing lib contents: {e}")

    # Try importing MCP with specific error handling for Windows
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        MCP_AVAILABLE = True
        print("S647: MCP SDK loaded successfully")
    except ImportError as mcp_error:
        # Check if it's a Windows-specific issue
        if "pywintypes" in str(mcp_error):
            print("S647: MCP SDK requires Windows-specific dependencies")
            print("S647: Install with: pip install pywin32")
        MCP_AVAILABLE = False
        print(f"S647: MCP SDK not available: {mcp_error}")
        print(f"S647 Debug: Current sys.path: {sys.path[:5]}...")  # Show first 5 paths

        # Define fallback classes when MCP is not available
        class ClientSession:
            pass

        class StdioServerParameters:
            pass

        stdio_client = None

except Exception as e:
    MCP_AVAILABLE = False
    print(f"S647: MCP SDK error: {e}")
    print(f"S647 Debug: Current sys.path: {sys.path[:5]}...")  # Show first 5 paths
    print("S647: Install with: pip install mcp")

    # Define fallback classes when MCP is not available
    class ClientSession:
        pass

    class StdioServerParameters:
        pass

    stdio_client = None


class MCPServerStatus(Enum):
    """MCP Server connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    enabled: bool = True
    timeout: int = 30
    description: str = ""


@dataclass
class MCPTool:
    """Represents an MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    server_name: str = ""


class MCPClientManager:
    """
    Manages multiple MCP server connections and provides unified access to tools and resources
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.sessions: Dict[str, "ClientSession"] = {}
        self.server_status: Dict[str, MCPServerStatus] = {}
        self.available_tools: Dict[str, MCPTool] = {}
        self.available_resources: Dict[str, MCPResource] = {}
        self.exit_stacks: Dict[str, AsyncExitStack] = {}
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.loop_thread: Optional[threading.Thread] = None
        self._callbacks: Dict[str, List[Callable]] = {
            'server_connected': [],
            'server_disconnected': [],
            'tool_discovered': [],
            'resource_discovered': [],
        }
        
        # Start async event loop in background thread
        self._start_event_loop()
    
    def _start_event_loop(self):
        """Start the async event loop in a background thread"""
        def run_loop():
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
    
    def add_server(self, config: MCPServerConfig) -> bool:
        """Add a new MCP server configuration"""
        try:
            self.servers[config.name] = config
            self.server_status[config.name] = MCPServerStatus.DISCONNECTED
            print(f"S647: Added MCP server configuration: {config.name}")
            return True
        except Exception as e:
            print(f"S647: Error adding MCP server {config.name}: {e}")
            return False
    
    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server configuration"""
        try:
            if server_name in self.sessions:
                self.disconnect_server(server_name)
            
            self.servers.pop(server_name, None)
            self.server_status.pop(server_name, None)
            
            # Remove tools and resources from this server
            self.available_tools = {k: v for k, v in self.available_tools.items() 
                                  if v.server_name != server_name}
            self.available_resources = {k: v for k, v in self.available_resources.items() 
                                      if v.server_name != server_name}
            
            print(f"S647: Removed MCP server: {server_name}")
            return True
        except Exception as e:
            print(f"S647: Error removing MCP server {server_name}: {e}")
            return False
    
    def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server"""
        if not MCP_AVAILABLE:
            print("S647: MCP SDK not available")
            return False
        
        if server_name not in self.servers:
            print(f"S647: Server {server_name} not configured")
            return False
        
        config = self.servers[server_name]
        if not config.enabled:
            print(f"S647: Server {server_name} is disabled")
            return False
        
        # Run connection in async event loop
        future = asyncio.run_coroutine_threadsafe(
            self._connect_server_async(server_name, config), 
            self.event_loop
        )
        
        try:
            return future.result(timeout=config.timeout)
        except Exception as e:
            print(f"S647: Error connecting to {server_name}: {e}")
            self.server_status[server_name] = MCPServerStatus.ERROR
            return False
    
    async def _connect_server_async(self, server_name: str, config: MCPServerConfig) -> bool:
        """Async implementation of server connection"""
        try:
            self.server_status[server_name] = MCPServerStatus.CONNECTING
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env
            )
            
            # Create exit stack for resource management
            exit_stack = AsyncExitStack()
            self.exit_stacks[server_name] = exit_stack
            
            # Connect to server
            stdio_transport = await exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            stdio, write = stdio_transport
            
            # Create session
            session = await exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )
            
            # Initialize session
            await session.initialize()
            
            # Store session
            self.sessions[server_name] = session
            self.server_status[server_name] = MCPServerStatus.CONNECTED
            
            # Discover tools and resources
            await self._discover_server_capabilities(server_name, session)
            
            # Notify callbacks
            self._notify_callbacks('server_connected', server_name)
            
            print(f"S647: Successfully connected to MCP server: {server_name}")
            return True
            
        except Exception as e:
            print(f"S647: Failed to connect to {server_name}: {e}")
            print(f"S647: Traceback: {traceback.format_exc()}")
            self.server_status[server_name] = MCPServerStatus.ERROR
            return False
    
    async def _discover_server_capabilities(self, server_name: str, session: "ClientSession"):
        """Discover tools and resources from a connected server"""
        try:
            # Discover tools
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                mcp_tool = MCPTool(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema,
                    server_name=server_name
                )
                tool_key = f"{server_name}.{tool.name}"
                self.available_tools[tool_key] = mcp_tool
                self._notify_callbacks('tool_discovered', mcp_tool)
            
            print(f"S647: Discovered {len(tools_response.tools)} tools from {server_name}")
            
            # Discover resources
            try:
                resources_response = await session.list_resources()
                for resource in resources_response.resources:
                    mcp_resource = MCPResource(
                        uri=resource.uri,
                        name=resource.name or resource.uri,
                        description=resource.description or "",
                        mime_type=getattr(resource, 'mimeType', None),
                        server_name=server_name
                    )
                    resource_key = f"{server_name}.{resource.uri}"
                    self.available_resources[resource_key] = mcp_resource
                    self._notify_callbacks('resource_discovered', mcp_resource)
                
                print(f"S647: Discovered {len(resources_response.resources)} resources from {server_name}")
            except Exception as e:
                print(f"S647: No resources available from {server_name}: {e}")
                
        except Exception as e:
            print(f"S647: Error discovering capabilities from {server_name}: {e}")
    
    def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        try:
            if server_name in self.exit_stacks:
                # Run disconnection in async event loop
                future = asyncio.run_coroutine_threadsafe(
                    self._disconnect_server_async(server_name), 
                    self.event_loop
                )
                future.result(timeout=10)
            
            # Clean up
            self.sessions.pop(server_name, None)
            self.exit_stacks.pop(server_name, None)
            self.server_status[server_name] = MCPServerStatus.DISCONNECTED
            
            # Remove tools and resources from this server
            self.available_tools = {k: v for k, v in self.available_tools.items() 
                                  if v.server_name != server_name}
            self.available_resources = {k: v for k, v in self.available_resources.items() 
                                      if v.server_name != server_name}
            
            # Notify callbacks
            self._notify_callbacks('server_disconnected', server_name)
            
            print(f"S647: Disconnected from MCP server: {server_name}")
            return True
            
        except Exception as e:
            print(f"S647: Error disconnecting from {server_name}: {e}")
            return False
    
    async def _disconnect_server_async(self, server_name: str):
        """Async implementation of server disconnection"""
        if server_name in self.exit_stacks:
            await self.exit_stacks[server_name].aclose()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any],
                  user_confirmation: bool = False) -> Optional[Dict[str, Any]]:
        """Call an MCP tool with security checks"""
        if not MCP_AVAILABLE:
            return {"error": "MCP SDK not available"}

        # Security check: Validate tool name
        if not self._is_safe_tool_name(tool_name):
            return {"error": f"Tool name '{tool_name}' contains unsafe characters"}

        # Find the tool
        tool = None
        server_name = None
        for key, mcp_tool in self.available_tools.items():
            if mcp_tool.name == tool_name or key == tool_name:
                tool = mcp_tool
                server_name = mcp_tool.server_name
                break

        if not tool or not server_name:
            return {"error": f"Tool {tool_name} not found"}

        if server_name not in self.sessions:
            return {"error": f"Server {server_name} not connected"}

        # Security check: Validate arguments
        validation_result = self._validate_tool_arguments(tool, arguments)
        if not validation_result["valid"]:
            return {"error": f"Invalid arguments: {validation_result['error']}"}

        # Check if user confirmation is required
        from .preferences import get_preferences
        prefs = get_preferences()
        if prefs.mcp_tool_confirmation and not user_confirmation:
            return {
                "error": "User confirmation required",
                "requires_confirmation": True,
                "tool_info": {
                    "name": tool.name,
                    "description": tool.description,
                    "server": server_name,
                    "arguments": arguments
                }
            }

        # Log tool call for security audit
        print(f"S647: MCP Tool Call - {tool.name} on {server_name} with args: {arguments}")

        # Run tool call in async event loop
        future = asyncio.run_coroutine_threadsafe(
            self._call_tool_async(server_name, tool.name, arguments),
            self.event_loop
        )

        try:
            return future.result(timeout=30)
        except Exception as e:
            print(f"S647: MCP Tool call error: {e}")
            return {"error": f"Tool call failed: {str(e)}"}

    async def _call_tool_async(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation of tool calling"""
        try:
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments)

            # Convert result to dict
            return {
                "success": True,
                "content": result.content,
                "isError": result.isError if hasattr(result, 'isError') else False
            }

        except Exception as e:
            print(f"S647: Error calling tool {tool_name}: {e}")
            return {"error": str(e)}

    def get_resource(self, resource_uri: str) -> Optional[Dict[str, Any]]:
        """Get content of an MCP resource"""
        if not MCP_AVAILABLE:
            return {"error": "MCP SDK not available"}

        # Find the resource
        resource = None
        server_name = None
        for key, mcp_resource in self.available_resources.items():
            if mcp_resource.uri == resource_uri or key == resource_uri:
                resource = mcp_resource
                server_name = mcp_resource.server_name
                break

        if not resource or not server_name:
            return {"error": f"Resource {resource_uri} not found"}

        if server_name not in self.sessions:
            return {"error": f"Server {server_name} not connected"}

        # Run resource read in async event loop
        future = asyncio.run_coroutine_threadsafe(
            self._get_resource_async(server_name, resource.uri),
            self.event_loop
        )

        try:
            return future.result(timeout=30)
        except Exception as e:
            return {"error": f"Resource read failed: {str(e)}"}

    async def _get_resource_async(self, server_name: str, resource_uri: str) -> Dict[str, Any]:
        """Async implementation of resource reading"""
        try:
            session = self.sessions[server_name]
            result = await session.read_resource(resource_uri)

            return {
                "success": True,
                "contents": result.contents
            }

        except Exception as e:
            print(f"S647: Error reading resource {resource_uri}: {e}")
            return {"error": str(e)}

    def get_server_status(self, server_name: str) -> MCPServerStatus:
        """Get the status of an MCP server"""
        return self.server_status.get(server_name, MCPServerStatus.DISCONNECTED)

    def get_all_servers(self) -> Dict[str, MCPServerConfig]:
        """Get all configured servers"""
        return self.servers.copy()

    def get_all_tools(self) -> Dict[str, MCPTool]:
        """Get all available tools from all connected servers"""
        return self.available_tools.copy()

    def get_all_resources(self) -> Dict[str, MCPResource]:
        """Get all available resources from all connected servers"""
        return self.available_resources.copy()

    def add_callback(self, event_type: str, callback: Callable):
        """Add a callback for MCP events"""
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)

    def remove_callback(self, event_type: str, callback: Callable):
        """Remove a callback for MCP events"""
        if event_type in self._callbacks and callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)

    def _notify_callbacks(self, event_type: str, data: Any):
        """Notify all callbacks for an event type"""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"S647: Error in MCP callback: {e}")

    def _is_safe_tool_name(self, tool_name: str) -> bool:
        """Check if tool name is safe (no injection attempts)"""
        import re
        # Allow only alphanumeric, underscore, hyphen, and dot
        safe_pattern = re.compile(r'^[a-zA-Z0-9_.-]+$')
        return bool(safe_pattern.match(tool_name)) and len(tool_name) <= 100

    def _validate_tool_arguments(self, tool: MCPTool, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool arguments against schema"""
        try:
            # Basic validation - check for required fields
            schema = tool.input_schema
            required_fields = schema.get('required', [])

            # Check required fields are present
            for field in required_fields:
                if field not in arguments:
                    return {
                        "valid": False,
                        "error": f"Required field '{field}' missing"
                    }

            # Check for dangerous patterns in string arguments
            for key, value in arguments.items():
                if isinstance(value, str):
                    if self._contains_dangerous_patterns(value):
                        return {
                            "valid": False,
                            "error": f"Argument '{key}' contains potentially dangerous content"
                        }

            return {"valid": True}

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    def _contains_dangerous_patterns(self, text: str) -> bool:
        """Check if text contains potentially dangerous patterns"""
        dangerous_patterns = [
            r'__import__',
            r'exec\s*\(',
            r'eval\s*\(',
            r'subprocess',
            r'os\.system',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
        ]

        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def shutdown(self):
        """Shutdown the MCP client manager"""
        try:
            # Disconnect all servers
            for server_name in list(self.sessions.keys()):
                self.disconnect_server(server_name)

            # Stop event loop
            if self.event_loop and not self.event_loop.is_closed():
                self.event_loop.call_soon_threadsafe(self.event_loop.stop)

            print("S647: MCP Client Manager shutdown complete")

        except Exception as e:
            print(f"S647: Error during MCP shutdown: {e}")


# Global MCP client manager instance
_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> Optional[MCPClientManager]:
    """Get the global MCP client manager instance"""
    global _mcp_manager
    if _mcp_manager is None and MCP_AVAILABLE:
        _mcp_manager = MCPClientManager()
    return _mcp_manager


def initialize_mcp():
    """Initialize the MCP client system"""
    global _mcp_manager
    if MCP_AVAILABLE and _mcp_manager is None:
        _mcp_manager = MCPClientManager()
        print("S647: MCP Client Manager initialized")

        # Load configuration from mcp.json
        try:
            from . import mcp_config
            success = mcp_config.load_mcp_config()
            if success:
                print("S647: MCP configuration loaded from mcp.json")
            else:
                print("S647: No MCP configuration found, using defaults")
        except Exception as e:
            print(f"S647: Error loading MCP configuration: {e}")

        return True
    return False


def shutdown_mcp():
    """Shutdown the MCP client system"""
    global _mcp_manager
    if _mcp_manager:
        _mcp_manager.shutdown()
        _mcp_manager = None
        print("S647: MCP Client Manager shutdown")


def is_mcp_available() -> bool:
    """Check if MCP is available"""
    return MCP_AVAILABLE


# Utility functions for easy access
def add_mcp_server(name: str, command: str, args: List[str] = None, env: Dict[str, str] = None,
                   description: str = "") -> bool:
    """Add an MCP server configuration"""
    manager = get_mcp_manager()
    if manager:
        config = MCPServerConfig(
            name=name,
            command=command,
            args=args or [],
            env=env,
            description=description
        )
        return manager.add_server(config)
    return False


def connect_mcp_server(server_name: str) -> bool:
    """Connect to an MCP server"""
    manager = get_mcp_manager()
    return manager.connect_server(server_name) if manager else False


def disconnect_mcp_server(server_name: str) -> bool:
    """Disconnect from an MCP server"""
    manager = get_mcp_manager()
    return manager.disconnect_server(server_name) if manager else False


def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Call an MCP tool"""
    manager = get_mcp_manager()
    return manager.call_tool(tool_name, arguments) if manager else None


def get_mcp_tools() -> Dict[str, MCPTool]:
    """Get all available MCP tools"""
    manager = get_mcp_manager()
    return manager.get_all_tools() if manager else {}


def get_mcp_resources() -> Dict[str, MCPResource]:
    """Get all available MCP resources"""
    manager = get_mcp_manager()
    return manager.get_all_resources() if manager else {}
