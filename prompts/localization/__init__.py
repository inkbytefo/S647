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
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
Localization Support for S647 Prompt System
===========================================

This module provides localization infrastructure for supporting
multiple languages in the S647 prompt system.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalizationManager:
    """
    Manager for handling multiple language support.
    
    This class provides the infrastructure for loading and managing
    localized text content for different languages.
    """
    
    def __init__(self):
        """Initialize the localization manager."""
        self.current_language = 'en'
        self.fallback_language = 'en'
        self.loaded_languages = {}
        self.localization_dir = Path(__file__).parent
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            language_code: Language code (e.g., 'en', 'tr', 'de')
            
        Returns:
            True if language was set successfully
        """
        try:
            if self.load_language(language_code):
                self.current_language = language_code
                logger.info(f"Language set to: {language_code}")
                return True
            else:
                logger.warning(f"Failed to set language to: {language_code}")
                return False
        except Exception as e:
            logger.error(f"Error setting language to {language_code}: {e}")
            return False
    
    def load_language(self, language_code: str) -> bool:
        """
        Load language file.
        
        Args:
            language_code: Language code to load
            
        Returns:
            True if loaded successfully
        """
        try:
            if language_code in self.loaded_languages:
                return True
            
            language_file = self.localization_dir / f"{language_code}.json"
            
            if not language_file.exists():
                logger.warning(f"Language file not found: {language_file}")
                return False
            
            with open(language_file, 'r', encoding='utf-8') as f:
                language_data = json.load(f)
            
            self.loaded_languages[language_code] = language_data
            logger.info(f"Loaded language: {language_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading language {language_code}: {e}")
            return False
    
    def get_text(self, key: str, language: Optional[str] = None) -> Optional[str]:
        """
        Get localized text by key.
        
        Args:
            key: Text key (supports dot notation: section.subsection.key)
            language: Optional language override
            
        Returns:
            Localized text or None if not found
        """
        try:
            target_language = language or self.current_language
            
            # Ensure language is loaded
            if target_language not in self.loaded_languages:
                if not self.load_language(target_language):
                    # Try fallback language
                    if self.fallback_language != target_language:
                        target_language = self.fallback_language
                        if not self.load_language(target_language):
                            return None
                    else:
                        return None
            
            # Navigate through nested keys
            data = self.loaded_languages[target_language]
            keys = key.split('.')
            
            for k in keys:
                if isinstance(data, dict) and k in data:
                    data = data[k]
                else:
                    # Try fallback language if current fails
                    if target_language != self.fallback_language:
                        return self.get_text(key, self.fallback_language)
                    return None
            
            return str(data) if data is not None else None
            
        except Exception as e:
            logger.error(f"Error getting localized text for key '{key}': {e}")
            return None
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available language codes.
        
        Returns:
            List of available language codes
        """
        try:
            languages = []
            for file_path in self.localization_dir.glob("*.json"):
                if file_path.is_file():
                    languages.append(file_path.stem)
            return sorted(languages)
        except Exception as e:
            logger.error(f"Error getting available languages: {e}")
            return ['en']  # Return default
    
    def get_language_info(self, language_code: str) -> Dict[str, Any]:
        """
        Get information about a language.
        
        Args:
            language_code: Language code
            
        Returns:
            Language information dictionary
        """
        try:
            if self.load_language(language_code):
                data = self.loaded_languages[language_code]
                return {
                    'code': language_code,
                    'name': data.get('_meta', {}).get('name', language_code),
                    'native_name': data.get('_meta', {}).get('native_name', language_code),
                    'version': data.get('_meta', {}).get('version', '1.0'),
                    'author': data.get('_meta', {}).get('author', 'Unknown'),
                    'completion': data.get('_meta', {}).get('completion', 100)
                }
            else:
                return {
                    'code': language_code,
                    'name': language_code,
                    'native_name': language_code,
                    'version': '0.0',
                    'author': 'Unknown',
                    'completion': 0
                }
        except Exception as e:
            logger.error(f"Error getting language info for {language_code}: {e}")
            return {'code': language_code, 'name': language_code}
    
    def validate_language_file(self, language_code: str) -> Dict[str, Any]:
        """
        Validate a language file.
        
        Args:
            language_code: Language code to validate
            
        Returns:
            Validation report
        """
        report = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            language_file = self.localization_dir / f"{language_code}.json"
            
            if not language_file.exists():
                report['errors'].append(f"Language file not found: {language_file}")
                return report
            
            with open(language_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for required sections
            required_sections = ['ui_texts', 'messages', 'system_prompts']
            for section in required_sections:
                if section not in data:
                    report['warnings'].append(f"Missing section: {section}")
            
            # Check metadata
            if '_meta' not in data:
                report['warnings'].append("Missing metadata section")
            else:
                meta = data['_meta']
                required_meta = ['name', 'native_name', 'version']
                for field in required_meta:
                    if field not in meta:
                        report['warnings'].append(f"Missing metadata field: {field}")
            
            # Count entries
            total_entries = 0
            for section, content in data.items():
                if section != '_meta' and isinstance(content, dict):
                    total_entries += self._count_entries(content)
            
            report['stats'] = {
                'total_entries': total_entries,
                'sections': len([k for k in data.keys() if k != '_meta']),
                'has_metadata': '_meta' in data
            }
            
            report['valid'] = len(report['errors']) == 0
            
        except json.JSONDecodeError as e:
            report['errors'].append(f"Invalid JSON: {e}")
        except Exception as e:
            report['errors'].append(f"Validation error: {e}")
        
        return report
    
    def _count_entries(self, data: Any) -> int:
        """
        Recursively count entries in nested dictionary.
        
        Args:
            data: Data to count
            
        Returns:
            Number of entries
        """
        if isinstance(data, dict):
            count = 0
            for value in data.values():
                if isinstance(value, dict):
                    count += self._count_entries(value)
                else:
                    count += 1
            return count
        else:
            return 1
    
    def create_language_template(self, language_code: str, base_language: str = 'en') -> bool:
        """
        Create a new language file template based on existing language.
        
        Args:
            language_code: New language code
            base_language: Base language to copy structure from
            
        Returns:
            True if template was created successfully
        """
        try:
            if not self.load_language(base_language):
                logger.error(f"Cannot load base language: {base_language}")
                return False
            
            base_data = self.loaded_languages[base_language].copy()
            
            # Update metadata
            if '_meta' in base_data:
                base_data['_meta']['name'] = f"Language Name ({language_code})"
                base_data['_meta']['native_name'] = f"Native Name ({language_code})"
                base_data['_meta']['version'] = "1.0"
                base_data['_meta']['author'] = "Translator Name"
                base_data['_meta']['completion'] = 0
                base_data['_meta']['base_language'] = base_language
            
            # Mark all text entries for translation
            self._mark_for_translation(base_data)
            
            # Save template
            template_file = self.localization_dir / f"{language_code}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(base_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created language template: {template_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating language template for {language_code}: {e}")
            return False
    
    def _mark_for_translation(self, data: Any, prefix: str = "[TRANSLATE]") -> None:
        """
        Recursively mark text entries for translation.
        
        Args:
            data: Data to process
            prefix: Prefix to add to translatable strings
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '_meta':
                    continue  # Skip metadata
                elif isinstance(value, dict):
                    self._mark_for_translation(value, prefix)
                elif isinstance(value, str):
                    data[key] = f"{prefix} {value}"


# Global localization manager instance
_localization_manager = LocalizationManager()


def get_localization_manager() -> LocalizationManager:
    """Get the global localization manager instance."""
    return _localization_manager


def set_language(language_code: str) -> bool:
    """Set the current language."""
    return _localization_manager.set_language(language_code)


def get_localized_text(key: str, language: Optional[str] = None) -> Optional[str]:
    """Get localized text by key."""
    return _localization_manager.get_text(key, language)


def get_available_languages() -> List[str]:
    """Get list of available languages."""
    return _localization_manager.get_available_languages()


__all__ = [
    'LocalizationManager',
    'get_localization_manager',
    'set_language',
    'get_localized_text',
    'get_available_languages'
]
