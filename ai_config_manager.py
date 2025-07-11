"""
S647 AI Configuration Manager

Centralized AI provider management system that supports OpenAI and OpenAI-compatible providers.
Provides a clean abstraction layer for different AI providers with proper error handling.

Author: S647 Team
License: MIT
"""

import json
import traceback
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import bpy

# Global state
_config_manager = None

class ProviderType(Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    CUSTOM = "custom"

class ConnectionStatus(Enum):
    """Connection status states"""
    NOT_CONFIGURED = "not_configured"
    CONFIGURED = "configured"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class ProviderConfig:
    """Configuration data for an AI provider"""
    provider_type: ProviderType
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    extra_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}

@dataclass
class ProviderStatus:
    """Status information for a provider"""
    status: ConnectionStatus
    message: str
    available_models: List[str] = None
    last_test_time: Optional[str] = None
    error_details: Optional[str] = None

    def __post_init__(self):
        if self.available_models is None:
            self.available_models = []

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None
        self._status = ProviderStatus(
            status=ConnectionStatus.NOT_CONFIGURED,
            message="Provider not configured"
        )

    @abstractmethod
    def validate_config(self) -> Tuple[bool, str]:
        """Validate the provider configuration"""
        pass

    @abstractmethod
    def create_client(self) -> Tuple[bool, str]:
        """Create and initialize the AI client"""
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Test the connection to the AI service"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass

    @abstractmethod
    def format_error(self, error: Exception) -> str:
        """Format provider-specific error messages"""
        pass

    @property
    def client(self):
        """Get the AI client instance"""
        return self._client

    @property
    def status(self) -> ProviderStatus:
        """Get current provider status"""
        return self._status

    def is_ready(self) -> bool:
        """Check if provider is ready for use"""
        return (self._client is not None and 
                self._status.status == ConnectionStatus.CONNECTED)

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    DEFAULT_MODELS = [
        'gpt-4o',
        'gpt-4o-mini', 
        'gpt-4-turbo',
        'gpt-3.5-turbo'
    ]

    def validate_config(self) -> Tuple[bool, str]:
        """Validate OpenAI configuration"""
        if not self.config.api_key:
            return False, "OpenAI API key is required"
        
        if not self.config.api_key.startswith('sk-'):
            return False, "Invalid OpenAI API key format (should start with 'sk-')"
        
        return True, "Configuration valid"

    def create_client(self) -> Tuple[bool, str]:
        """Create OpenAI client"""
        try:
            # Import OpenAI with proper error handling
            try:
                from openai import OpenAI
            except ImportError:
                return False, "OpenAI library not installed. Run: pip install openai==1.95.0"

            # Validate config first
            valid, message = self.validate_config()
            if not valid:
                return False, message

            # Create client
            self._client = OpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            self._status.status = ConnectionStatus.CONFIGURED
            self._status.message = "OpenAI client created successfully"
            return True, "OpenAI client initialized"

        except Exception as e:
            error_msg = self.format_error(e)
            self._status.status = ConnectionStatus.ERROR
            self._status.message = error_msg
            self._status.error_details = str(e)
            return False, error_msg

    def test_connection(self) -> Tuple[bool, str]:
        """Test OpenAI connection"""
        if not self._client:
            return False, "Client not initialized"

        try:
            # Use a simple, low-cost test
            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self._status.status = ConnectionStatus.CONNECTED
            self._status.message = "Connection successful"
            return True, "OpenAI connection test successful"

        except Exception as e:
            error_msg = self.format_error(e)
            self._status.status = ConnectionStatus.ERROR
            self._status.message = error_msg
            self._status.error_details = str(e)
            return False, error_msg

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        if not self._client:
            return self.DEFAULT_MODELS

        try:
            # Try to get models from API
            models_response = self._client.models.list()
            models = [model.id for model in models_response.data 
                     if model.id.startswith(('gpt-', 'text-'))]
            
            # Filter and sort models
            filtered_models = [m for m in models if any(
                default in m for default in ['gpt-4', 'gpt-3.5']
            )]
            
            return sorted(filtered_models) if filtered_models else self.DEFAULT_MODELS

        except Exception as e:
            print(f"S647: Could not fetch OpenAI models: {e}")
            return self.DEFAULT_MODELS

    def format_error(self, error: Exception) -> str:
        """Format OpenAI-specific errors"""
        error_str = str(error).lower()
        
        if "api key" in error_str or "unauthorized" in error_str:
            return "Invalid or expired OpenAI API key"
        elif "quota" in error_str or "billing" in error_str:
            return "OpenAI quota exceeded or billing issue"
        elif "rate limit" in error_str:
            return "OpenAI rate limit exceeded"
        elif "network" in error_str or "connection" in error_str:
            return "Network connection error to OpenAI"
        elif "model" in error_str and "not found" in error_str:
            return "Requested model not available"
        else:
            return f"OpenAI error: {str(error)}"

class CustomProvider(AIProvider):
    """Custom OpenAI-compatible provider implementation"""
    
    def validate_config(self) -> Tuple[bool, str]:
        """Validate custom provider configuration"""
        if not self.config.api_key:
            return False, "API key is required for custom provider"
        
        if not self.config.base_url:
            return False, "Base URL is required for custom provider"
        
        if not self.config.model:
            return False, "Model name is required for custom provider"
        
        # Validate URL format
        if not (self.config.base_url.startswith('http://') or 
                self.config.base_url.startswith('https://')):
            return False, "Base URL must start with http:// or https://"
        
        return True, "Configuration valid"

    def create_client(self) -> Tuple[bool, str]:
        """Create custom provider client"""
        try:
            # Import OpenAI with proper error handling
            try:
                from openai import OpenAI
            except ImportError:
                return False, "OpenAI library not installed. Run: pip install openai==1.95.0"

            # Validate config first
            valid, message = self.validate_config()
            if not valid:
                return False, message

            # Create client with custom base URL
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
            
            self._status.status = ConnectionStatus.CONFIGURED
            self._status.message = f"Custom provider client created for {self.config.base_url}"
            return True, "Custom provider client initialized"

        except Exception as e:
            error_msg = self.format_error(e)
            self._status.status = ConnectionStatus.ERROR
            self._status.message = error_msg
            self._status.error_details = str(e)
            return False, error_msg

    def test_connection(self) -> Tuple[bool, str]:
        """Test custom provider connection"""
        if not self._client:
            return False, "Client not initialized"

        try:
            # Test with the configured model
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self._status.status = ConnectionStatus.CONNECTED
            self._status.message = "Connection successful"
            return True, f"Custom provider connection test successful with model {self.config.model}"

        except Exception as e:
            error_msg = self.format_error(e)
            self._status.status = ConnectionStatus.ERROR
            self._status.message = error_msg
            self._status.error_details = str(e)
            return False, error_msg

    def get_available_models(self) -> List[str]:
        """Get available models for custom provider"""
        # For custom providers, we typically only know the configured model
        # unless the provider supports model listing
        if self.config.model:
            return [self.config.model]
        
        if not self._client:
            return []

        try:
            # Try to get models from API (if supported)
            models_response = self._client.models.list()
            return [model.id for model in models_response.data]
        except Exception:
            # If model listing is not supported, return configured model
            return [self.config.model] if self.config.model else []

    def format_error(self, error: Exception) -> str:
        """Format custom provider-specific errors"""
        error_str = str(error).lower()
        
        if "api key" in error_str or "unauthorized" in error_str:
            return f"Invalid API key for custom provider ({self.config.base_url})"
        elif "not found" in error_str and "model" in error_str:
            return f"Model '{self.config.model}' not found on custom provider"
        elif "connection" in error_str or "network" in error_str:
            return f"Cannot connect to custom provider at {self.config.base_url}"
        elif "timeout" in error_str:
            return f"Timeout connecting to custom provider ({self.config.base_url})"
        elif "ssl" in error_str or "certificate" in error_str:
            return f"SSL/Certificate error with custom provider ({self.config.base_url})"
        else:
            return f"Custom provider error: {str(error)}"


class AIConfigManager:
    """Central AI configuration and provider management"""

    def __init__(self):
        self._current_provider: Optional[AIProvider] = None
        self._provider_cache: Dict[str, AIProvider] = {}
        self._last_config_hash: Optional[str] = None

    def get_current_provider(self) -> Optional[AIProvider]:
        """Get the currently active AI provider"""
        return self._current_provider

    def initialize_from_preferences(self) -> Tuple[bool, str]:
        """Initialize provider from Blender preferences"""
        try:
            from .preferences import get_preferences
            prefs = get_preferences()

            # Create config from preferences
            if prefs.provider_type == 'openai':
                config = ProviderConfig(
                    provider_type=ProviderType.OPENAI,
                    api_key=prefs.api_key,
                    model=prefs.api_model,
                    max_tokens=prefs.max_tokens,
                    temperature=prefs.temperature
                )
            elif prefs.provider_type == 'custom':
                config = ProviderConfig(
                    provider_type=ProviderType.CUSTOM,
                    api_key=prefs.custom_api_key,
                    base_url=prefs.custom_base_url,
                    model=prefs.custom_model,
                    max_tokens=prefs.max_tokens,
                    temperature=prefs.temperature
                )
            else:
                return False, f"Unknown provider type: {prefs.provider_type}"

            return self.set_provider(config)

        except Exception as e:
            return False, f"Failed to initialize from preferences: {str(e)}"

    def set_provider(self, config: ProviderConfig) -> Tuple[bool, str]:
        """Set and initialize a new provider"""
        try:
            # Generate config hash for caching
            config_hash = self._generate_config_hash(config)

            # Check if we can reuse cached provider
            if (config_hash == self._last_config_hash and
                self._current_provider and
                self._current_provider.is_ready()):
                return True, "Provider already initialized and ready"

            # Create new provider
            if config.provider_type == ProviderType.OPENAI:
                provider = OpenAIProvider(config)
            elif config.provider_type == ProviderType.CUSTOM:
                provider = CustomProvider(config)
            else:
                return False, f"Unsupported provider type: {config.provider_type}"

            # Initialize provider
            success, message = provider.create_client()
            if not success:
                return False, message

            # Test connection
            success, test_message = provider.test_connection()
            if not success:
                return False, f"Connection test failed: {test_message}"

            # Set as current provider
            self._current_provider = provider
            self._last_config_hash = config_hash
            self._provider_cache[config_hash] = provider

            return True, f"Provider initialized successfully: {message}"

        except Exception as e:
            return False, f"Failed to set provider: {str(e)}"

    def test_current_provider(self) -> Tuple[bool, str]:
        """Test the current provider connection"""
        if not self._current_provider:
            return False, "No provider configured"

        return self._current_provider.test_connection()

    def get_available_models(self) -> List[str]:
        """Get available models from current provider"""
        if not self._current_provider:
            return []

        return self._current_provider.get_available_models()

    def get_provider_status(self) -> Optional[ProviderStatus]:
        """Get current provider status"""
        if not self._current_provider:
            return None

        return self._current_provider.status

    def is_ready(self) -> bool:
        """Check if AI system is ready for use"""
        return (self._current_provider is not None and
                self._current_provider.is_ready())

    def get_client(self):
        """Get the current AI client for making requests"""
        if not self._current_provider:
            return None

        return self._current_provider.client

    def reset(self):
        """Reset the configuration manager"""
        self._current_provider = None
        self._provider_cache.clear()
        self._last_config_hash = None

    def _generate_config_hash(self, config: ProviderConfig) -> str:
        """Generate a hash for config caching"""
        import hashlib

        config_str = f"{config.provider_type.value}:{config.api_key}:{config.base_url}:{config.model}"
        return hashlib.md5(config_str.encode()).hexdigest()

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the current state"""
        info = {
            "has_provider": self._current_provider is not None,
            "provider_ready": self.is_ready(),
            "cached_providers": len(self._provider_cache),
            "last_config_hash": self._last_config_hash
        }

        if self._current_provider:
            status = self._current_provider.status
            info.update({
                "provider_type": self._current_provider.config.provider_type.value,
                "provider_status": status.status.value,
                "provider_message": status.message,
                "available_models_count": len(status.available_models),
                "has_client": self._current_provider.client is not None
            })

        return info


def get_ai_config_manager() -> AIConfigManager:
    """Get the global AI config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AIConfigManager()
    return _config_manager


def reset_ai_config_manager():
    """Reset the global AI config manager"""
    global _config_manager
    if _config_manager:
        _config_manager.reset()
    _config_manager = None
