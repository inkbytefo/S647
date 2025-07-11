# S647 Model Context Protocol (MCP) Integration Guide

## 🎯 Overview

S647 now includes comprehensive Model Context Protocol (MCP) integration, allowing your Blender AI assistant to connect to external MCP servers and access their tools and resources. This opens up unlimited possibilities for extending S647's capabilities.

## 🚀 What is MCP?

Model Context Protocol (MCP) is an open protocol developed by Anthropic that standardizes how AI applications connect to external data sources and tools. Think of it as a "USB-C port for AI applications" - it provides a standardized way to connect AI models to different services and capabilities.

### Key Benefits:
- **Extensibility**: Connect to any MCP-compatible server
- **Standardization**: Use the same protocol across different AI applications
- **Security**: Built-in security controls and user consent mechanisms
- **Flexibility**: Support for tools, resources, and prompts

## 🛠️ Installation and Setup

### Prerequisites

1. **Install MCP SDK**:
   ```bash
   pip install mcp>=1.0.0
   ```

2. **Enable MCP in S647**:
   - Open Blender Preferences (Edit → Preferences)
   - Go to Add-ons → S647
   - Check "Enable MCP Integration"
   - Optionally enable "Auto-connect MCP Servers"

### Verification

Run the MCP integration test:
```python
# In Blender's Python console
import sys
sys.path.append("path/to/s647/addon")
from s647 import test_mcp_integration
test_mcp_integration.run_all_tests()
```

## 📋 MCP Server Management

### Adding MCP Servers

#### Method 1: JSON Import (Recommended)
1. Open Blender Preferences → Add-ons → S647
2. Expand "Model Context Protocol (MCP)" section
3. Click "Import JSON Config"
4. Paste your Claude Desktop compatible JSON configuration
5. Click "Import MCP Configuration"

Example JSON format:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "description": "Dynamic problem-solving through thought sequences"
    }
  }
}
```

#### Method 2: mcp.json File
1. Create or edit `mcp.json` file in the S647 addon directory
2. Use Claude Desktop compatible JSON format
3. Click "Load mcp.json" in preferences or MCP panel

#### Method 3: Through UI
1. Open S647 panel in 3D Viewport sidebar
2. Expand "MCP Integration" section
3. Click "Manage Servers"
4. Use "Add" button for example servers or configure custom ones

#### Method 4: Programmatically
```python
from s647 import mcp_client

# Add a server configuration
mcp_client.add_mcp_server(
    name="weather_server",
    command="python",
    args=["weather_server.py"],
    description="Weather information server"
)

# Connect to the server
mcp_client.connect_mcp_server("weather_server")
```

### Server Configuration Examples

#### Python MCP Server
```python
mcp_client.add_mcp_server(
    name="file_manager",
    command="python",
    args=["file_manager_server.py"],
    env={"DATA_PATH": "/path/to/data"},
    description="File management server"
)
```

#### Node.js MCP Server
```python
mcp_client.add_mcp_server(
    name="api_server",
    command="node",
    args=["api_server.js"],
    env={"API_KEY": "your_api_key"},
    description="External API integration server"
)
```

## 🧠 Sequential Thinking Integration

S647 comes with the Sequential Thinking MCP server pre-configured, providing advanced problem-solving capabilities:

### Features:
- **Step-by-step Analysis**: Break complex problems into manageable steps
- **Thought Revision**: Revise and refine thoughts as understanding deepens
- **Alternative Paths**: Branch into different reasoning approaches
- **Hypothesis Testing**: Generate and verify solution hypotheses

### Usage Examples:
```
User: "How should I approach modeling a complex architectural structure?"
AI: [Uses sequential thinking]
Step 1: Analyzing the architectural requirements...
Step 2: Considering different modeling approaches...
Step 3: Evaluating pros and cons of each method...
[Continues with structured thinking process]

User: "Help me debug this Python script for Blender"
AI: [Uses sequential thinking]
Step 1: Understanding the script's intended functionality...
Step 2: Identifying potential error sources...
Step 3: Testing hypotheses about the bug...
[Provides systematic debugging approach]
```

## 🔧 Using MCP Tools

### Automatic Tool Discovery

When you connect to an MCP server, S647 automatically:
1. Discovers available tools
2. Adds them to the AI's tool palette
3. Makes them available for AI-driven workflows

### Tool Usage in Chat

Simply describe what you want to do, and the AI will automatically use appropriate MCP tools:

```
User: "Think through the best approach for this modeling task"
AI: [Uses sequential thinking tool] "Let me break this down step by step..."

User: "Check the weather in New York"
AI: [Uses weather MCP tool] "The current weather in New York is..."

User: "Save this mesh data to a file"
AI: [Uses file management MCP tool] "I've saved the mesh data to..."
```

### Manual Tool Calls

You can also call MCP tools directly:
```python
from s647 import mcp_client

# Call a tool
result = mcp_client.call_mcp_tool(
    tool_name="get_weather",
    arguments={"location": "New York", "units": "metric"}
)

print(result)
```

## 📚 MCP Resources

MCP servers can provide resources (data, files, documentation) that enhance the AI's context:

### Automatic Resource Integration

Resources are automatically included in the AI's context:
- File contents
- Documentation
- Configuration data
- Real-time data feeds

### Accessing Resources

```python
from s647 import mcp_client

# Get a resource
resource = mcp_client.get_mcp_manager().get_resource("file://project_docs.md")
print(resource)
```

## 🔒 Security Features

### Built-in Security Controls

1. **Tool Name Validation**: Prevents injection attacks
2. **Argument Validation**: Checks tool arguments against schemas
3. **Dangerous Pattern Detection**: Scans for potentially harmful code
4. **User Confirmation**: Optional confirmation for tool calls

### Security Settings

Configure security in preferences:
- **Confirm MCP Tool Calls**: Require user confirmation (recommended)
- **Auto-connect MCP Servers**: Automatically connect on startup
- **Enable MCP Integration**: Master switch for MCP features

### Security Best Practices

1. **Only connect to trusted MCP servers**
2. **Keep "Confirm MCP Tool Calls" enabled**
3. **Review tool descriptions before use**
4. **Monitor tool call logs in console**

## 🎨 Integration with S647 Modes

### Chat Mode
- MCP tools enhance conversational AI
- Resources provide additional context
- Natural language tool invocation

### Act Mode
- MCP tools become part of automated workflows
- Task-oriented tool usage
- Streamlined execution paths

### Hybrid Mode
- Intelligent tool selection based on context
- Seamless mode switching with MCP capabilities

## 🔧 Advanced Configuration

### Custom Server Development

Create your own MCP servers using the official SDKs:
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Other SDKs](https://modelcontextprotocol.io/sdks)

### Environment Variables

Configure servers with environment variables:
```python
mcp_client.add_mcp_server(
    name="database_server",
    command="python",
    args=["db_server.py"],
    env={
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "blender_projects"
    }
)
```

## 🐛 Troubleshooting

### Common Issues

1. **"MCP SDK not available"**
   - Install: `pip install mcp>=1.0.0`
   - Restart Blender

2. **Server connection fails**
   - Check server script path
   - Verify server dependencies
   - Check console for error messages

3. **Tools not appearing**
   - Ensure server is connected
   - Check server tool implementation
   - Restart AI engine: S647 panel → Advanced → Initialize AI

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- Check console output for detailed error messages
- Run the test suite to identify issues
- Review MCP server logs
- Consult [MCP documentation](https://modelcontextprotocol.io)

## 📈 Performance Tips

1. **Limit concurrent connections**: Connect only to needed servers
2. **Use resource caching**: Resources are cached automatically
3. **Monitor tool call frequency**: Avoid excessive tool calls
4. **Optimize server response times**: Use efficient MCP server implementations

## 🔮 Future Enhancements

Planned features for future releases:
- Visual MCP server builder
- Server marketplace integration
- Advanced resource management
- Custom tool creation wizard
- Performance monitoring dashboard

## 📖 Examples and Use Cases

### 3D Asset Management
```python
# Connect to asset management server
mcp_client.add_mcp_server(
    name="asset_manager",
    command="python",
    args=["asset_server.py"],
    description="3D asset management and retrieval"
)
```

### Version Control Integration
```python
# Connect to Git server
mcp_client.add_mcp_server(
    name="git_server",
    command="node",
    args=["git_mcp_server.js"],
    description="Git version control integration"
)
```

### Cloud Storage Access
```python
# Connect to cloud storage
mcp_client.add_mcp_server(
    name="cloud_storage",
    command="python",
    args=["cloud_server.py"],
    env={"CLOUD_API_KEY": "your_key"},
    description="Cloud storage integration"
)
```

---

For more information about Model Context Protocol, visit [modelcontextprotocol.io](https://modelcontextprotocol.io).
