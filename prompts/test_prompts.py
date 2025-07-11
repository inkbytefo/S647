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
Test Suite for S647 Prompt System
=================================

This module contains tests for the centralized prompt management system.
"""

import unittest
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from prompts import PromptManager
    from prompts.templates import TemplateEngine, render_simple, format_count
    from prompts.system_prompts import SystemPrompts
    from prompts.ui_texts import UITexts
    from prompts.messages import Messages
except ImportError as e:
    print(f"Import error: {e}")
    print("Running tests in standalone mode...")

    # Import directly for standalone testing
    from __init__ import PromptManager
    from templates import TemplateEngine, render_simple, format_count
    from system_prompts import SystemPrompts
    from ui_texts import UITexts
    from messages import Messages


class TestPromptManager(unittest.TestCase):
    """Test cases for PromptManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        PromptManager.initialize()
    
    def test_get_system_prompt(self):
        """Test system prompt generation."""
        # Test basic prompt
        prompt = PromptManager.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("S647", prompt)
        
        # Test mode-specific prompts
        chat_prompt = PromptManager.get_system_prompt(mode='chat')
        act_prompt = PromptManager.get_system_prompt(mode='act')
        hybrid_prompt = PromptManager.get_system_prompt(mode='hybrid')
        
        self.assertIn("CHAT MODE", chat_prompt)
        self.assertIn("ACT MODE", act_prompt)
        self.assertIn("HYBRID MODE", hybrid_prompt)
    
    def test_get_ui_text(self):
        """Test UI text retrieval."""
        # Test basic text
        text = PromptManager.get_ui_text('clear')
        self.assertEqual(text, "🗑️ Clear")
        
        # Test mode-specific text
        send_chat = PromptManager.get_ui_text('send', mode='chat')
        send_act = PromptManager.get_ui_text('send', mode='act')
        
        self.assertEqual(send_chat, "💬 Send")
        self.assertEqual(send_act, "⚡ Execute")
        
        # Test missing text
        missing = PromptManager.get_ui_text('nonexistent')
        self.assertIn("Missing", missing)
    
    def test_get_message(self):
        """Test message retrieval."""
        # Test error message
        error = PromptManager.get_message('api_key_missing', level='error')
        self.assertIn("Configure AI provider", error)
        
        # Test success message
        success = PromptManager.get_message('connection_successful', level='success')
        self.assertIn("Connection successful", success)
    
    def test_placeholder_text(self):
        """Test placeholder text generation."""
        # Test mode-specific placeholders
        chat_placeholder = PromptManager.get_placeholder_text('input', mode='chat')
        act_placeholder = PromptManager.get_placeholder_text('input', mode='act')
        
        self.assertIn("Ask me anything", chat_placeholder)
        self.assertIn("Tell me what to do", act_placeholder)
    
    def test_validation(self):
        """Test prompt validation."""
        report = PromptManager.validate_prompts()
        self.assertIsInstance(report, dict)
        self.assertIn('valid', report)
        self.assertIn('stats', report)


class TestTemplateEngine(unittest.TestCase):
    """Test cases for TemplateEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = TemplateEngine()
    
    def test_simple_variable_substitution(self):
        """Test basic variable substitution."""
        template = "Hello {name}!"
        variables = {'name': 'World'}
        result = self.engine.render(template, variables)
        self.assertEqual(result, "Hello World!")
    
    def test_variable_with_default(self):
        """Test variable substitution with default values."""
        template = "Hello {name|Anonymous}!"
        
        # With variable
        result1 = self.engine.render(template, {'name': 'Alice'})
        self.assertEqual(result1, "Hello Alice!")
        
        # Without variable (use default)
        result2 = self.engine.render(template, {})
        self.assertEqual(result2, "Hello Anonymous!")
    
    def test_conditional_blocks(self):
        """Test conditional block processing."""
        template = "{if show_greeting}Hello {name}!{endif}"
        
        # With condition true
        result1 = self.engine.render(template, {'show_greeting': True, 'name': 'Alice'})
        self.assertEqual(result1, "Hello Alice!")
        
        # With condition false
        result2 = self.engine.render(template, {'show_greeting': False, 'name': 'Alice'})
        self.assertEqual(result2, "")
    
    def test_nested_variable_access(self):
        """Test nested variable access with dot notation."""
        template = "User: {user.name}, Email: {user.email}"
        variables = {
            'user': {
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        result = self.engine.render(template, variables)
        self.assertEqual(result, "User: John Doe, Email: john@example.com")
    
    def test_template_validation(self):
        """Test template validation."""
        # Valid template
        valid_template = "Hello {name}! {if greeting}Welcome!{endif}"
        report1 = self.engine.validate_template(valid_template)
        self.assertTrue(report1['valid'])
        self.assertEqual(len(report1['variables_found']), 1)
        self.assertEqual(len(report1['conditionals_found']), 1)
        
        # Invalid template (unmatched braces)
        invalid_template = "Hello {name! Missing brace"
        report2 = self.engine.validate_template(invalid_template)
        self.assertFalse(report2['valid'])
        self.assertGreater(len(report2['errors']), 0)
    
    def test_utility_functions(self):
        """Test utility template functions."""
        # Test render_simple
        result1 = render_simple("Hello {name}!", name="World")
        self.assertEqual(result1, "Hello World!")
        
        # Test format_count
        result2 = format_count("{count} items", 5)
        self.assertEqual(result2, "5 items")


class TestSystemPrompts(unittest.TestCase):
    """Test cases for SystemPrompts."""
    
    def test_base_prompt(self):
        """Test base prompt retrieval."""
        prompt = SystemPrompts.get_base_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("S647", prompt)
        self.assertIn("Blender", prompt)
    
    def test_mode_prompts(self):
        """Test mode-specific prompts."""
        chat_mode = SystemPrompts.get_mode_prompt('chat')
        act_mode = SystemPrompts.get_mode_prompt('act')
        hybrid_mode = SystemPrompts.get_mode_prompt('hybrid')
        
        self.assertIn("CHAT MODE", chat_mode)
        self.assertIn("ACT MODE", act_mode)
        self.assertIn("HYBRID MODE", hybrid_mode)
    
    def test_full_prompt_generation(self):
        """Test complete prompt generation with context."""
        context = {
            'scene_name': 'TestScene',
            'mode': 'OBJECT',
            'active_object': {'name': 'Cube'},
            'selected_objects': ['Cube', 'Sphere'],
            'total_objects': 2,
            'current_frame': 1,
            'frame_range': [1, 100]
        }
        
        prompt = SystemPrompts.get_full_prompt(mode='chat', context=context)
        self.assertIn("TestScene", prompt)
        self.assertIn("Cube", prompt)
        self.assertIn("CHAT MODE", prompt)
    
    def test_validation(self):
        """Test system prompts validation."""
        stats = SystemPrompts.validate()
        self.assertIsInstance(stats, dict)
        self.assertIn('base_prompt_length', stats)
        self.assertIn('mode_prompts_count', stats)
        self.assertEqual(stats['mode_prompts_count'], 3)


class TestUITexts(unittest.TestCase):
    """Test cases for UITexts."""
    
    def test_text_retrieval(self):
        """Test basic text retrieval."""
        text = UITexts.get_text('clear')
        self.assertEqual(text, "🗑️ Clear")
        
        # Test missing text
        missing = UITexts.get_text('nonexistent')
        self.assertIn("Missing", missing)
    
    def test_mode_specific_texts(self):
        """Test mode-specific text variations."""
        send_chat = UITexts.get_text('send', mode='chat')
        send_act = UITexts.get_text('send', mode='act')
        send_hybrid = UITexts.get_text('send', mode='hybrid')
        
        self.assertEqual(send_chat, "💬 Send")
        self.assertEqual(send_act, "⚡ Execute")
        self.assertEqual(send_hybrid, "🧠 Process")
    
    def test_placeholders(self):
        """Test placeholder text generation."""
        chat_placeholder = UITexts.get_placeholder('input', mode='chat')
        act_placeholder = UITexts.get_placeholder('input', mode='act')
        
        self.assertIn("Ask me anything", chat_placeholder)
        self.assertIn("Tell me what to do", act_placeholder)
    
    def test_status_texts(self):
        """Test status text retrieval."""
        thinking = UITexts.get_status_text('thinking')
        responding = UITexts.get_status_text('responding')
        
        self.assertIn("thinking", thinking)
        self.assertIn("responding", responding)
    
    def test_validation(self):
        """Test UI texts validation."""
        stats = UITexts.validate()
        self.assertIsInstance(stats, dict)
        self.assertGreater(stats['button_texts'], 0)
        self.assertGreater(stats['status_texts'], 0)


class TestMessages(unittest.TestCase):
    """Test cases for Messages."""
    
    def test_message_retrieval(self):
        """Test message retrieval by level."""
        error = Messages.get_message('api_key_missing', 'error')
        warning = Messages.get_message('api_key_missing_openai', 'warning')
        success = Messages.get_message('connection_successful', 'success')
        
        self.assertIn("Configure AI provider", error)
        self.assertIn("API key required", warning)
        self.assertIn("Connection successful", success)
    
    def test_convenience_methods(self):
        """Test convenience methods for different message types."""
        error = Messages.get_error('api_key_missing')
        warning = Messages.get_warning('api_key_missing_openai')
        success = Messages.get_success('connection_successful')
        info = Messages.get_info('ai_engine_ready')
        
        self.assertIsInstance(error, str)
        self.assertIsInstance(warning, str)
        self.assertIsInstance(success, str)
        self.assertIsInstance(info, str)
    
    def test_validation(self):
        """Test messages validation."""
        stats = Messages.validate()
        self.assertIsInstance(stats, dict)
        self.assertGreater(stats['error_messages'], 0)
        self.assertGreater(stats['success_messages'], 0)


def run_tests():
    """Run all prompt system tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestPromptManager))
    suite.addTest(unittest.makeSuite(TestTemplateEngine))
    suite.addTest(unittest.makeSuite(TestSystemPrompts))
    suite.addTest(unittest.makeSuite(TestUITexts))
    suite.addTest(unittest.makeSuite(TestMessages))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
