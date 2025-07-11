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
S647 MCP Configuration Module
=============================

Handles MCP server configuration loading and management.
Supports Claude Desktop compatible JSON format and mcp.json files.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import bpy

class MCPConfigManager:
    """
    Manages MCP server configurations from JSON files
    """
    
    def __init__(self):
        self.addon_dir = Path(__file__).parent
        self.config_file = self.addon_dir / "mcp.json"
        self.default_configs = self._get_default_configs()
    
    def _get_default_configs(self) -> Dict[str, Any]:
        """Get default MCP server configurations"""
        return {
            "mcpServers": {
                "sequential-thinking": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-sequential-thinking"
                    ],
                    "description": "Dynamic and reflective problem-solving through thought sequences",
                    "enabled": True
                }
            }
        }
    
    def load_config_file(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load MCP configuration from JSON file
        
        Args:
            file_path: Path to JSON config file. If None, uses default mcp.json
            
        Returns:
            Dictionary containing MCP server configurations
        """
        if file_path is None:
            file_path = self.config_file
        else:
            file_path = Path(file_path)
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"S647: Loaded MCP config from {file_path}")
                return config
            else:
                print(f"S647: Config file {file_path} not found, using defaults")
                return self.default_configs
                
        except json.JSONDecodeError as e:
            print(f"S647: Error parsing JSON config: {e}")
            return {}
        except Exception as e:
            print(f"S647: Error loading config file: {e}")
            return {}
    
    def save_config_file(self, config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
        """
        Save MCP configuration to JSON file
        
        Args:
            config: Configuration dictionary to save
            file_path: Path to save file. If None, uses default mcp.json
            
        Returns:
            True if successful, False otherwise
        """
        if file_path is None:
            file_path = self.config_file
        else:
            file_path = Path(file_path)
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"S647: Saved MCP config to {file_path}")
            return True
            
        except Exception as e:
            print(f"S647: Error saving config file: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate MCP configuration format
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if mcpServers key exists
        if "mcpServers" not in config:
            result["errors"].append("Missing 'mcpServers' key in configuration")
            result["valid"] = False
            return result
        
        mcp_servers = config["mcpServers"]
        if not isinstance(mcp_servers, dict):
            result["errors"].append("'mcpServers' must be a dictionary")
            result["valid"] = False
            return result
        
        # Validate each server configuration
        for server_name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                result["errors"].append(f"Server '{server_name}' configuration must be a dictionary")
                result["valid"] = False
                continue
            
            # Check required fields
            if "command" not in server_config:
                result["errors"].append(f"Server '{server_name}' missing required 'command' field")
                result["valid"] = False
            
            # Check optional fields
            if "args" in server_config and not isinstance(server_config["args"], list):
                result["errors"].append(f"Server '{server_name}' 'args' must be a list")
                result["valid"] = False
            
            if "env" in server_config and not isinstance(server_config["env"], dict):
                result["errors"].append(f"Server '{server_name}' 'env' must be a dictionary")
                result["valid"] = False
            
            # Warnings for recommended fields
            if "description" not in server_config:
                result["warnings"].append(f"Server '{server_name}' missing recommended 'description' field")
        
        return result
    
    def parse_claude_desktop_config(self, config_text: str) -> Dict[str, Any]:
        """
        Parse Claude Desktop compatible configuration
        
        Args:
            config_text: JSON configuration text
            
        Returns:
            Parsed configuration dictionary
        """
        try:
            config = json.loads(config_text)
            
            # Validate format
            validation = self.validate_config(config)
            if not validation["valid"]:
                print(f"S647: Configuration validation failed: {validation['errors']}")
                return {}
            
            # Add default fields if missing
            if "mcpServers" in config:
                for server_name, server_config in config["mcpServers"].items():
                    # Add enabled flag if not present
                    if "enabled" not in server_config:
                        server_config["enabled"] = True
                    
                    # Add description if not present
                    if "description" not in server_config:
                        server_config["description"] = f"MCP Server: {server_name}"
            
            return config
            
        except json.JSONDecodeError as e:
            print(f"S647: JSON parsing error: {e}")
            return {}
        except Exception as e:
            print(f"S647: Error parsing configuration: {e}")
            return {}
    
    def convert_to_s647_format(self, claude_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert Claude Desktop config format to S647 MCPServerConfig format
        
        Args:
            claude_config: Claude Desktop configuration
            
        Returns:
            List of server configurations for S647
        """
        server_configs = []
        
        if "mcpServers" not in claude_config:
            return server_configs
        
        for server_name, server_config in claude_config["mcpServers"].items():
            s647_config = {
                "name": server_name,
                "command": server_config.get("command", ""),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {}),
                "enabled": server_config.get("enabled", True),
                "description": server_config.get("description", f"MCP Server: {server_name}"),
                "timeout": server_config.get("timeout", 30)
            }
            server_configs.append(s647_config)
        
        return server_configs
    
    def get_example_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get example MCP server configurations"""
        return {
            "Sequential Thinking": {
                "mcpServers": {
                    "sequential-thinking": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
                        "description": "Dynamic problem-solving through thought sequences"
                    }
                }
            },
            "Filesystem": {
                "mcpServers": {
                    "filesystem": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
                        "description": "File system access and manipulation"
                    }
                }
            },
            "Brave Search": {
                "mcpServers": {
                    "brave-search": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                        "env": {
                            "BRAVE_API_KEY": "your_api_key_here"
                        },
                        "description": "Web search using Brave Search API"
                    }
                }
            },
            "SQLite": {
                "mcpServers": {
                    "sqlite": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"],
                        "description": "SQLite database access"
                    }
                }
            }
        }
    
    def load_and_apply_config(self) -> bool:
        """
        Load configuration and apply to MCP client manager
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from . import mcp_client
            
            # Load configuration
            config = self.load_config_file()
            if not config:
                print("S647: No valid configuration found")
                return False
            
            # Convert to S647 format
            server_configs = self.convert_to_s647_format(config)
            if not server_configs:
                print("S647: No server configurations found")
                return False
            
            # Apply to MCP client manager
            manager = mcp_client.get_mcp_manager()
            if not manager:
                print("S647: MCP manager not available")
                return False
            
            success_count = 0
            for server_config in server_configs:
                from .mcp_client import MCPServerConfig
                
                mcp_config = MCPServerConfig(
                    name=server_config["name"],
                    command=server_config["command"],
                    args=server_config["args"],
                    env=server_config["env"],
                    enabled=server_config["enabled"],
                    description=server_config["description"],
                    timeout=server_config["timeout"]
                )
                
                if manager.add_server(mcp_config):
                    success_count += 1
                    print(f"S647: Added server configuration: {server_config['name']}")
            
            print(f"S647: Successfully loaded {success_count}/{len(server_configs)} server configurations")

            # Auto-connect if enabled in preferences
            try:
                from .preferences import get_preferences
                prefs = get_preferences()
                if prefs and prefs.mcp_auto_connect:
                    print("S647: Auto-connecting to MCP servers...")
                    connect_count = 0
                    for server_config in server_configs:
                        if server_config["enabled"]:
                            if manager.connect_server(server_config["name"]):
                                connect_count += 1
                    print(f"S647: Auto-connected to {connect_count}/{len([s for s in server_configs if s['enabled']])} enabled servers")
            except Exception as e:
                print(f"S647: Auto-connect failed: {e}")

            return success_count > 0
            
        except Exception as e:
            print(f"S647: Error loading and applying config: {e}")
            return False


# Global config manager instance
_config_manager: Optional[MCPConfigManager] = None


def get_config_manager() -> MCPConfigManager:
    """Get the global MCP config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = MCPConfigManager()
    return _config_manager


def load_mcp_config() -> bool:
    """Load MCP configuration from file"""
    manager = get_config_manager()
    return manager.load_and_apply_config()


def save_mcp_config(config: Dict[str, Any]) -> bool:
    """Save MCP configuration to file"""
    manager = get_config_manager()
    return manager.save_config_file(config)


def validate_mcp_config(config_text: str) -> Dict[str, Any]:
    """Validate MCP configuration JSON"""
    manager = get_config_manager()
    config = manager.parse_claude_desktop_config(config_text)
    if config:
        return manager.validate_config(config)
    return {"valid": False, "errors": ["Invalid JSON format"], "warnings": []}


def auto_connect_servers() -> int:
    """Auto-connect to all enabled MCP servers"""
    try:
        from . import mcp_client
        from .preferences import get_preferences

        prefs = get_preferences()
        if not prefs or not prefs.mcp_auto_connect:
            print("S647: Auto-connect disabled in preferences")
            return 0

        manager = mcp_client.get_mcp_manager()
        if not manager:
            print("S647: MCP manager not available")
            return 0

        servers = manager.get_all_servers()
        connect_count = 0

        for server_name, config in servers.items():
            if config.enabled:
                print(f"S647: Connecting to {server_name}...")
                if manager.connect_server(server_name):
                    connect_count += 1
                    print(f"S647: Successfully connected to {server_name}")
                else:
                    print(f"S647: Failed to connect to {server_name}")

        print(f"S647: Auto-connected to {connect_count}/{len([s for s in servers.values() if s.enabled])} enabled servers")
        return connect_count

    except Exception as e:
        print(f"S647: Auto-connect error: {e}")
        return 0
