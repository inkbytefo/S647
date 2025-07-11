# S647 Multi-Provider AI Integration Guide

## 🎯 Overview

S647 now supports multiple AI providers through a simple, unified interface. You can use either:
- **OpenAI** (default) - Official OpenAI API
- **Custom OpenAI-Compatible** - Any OpenAI-compatible API provider

## 🚀 Supported Providers

### Popular OpenAI-Compatible Providers:

1. **Anthropic Claude**
   - Base URL: `https://api.anthropic.com/v1`
   - Models: `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`

2. **Groq**
   - Base URL: `https://api.groq.com/openai/v1`
   - Models: `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`

3. **DeepSeek**
   - Base URL: `https://api.deepseek.com/v1`
   - Models: `deepseek-chat`, `deepseek-coder`

4. **Local Ollama**
   - Base URL: `http://localhost:11434/v1`
   - Models: `llama3.2`, `codellama`, `mistral`

5. **xAI (Grok)**
   - Base URL: `https://api.x.ai/v1`
   - Models: `grok-beta`

## ⚙️ Configuration

### Method 1: OpenAI (Default)
1. Go to `Edit > Preferences > Add-ons > S647`
2. Set **AI Provider** to `OpenAI`
3. Enter your OpenAI API key
4. Select your preferred model
5. Click "Test Connection"

### Method 2: Custom Provider
1. Go to `Edit > Preferences > Add-ons > S647`
2. Set **AI Provider** to `Custom OpenAI-Compatible`
3. Fill in the custom provider settings:
   - **Base URL**: The API endpoint (e.g., `https://api.anthropic.com/v1`)
   - **Model Name**: The exact model name (e.g., `claude-3-5-sonnet-20241022`)
   - **Custom API Key**: Your API key for the provider
4. Click "Test Connection"

## 📋 Configuration Examples

### Anthropic Claude
```
Provider: Custom OpenAI-Compatible
Base URL: https://api.anthropic.com/v1
Model Name: claude-3-5-sonnet-20241022
API Key: sk-ant-api03-[your-key]
```

### Groq
```
Provider: Custom OpenAI-Compatible
Base URL: https://api.groq.com/openai/v1
Model Name: llama-3.1-70b-versatile
API Key: gsk_[your-key]
```

### Local Ollama
```
Provider: Custom OpenAI-Compatible
Base URL: http://localhost:11434/v1
Model Name: llama3.2
API Key: ollama (or any value)
```

### DeepSeek
```
Provider: Custom OpenAI-Compatible
Base URL: https://api.deepseek.com/v1
Model Name: deepseek-chat
API Key: sk-[your-key]
```

## 🔧 Technical Details

### How It Works
- Uses OpenAI Python client with custom `base_url` parameter
- Maintains full compatibility with existing safety features
- Preserves all conversation history and context features
- No changes to the user interface panels

### Supported Features
- ✅ Chat completions
- ✅ Streaming responses (if provider supports)
- ✅ Temperature and max_tokens control
- ✅ Conversation history
- ✅ Code execution safety features
- ✅ Blender context awareness

### Limitations
- Provider must be OpenAI API compatible
- Some providers may have different rate limits
- Model-specific features may vary

## 🛠️ Troubleshooting

### Common Issues

1. **"Connection failed" error**
   - Check Base URL format (must include `/v1` for most providers)
   - Verify API key is correct
   - Ensure model name is exact (case-sensitive)

2. **"Model not found" error**
   - Double-check model name spelling
   - Verify model is available for your API key
   - Some models require special access

3. **"Authentication failed" error**
   - Verify API key format
   - Check if API key has required permissions
   - Some providers require specific headers

### Testing Connection
Always use the "Test Connection" button after configuration to verify:
- API endpoint is reachable
- Authentication is working
- Model is available

## 🔒 Security Notes

- API keys are stored securely in Blender preferences
- All existing safety features remain active
- Custom providers inherit the same security sandbox
- Code execution safety is provider-independent

## 💡 Tips

1. **Cost Optimization**: Different providers have different pricing
2. **Performance**: Local models (Ollama) don't require internet
3. **Privacy**: Local models keep data completely private
4. **Fallback**: Keep OpenAI configured as backup
5. **Testing**: Use smaller models for testing configurations

## 🆘 Support

If you encounter issues:
1. Check the Base URL format
2. Verify model name accuracy
3. Test with a simple model first
4. Check provider documentation for API compatibility

---

**Happy AI-powered Blender modeling! 🎨🤖**
