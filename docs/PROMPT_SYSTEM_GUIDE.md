# S647 Centralized Prompt System Guide

## 🎯 Overview

The S647 Centralized Prompt System provides a unified, maintainable approach to managing all text content in the Blender addon. This system replaces scattered hardcoded strings with a centralized, template-based solution that supports localization and consistent messaging.

## 🏗️ Architecture

### Core Components

```
prompts/
├── __init__.py              # PromptManager - Main API
├── system_prompts.py        # AI system prompts
├── ui_texts.py             # UI labels and buttons
├── messages.py             # Error/success messages
├── templates.py            # Template engine
└── localization/           # Multi-language support
    ├── __init__.py
    ├── en.json
    └── tr.json
```

### Key Classes

- **`PromptManager`**: Central interface for all text access
- **`SystemPrompts`**: AI system prompts with mode variations
- **`UITexts`**: User interface texts and labels
- **`Messages`**: System messages (errors, warnings, success)
- **`TemplateEngine`**: Dynamic text generation with variables
- **`LocalizationManager`**: Multi-language support

## 🚀 Quick Start

### Basic Usage

```python
from .prompts import PromptManager

# Get system prompt for AI
prompt = PromptManager.get_system_prompt(mode='chat')

# Get UI text
button_text = PromptManager.get_ui_text('send', mode='act')

# Get error message
error_msg = PromptManager.get_message('api_key_missing', level='error')

# Get placeholder text
placeholder = PromptManager.get_placeholder_text('input', mode='chat')
```

### In Panel Classes

```python
class MyPanel(Panel):
    def _get_ui_text(self, key: str, mode: str = None, **kwargs) -> str:
        """Get UI text with fallback"""
        try:
            from .prompts import PromptManager
            return PromptManager.get_ui_text(key, mode=mode, **kwargs)
        except (ImportError, Exception):
            return f"[{key}]"  # Fallback
    
    def draw(self, context):
        layout = self.layout
        
        # Use centralized text
        layout.label(text=self._get_ui_text("welcome_main"))
        layout.operator("my.op", text=self._get_ui_text("send", mode="chat"))
```

## 📝 System Prompts

### Mode-Specific Prompts

The system supports three interaction modes:

- **Chat Mode**: Educational, conversational
- **Act Mode**: Task-focused, direct
- **Hybrid Mode**: Adaptive switching

```python
# Get mode-specific system prompt
chat_prompt = PromptManager.get_system_prompt(mode='chat')
act_prompt = PromptManager.get_system_prompt(mode='act')
hybrid_prompt = PromptManager.get_system_prompt(mode='hybrid')
```

### With Context

```python
# Include Blender context
context = {
    'scene_name': 'MyScene',
    'mode': 'OBJECT',
    'active_object': {'name': 'Cube'},
    'selected_objects': ['Cube', 'Sphere'],
    'total_objects': 5
}

prompt = PromptManager.get_system_prompt(
    mode='chat', 
    context=context,
    user_request="Create a material"
)
```

## 🎨 UI Texts

### Button Texts

```python
# Mode-specific button texts
send_chat = PromptManager.get_ui_text('send', mode='chat')    # "💬 Send"
send_act = PromptManager.get_ui_text('send', mode='act')      # "⚡ Execute"
send_hybrid = PromptManager.get_ui_text('send', mode='hybrid') # "🧠 Process"

# Regular button texts
clear_text = PromptManager.get_ui_text('clear')              # "🗑️ Clear"
save_text = PromptManager.get_ui_text('save')                # "💾 Save"
```

### Placeholders

```python
# Input placeholders by mode
chat_placeholder = PromptManager.get_placeholder_text('input', mode='chat')
# "💬 Ask me anything about Blender..."

act_placeholder = PromptManager.get_placeholder_text('input', mode='act')
# "⚡ Tell me what to do in Blender..."
```

### Status Texts

```python
# Status indicators
thinking = PromptManager.get_status_text('thinking')         # "🤖 S647 is thinking..."
responding = PromptManager.get_status_text('responding')     # "🤖 S647 is responding..."
error = PromptManager.get_status_text('error')              # "❌ Error occurred"
```

## 📢 Messages

### Message Types

```python
# Error messages
error = PromptManager.get_message('api_key_missing', level='error')
# "⚠️ Configure AI provider in preferences"

# Warning messages
warning = PromptManager.get_message('code_execution_disabled', level='warning')
# "⚠️ Code execution disabled"

# Success messages
success = PromptManager.get_message('connection_successful', level='success')
# "✅ Connection successful"

# Info messages
info = PromptManager.get_message('ai_engine_ready', level='info')
# "✓ AI Engine Ready"
```

### Convenience Methods

```python
# Direct access methods
error = Messages.get_error('api_key_missing')
warning = Messages.get_warning('safety_warnings_detected')
success = Messages.get_success('file_saved')
info = Messages.get_info('processing_request')
```

## 🔧 Template System

### Variable Substitution

```python
# Template with variables
template = "📝 {count} characters"
result = PromptManager.get_ui_text('character_count', count=42)
# "📝 42 characters"
```

### Conditional Blocks

```python
# Template with conditions
template = "{if show_count}You have {count} messages{endif}"
variables = {'show_count': True, 'count': 5}
result = TemplateEngine().render(template, variables)
# "You have 5 messages"
```

### Default Values

```python
# Template with defaults
template = "Hello {name|Anonymous}!"
result1 = TemplateEngine().render(template, {'name': 'Alice'})  # "Hello Alice!"
result2 = TemplateEngine().render(template, {})                 # "Hello Anonymous!"
```

## 🌍 Localization

### Setting Language

```python
from prompts.localization import set_language, get_available_languages

# Get available languages
languages = get_available_languages()  # ['en', 'tr']

# Set language
success = set_language('tr')  # Switch to Turkish
```

### Language Files

Language files are stored in `prompts/localization/`:

```json
{
  "_meta": {
    "name": "English",
    "native_name": "English",
    "version": "1.0.0",
    "completion": 100
  },
  "ui_texts": {
    "buttons": {
      "send": {
        "chat": "💬 Send",
        "act": "⚡ Execute"
      }
    }
  }
}
```

## 🔍 Validation

### Validate Prompts

```python
# Validate all prompts
report = PromptManager.validate_prompts()

print(f"Valid: {report['valid']}")
print(f"Errors: {report['errors']}")
print(f"Statistics: {report['stats']}")
```

### Validate Templates

```python
from prompts.templates import TemplateEngine

engine = TemplateEngine()
report = engine.validate_template("Hello {name}! {if greeting}Welcome!{endif}")

print(f"Valid: {report['valid']}")
print(f"Variables: {report['variables_found']}")
print(f"Conditionals: {report['conditionals_found']}")
```

## 📚 Adding New Content

### Adding UI Texts

1. **Add to `ui_texts.py`**:
```python
BUTTON_TEXTS = {
    'my_new_button': "🆕 New Action",
    # ...
}
```

2. **Use in code**:
```python
text = PromptManager.get_ui_text('my_new_button')
```

### Adding Messages

1. **Add to `messages.py`**:
```python
ERROR_MESSAGES = {
    'my_new_error': "❌ Something went wrong with {operation}",
    # ...
}
```

2. **Use in code**:
```python
error = PromptManager.get_message('my_new_error', level='error', operation="file save")
```

### Adding System Prompts

1. **Modify `system_prompts.py`**:
```python
MODE_PROMPTS = {
    'my_new_mode': """
🔥 MY NEW MODE:
• Special instructions for this mode
• Custom behavior guidelines
""",
    # ...
}
```

## 🔄 Migration from Legacy Code

### Before (Legacy)
```python
# Hardcoded strings
layout.label(text="💬 Send")
layout.label(text="⚠️ API key required")
```

### After (Centralized)
```python
# Centralized system
layout.label(text=self._get_ui_text('send', mode='chat'))
layout.label(text=self._get_message('api_key_missing', level='error'))
```

## 🛠️ Best Practices

1. **Always use PromptManager**: Don't hardcode strings
2. **Provide fallbacks**: Handle import errors gracefully
3. **Use templates**: For dynamic content with variables
4. **Validate regularly**: Check prompt system integrity
5. **Document new additions**: Update this guide when adding content
6. **Test thoroughly**: Use the integration test script

## 🧪 Testing

Run the integration test:

```bash
python test_prompt_integration.py
```

This tests:
- PromptManager import and initialization
- System prompt generation
- UI text retrieval
- Message handling
- Template engine functionality
- Localization support
- Validation system
- Legacy compatibility

## 🔗 Related Files

- `test_prompt_integration.py` - Integration tests
- `prompts/test_prompts.py` - Unit tests
- `docs/MULTI_PROVIDER_GUIDE.md` - AI provider configuration
- `docs/MCP_INTEGRATION_GUIDE.md` - MCP integration

---

*This guide covers the S647 Centralized Prompt System. For questions or contributions, refer to the project documentation.*
