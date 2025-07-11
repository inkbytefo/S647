# S647 - AI-Powered Blender Assistant

🤖 Advanced Blender addon with AI chat, code execution, and MCP integration for enhanced 3D workflows.

## ✨ Features

- **💬 Chat & Act Modes**: Conversational learning or direct task execution
- **🔧 Code Generation**: AI creates and executes Blender Python scripts safely
- **🧠 MCP Integration**: Connect to external tools and services via Model Context Protocol
- **🎯 Multi-Provider Support**: OpenAI, Anthropic, Groq, Ollama, and custom providers
- **💾 Smart Memory**: Persistent conversations and context management

## 📋 Requirements

- Blender 4.4.0+
- AI Provider API Key (OpenAI, Anthropic, etc.)
- Internet connection

## � Installation

### Quick Setup (ZIP Install)

1. **Download**: Get the latest release ZIP from GitHub
2. **Install**: Blender → Edit → Preferences → Add-ons → Install → Select ZIP
3. **Enable**: Check "S647 - AI-Powered Blender Assistant"
4. **Configure**: Add your AI provider API key in addon preferences
5. **Test**: Click "Test Connection" to verify setup

### MCP Configuration (Optional)

1. **Copy**: `mcp.json.example` → `mcp.json`
2. **Edit**: Update file paths and enable desired MCP servers
3. **Reload**: Restart Blender or reload addon

> See `docs/MCP_INTEGRATION_GUIDE.md` for detailed MCP setup

## 🎯 Usage

1. **Open Panel**: Press `N` in 3D Viewport → Find "S647" tab
2. **Choose Mode**:
   - 💬 **Chat**: Learning & questions
   - ⚡ **Act**: Direct actions & automation
3. **Type & Send**: Enter your request and click Send/Execute
4. **Review Code**: Check AI-generated scripts before running
5. **Execute**: Click "Execute" to run code in Blender

### Example Prompts

**Chat**: "How do I create realistic materials?"
**Act**: "Create 10 cubes in a circle pattern"
**Act**: "Add subdivision surface to selected object"

## 📚 Documentation

- **MCP Setup**: `docs/MCP_INTEGRATION_GUIDE.md`
- **Multi-Provider Config**: `docs/MULTI_PROVIDER_GUIDE.md`
- **Implementation Details**: `docs/` folder

## 🔒 Safety

- Built-in code validation and sandbox mode
- User confirmation for code execution
- Safe module import restrictions
- Always review AI-generated code before running

## 📄 License

GNU General Public License v2.0 or later

## ⚠️ Disclaimer

Review all AI-generated code before execution. Keep API keys secure.
