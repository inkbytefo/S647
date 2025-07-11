# S647 - AI-Powered Blender Assistant

An advanced Blender addon that integrates OpenAI's powerful language models to assist with 3D modeling, scripting, and automation tasks within Blender.

## 🚀 Features

### 💬 **Unified Chat Interface**
- **Modern Chat Experience**: Single, streamlined interface inspired by leading AI assistants
- **Smart Mode Pills**: Easy switching between Chat, Act, and Hybrid modes
- **Message Bubbles**: Clean, modern message display with timestamps
- **Instant Actions**: Apply, explain, or modify AI-generated code with one click
- **Context-Aware Input**: Smart placeholders and suggestions based on current mode

### 🎯 **Interaction Modes**
- **💬 Chat Mode**: Conversational, educational interactions perfect for learning
- **⚡ Act Mode**: Task-focused, direct action and automation
- **🧠 Hybrid Mode**: Smart mode switching based on context and intent

### 🧠 **Advanced AI Capabilities**
- **AI-Powered Assistance**: Specialized AI assistant for Blender workflows
- **Code Generation**: Generate Python scripts for Blender automation
- **Safe Code Execution**: Execute AI-generated code with built-in safety measures
- **Context Awareness**: AI understands your current Blender scene and selection
- **Intent Detection**: AI recognizes whether you're asking questions or requesting actions

### 💾 **Context Management**
- **Conversation Threading**: Organize conversations by topic or project
- **Persistent Memory**: Remember context across Blender sessions
- **Smart Context Compression**: Intelligent memory management for optimal performance
- **Context Export/Import**: Share conversations and context between projects

### 🎯 **Task Management**
- **Task Breakdown**: Complex operations split into manageable steps
- **Progress Tracking**: Visual progress indicators for multi-step tasks
- **Action Queue**: Sequential execution of complex workflows
- **Error Recovery**: Smart handling of failed operations

### 🔧 **Technical Features**
- **Multiple AI Providers**: Support for OpenAI and custom OpenAI-compatible providers (Anthropic, Groq, Ollama, etc.)
- **Multiple AI Models**: Support for various models from different providers
- **Conversation History**: Keep track of your interactions with the AI

## 📋 Requirements

- **Blender**: 4.4.0 or higher
- **Python**: 3.8+ (included with Blender)
- **AI Provider API Key**: Required for AI functionality (OpenAI, Anthropic, Groq, etc.)
- **Internet Connection**: Required for API communication

## 🔧 Installation

### Method 1: Automatic Installation (Recommended)

1. **Download the Addon**
   - Download all files from this repository
   - Keep the folder structure intact

2. **Install Dependencies**
   - Run the dependency installer: `python install_dependencies.py`
   - Or manually install: `pip install openai==1.95.0`

3. **Install in Blender**
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Click `Install...` and select the addon folder
   - Enable the "S647 - AI-Powered Blender Assistant" addon

4. **Configure AI Provider**
   - In the addon preferences, choose your AI provider:
     - **OpenAI**: Enter your OpenAI API key from https://platform.openai.com/api-keys
     - **Custom Provider**: Enter Base URL, Model Name, and API key for any OpenAI-compatible provider
   - Choose your preferred AI model and settings
   - Click "Test Connection" to verify setup
   - See `MULTI_PROVIDER_GUIDE.md` for detailed configuration examples

### Method 2: Manual Installation

1. **Install OpenAI Package**
   ```bash
   # Find your Blender's Python path, then:
   /path/to/blender/python -m pip install openai==1.95.0
   ```

2. **Install Addon**
   - Follow steps 3-4 from Method 1

## 🎯 Usage

### Basic Usage

1. **Open the S647 Panel**
   - In the 3D Viewport, press `N` to open the sidebar
   - Look for the "S647" tab

2. **Choose Your Interaction Mode**
   - **💬 Chat Mode**: For learning and exploring ("How do I create materials?")
   - **⚡ Act Mode**: For direct actions ("Create 10 cubes in a circle")
   - **🧠 Hybrid Mode**: Let AI choose the best response style

3. **Start Interacting**
   - Type your question or request in the prompt field
   - Click "Send" (Chat), "Execute" (Act), or "Process" (Hybrid)
   - The AI will respond with mode-appropriate assistance

4. **Execute Code**
   - When the AI provides Python code, you'll see an "Execute" button
   - Review the code before execution
   - Click "Execute" to run the code in Blender

5. **Manage Context**
   - Use conversation threads to organize different topics
   - Save important contexts for later use
   - Export conversations to share with team members

### Example Prompts

#### 💬 Chat Mode Examples:
- "How do subdivision surfaces work in Blender?"
- "Explain the difference between Cycles and Eevee rendering"
- "What's the best way to create realistic glass materials?"
- "Can you teach me about keyframe animation?"

#### ⚡ Act Mode Examples:
- "Create a simple material with a red color"
- "Add a subdivision surface modifier to the selected object"
- "Create an array of cubes in a circle pattern"
- "Generate a procedural texture for a metal surface"
- "Set up a three-point lighting rig"

#### 🧠 Hybrid Mode Examples:
- "I need help with rigging - create an armature and explain the process"
- "Make this animation smoother and tell me why it works"
- "Optimize my scene for rendering and explain the changes"

### Advanced Safety Features

- **Comprehensive Code Analysis**: Multi-layer security scanning
- **Risk Level Assessment**: Low, Medium, High, Critical risk classification
- **Enhanced Sandbox Mode**: Strict module import restrictions
- **Real-time Safety Warnings**: Immediate feedback on dangerous operations
- **Blender Operation Detection**: Identifies destructive Blender commands
- **Execution Time Limits**: Prevents infinite loops and runaway code
- **Memory Protection**: Operation count limits to prevent resource abuse
- **Import Validation**: Whitelist-based module import control
- **Pattern Recognition**: Advanced regex-based threat detection

## ⚙️ Configuration

### Addon Preferences

Access via `Edit > Preferences > Add-ons > S647`

**AI Provider Settings:**
- **Provider**: Choose between OpenAI or Custom OpenAI-Compatible
- **API Key**: Your provider's API key
- **Model**: Choose model (varies by provider)
- **Custom Settings**: Base URL and model name for custom providers
- **Max Tokens**: Maximum response length
- **Temperature**: Controls creativity (0.0 = deterministic, 1.0 = creative)

**Safety Settings:**
- **Enable Code Execution**: Allow/disallow code execution
- **Confirm Before Execution**: Show confirmation dialogs
- **Sandbox Mode**: Run code in restricted environment

**Interface Settings:**
- **Show Advanced Options**: Display advanced controls
- **Auto-save Conversations**: Automatically save chat history
- **Conversation History Limit**: Maximum messages to keep

### Panel Options

**Interaction Mode:**
- **Chat Mode**: Conversational, educational responses
- **Act Mode**: Task-focused, direct action
- **Hybrid Mode**: Smart mode switching based on context

**Context Mode:**
- **Minimal**: Basic scene information
- **Standard**: Selected objects and scene data
- **Detailed**: Comprehensive object information
- **Full**: Complete scene dump (may be slow)

**Context Management:**
- **Thread Management**: Organize conversations by topic
- **Memory Persistence**: Save context between sessions
- **Context Export/Import**: Share conversations and context

## 🔒 Security & Safety

S647 includes multiple safety layers:

1. **Code Validation**: Syntax checking before execution
2. **Import Restrictions**: Blocks dangerous modules in sandbox mode
3. **Builtin Restrictions**: Removes risky functions like `eval()`, `exec()`
4. **User Confirmation**: Optional dialogs before code execution
5. **Output Capture**: Safe execution with error handling

### Sandbox Mode

When enabled, sandbox mode:
- Restricts file system access
- Blocks network operations
- Prevents system command execution
- Limits module imports to safe Blender-related modules

## 📁 File Structure

```
S647/
├── __init__.py          # Main addon entry point
├── preferences.py       # Addon preferences and settings
├── properties.py        # Runtime properties and data
├── operators.py         # Blender operators (actions)
├── panels.py           # User interface panels
├── ai_engine.py        # AI communication (placeholder)
├── code_executor.py    # Safe code execution
├── utils.py            # Utility functions
└── README.md           # This file
```

## 🚧 Development Status

**Current Phase: Advanced Code Execution System Complete**

✅ **Completed:**
- ✅ Basic addon structure and registration
- ✅ User interface panels and controls
- ✅ Properties and preferences system
- ✅ **Advanced code execution with comprehensive safety**
- ✅ **OpenAI API integration with real AI models**
- ✅ **Automatic dependency installation**
- ✅ **Connection testing and error handling**
- ✅ **Context-aware AI responses**
- ✅ **Enhanced security sandbox with strict mode**
- ✅ **Comprehensive code analysis and risk assessment**
- ✅ **Blender-specific operation detection**
- ✅ **Real-time safety warnings and recommendations**

✅ **Latest Addition: Multi-Provider Support**
- ✅ **OpenAI and Custom Provider Support**
- ✅ **Anthropic Claude Integration**
- ✅ **Groq, DeepSeek, and Local Ollama Support**
- ✅ **Unified OpenAI-Compatible Interface**

✅ **Latest Major Update: Chat & Act Modes + Context Management**
- ✅ **Chat, Act, and Hybrid interaction modes**
- ✅ **Advanced context management and threading**
- ✅ **Task breakdown and progress tracking**
- ✅ **Intent detection and smart suggestions**
- ✅ **Persistent memory and context export/import**

🔄 **Next Phase: Advanced AI Features**
- Multimodal AI integration (vision capabilities)
- Voice interaction support
- Collaborative AI agents
- Custom workflow automation

🔮 **Future Enhancements:**
- Custom AI model fine-tuning
- Plugin system for extensions
- Advanced code analysis and validation
- Voice interaction capabilities

## 🤝 Contributing

This is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the GNU General Public License v2.0 or later.
See the license headers in individual files for details.

## ⚠️ Disclaimer

- This addon executes AI-generated code in Blender
- Always review code before execution
- Use sandbox mode for additional safety
- The developers are not responsible for any damage caused by code execution
- Keep your API key secure and never share it

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the Blender Python API docs
- **Community**: Join Blender development forums

## 🙏 Acknowledgments

- Blender Foundation for the amazing 3D software
- OpenAI for providing powerful language models
- Blender Python API documentation and community
- All contributors and testers

---

**S647 Development Team**  
*Making AI-powered 3D creation accessible to everyone*
