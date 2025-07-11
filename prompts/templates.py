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
Template Engine for S647 Prompt System
======================================

This module provides template processing capabilities for dynamic
prompt and text generation with variable substitution.
"""

import re
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Simple template engine for prompt and text processing.
    
    Supports:
    - Variable substitution: {variable_name}
    - Conditional blocks: {if condition}...{endif}
    - Default values: {variable_name|default_value}
    - Safe handling of missing variables
    """
    
    def __init__(self):
        """Initialize the template engine."""
        # Pattern for variable substitution: {variable_name} or {variable_name|default}
        self.variable_pattern = re.compile(r'\{([^}|]+)(?:\|([^}]*))?\}')
        
        # Pattern for conditional blocks: {if variable}...{endif}
        self.conditional_pattern = re.compile(r'\{if\s+([^}]+)\}(.*?)\{endif\}', re.DOTALL)
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Render template with provided variables.
        
        Args:
            template: Template string with placeholders
            variables: Dictionary of variables for substitution
            
        Returns:
            Rendered string with variables substituted
        """
        try:
            # First process conditional blocks
            rendered = self._process_conditionals(template, variables)
            
            # Then process variable substitutions
            rendered = self._process_variables(rendered, variables)
            
            return rendered
            
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return template  # Return original template on error
    
    def _process_conditionals(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Process conditional blocks in template.
        
        Args:
            text: Template text
            variables: Variables dictionary
            
        Returns:
            Text with conditionals processed
        """
        def replace_conditional(match):
            condition = match.group(1).strip()
            content = match.group(2)
            
            # Simple condition evaluation
            if self._evaluate_condition(condition, variables):
                return content
            else:
                return ''
        
        return self.conditional_pattern.sub(replace_conditional, text)
    
    def _process_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Process variable substitutions in template.
        
        Args:
            text: Template text
            variables: Variables dictionary
            
        Returns:
            Text with variables substituted
        """
        def replace_variable(match):
            var_name = match.group(1).strip()
            default_value = match.group(2) if match.group(2) is not None else ''
            
            # Get variable value
            value = self._get_variable_value(var_name, variables)
            
            if value is not None:
                return str(value)
            else:
                return default_value
        
        return self.variable_pattern.sub(replace_variable, text)
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """
        Evaluate a simple condition.
        
        Args:
            condition: Condition string
            variables: Variables dictionary
            
        Returns:
            Boolean result of condition evaluation
        """
        try:
            # Simple variable existence check
            if condition in variables:
                value = variables[condition]
                # Consider empty strings, None, 0, empty lists as False
                if value is None or value == '' or value == 0 or value == []:
                    return False
                return True
            
            # Check for simple comparisons (variable == value)
            if '==' in condition:
                var_name, expected_value = condition.split('==', 1)
                var_name = var_name.strip()
                expected_value = expected_value.strip().strip('"\'')
                
                actual_value = self._get_variable_value(var_name, variables)
                return str(actual_value) == expected_value
            
            # Check for simple negation (!variable)
            if condition.startswith('!'):
                var_name = condition[1:].strip()
                return not self._evaluate_condition(var_name, variables)
            
            return False
            
        except Exception as e:
            logger.warning(f"Condition evaluation error: {e}")
            return False
    
    def _get_variable_value(self, var_name: str, variables: Dict[str, Any]) -> Any:
        """
        Get variable value with support for nested access.
        
        Args:
            var_name: Variable name (supports dot notation: object.property)
            variables: Variables dictionary
            
        Returns:
            Variable value or None if not found
        """
        try:
            # Support dot notation for nested access
            if '.' in var_name:
                parts = var_name.split('.')
                value = variables
                
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    elif hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        return None
                
                return value
            else:
                return variables.get(var_name)
                
        except Exception as e:
            logger.warning(f"Variable access error for '{var_name}': {e}")
            return None
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """
        Validate template syntax and return analysis.
        
        Args:
            template: Template string to validate
            
        Returns:
            Validation report
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'variables_found': [],
            'conditionals_found': []
        }
        
        try:
            # Find all variables
            variables = self.variable_pattern.findall(template)
            for var_match in variables:
                var_name = var_match[0]
                default_value = var_match[1] if var_match[1] else None
                report['variables_found'].append({
                    'name': var_name,
                    'has_default': default_value is not None,
                    'default': default_value
                })
            
            # Find all conditionals
            conditionals = self.conditional_pattern.findall(template)
            for cond_match in conditionals:
                condition = cond_match[0]
                report['conditionals_found'].append(condition)
            
            # Check for unmatched braces
            open_braces = template.count('{')
            close_braces = template.count('}')
            if open_braces != close_braces:
                report['valid'] = False
                report['errors'].append(f"Unmatched braces: {open_braces} open, {close_braces} close")
            
            # Check for nested conditionals (not supported)
            if template.count('{if') != template.count('{endif}'):
                report['valid'] = False
                report['errors'].append("Unmatched if/endif blocks")
            
        except Exception as e:
            report['valid'] = False
            report['errors'].append(f"Template validation error: {e}")
        
        return report


# Utility functions for common template operations
def render_simple(template: str, **kwargs) -> str:
    """
    Simple template rendering function.
    
    Args:
        template: Template string
        **kwargs: Variables for substitution
        
    Returns:
        Rendered string
    """
    engine = TemplateEngine()
    return engine.render(template, kwargs)


def format_count(template: str, count: int, **kwargs) -> str:
    """
    Format template with count and additional variables.
    
    Args:
        template: Template string
        count: Count value
        **kwargs: Additional variables
        
    Returns:
        Formatted string
    """
    variables = {'count': count}
    variables.update(kwargs)
    return render_simple(template, **variables)


def format_status(template: str, status: str, **kwargs) -> str:
    """
    Format template with status and additional variables.
    
    Args:
        template: Template string
        status: Status value
        **kwargs: Additional variables
        
    Returns:
        Formatted string
    """
    variables = {'status': status}
    variables.update(kwargs)
    return render_simple(template, **variables)
