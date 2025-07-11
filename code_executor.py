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
S647 Code Executor Module
=========================

Handles safe execution of AI-generated Python code within Blender.
Provides sandboxing and security features.
"""

import bpy
import sys
import io
import contextlib
import traceback
import re
from typing import Optional, Dict, Any, List, Tuple

# Enhanced security configuration for sandbox mode
ALLOWED_MODULES = {
    # Core Blender modules
    'bpy', 'bmesh', 'mathutils', 'bpy_extras', 'gpu', 'gpu_extras',
    'blf', 'aud', 'freestyle', 'cycles',

    # Safe Python standard library
    'math', 'random', 'time', 'datetime', 'json', 're', 'collections',
    'itertools', 'functools', 'operator', 'typing', 'enum', 'dataclasses',
    'copy', 'weakref', 'decimal', 'fractions', 'statistics', 'uuid',
    'string', 'textwrap', 'unicodedata', 'codecs', 'base64', 'binascii',
    'struct', 'array', 'bisect', 'heapq', 'keyword', 'reprlib',
}

RESTRICTED_MODULES = {
    # File system and OS access
    'os', 'sys', 'subprocess', 'shutil', 'glob', 'pathlib', 'tempfile',
    'fileinput', 'stat', 'filecmp', 'fnmatch', 'linecache', 'shlex',

    # Network and internet
    'urllib', 'requests', 'socket', 'socketserver', 'http', 'ftplib',
    'poplib', 'imaplib', 'nntplib', 'smtplib', 'telnetlib', 'ssl',
    'xmlrpc', 'webbrowser', 'cgi', 'cgitb', 'wsgiref',

    # Process and threading
    'threading', 'multiprocessing', '_thread', 'concurrent', 'asyncio',
    'queue', 'sched', 'signal', 'atexit',

    # Serialization and databases
    'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3', 'csv',

    # Code execution and introspection
    'imp', 'importlib', 'pkgutil', 'modulefinder', 'runpy', 'ast',
    'dis', 'inspect', 'types', 'gc', 'ctypes', 'mmap',

    # Debugging and profiling
    'pdb', 'profile', 'pstats', 'timeit', 'trace', 'tracemalloc',
}

# Dangerous built-in functions to restrict
DANGEROUS_BUILTINS = {
    'eval', 'exec', 'compile', '__import__', 'open', 'input', 'raw_input',
    'file', 'execfile', 'reload', 'vars', 'locals', 'globals', 'dir',
    'getattr', 'setattr', 'delattr', 'hasattr', 'callable'
}

# Dangerous operations patterns
DANGEROUS_PATTERNS = [
    # File operations
    (r'\bopen\s*\(', "File operations detected"),
    (r'\bfile\s*\(', "File operations detected"),
    (r'\.read\s*\(', "File read operation"),
    (r'\.write\s*\(', "File write operation"),
    (r'\.delete\s*\(', "Delete operation"),

    # System operations
    (r'\bos\b', "Operating system access"),
    (r'\bsys\b', "System module access"),
    (r'\bsubprocess\b', "Subprocess execution"),
    (r'\beval\s*\(', "Dynamic code evaluation"),
    (r'\bexec\s*\(', "Dynamic code execution"),
    (r'\b__import__\s*\(', "Dynamic module import"),

    # Destructive Blender operations
    (r'bpy\.ops\.wm\.quit', "Blender quit operation"),
    (r'bpy\.ops\.wm\.save', "File save operation"),
    (r'bpy\.ops\.wm\.open', "File open operation"),
    (r'bpy\.data\..*\.remove\s*\(', "Data removal operation"),
    (r'bpy\.ops\..*\.delete', "Delete operation"),
    (r'\.clear\s*\(', "Clear operation"),

    # Network operations
    (r'\burllib\b', "Network access"),
    (r'\brequests\b', "HTTP requests"),
    (r'\bsocket\b', "Socket operations"),

    # Threading and processes
    (r'\bthreading\b', "Threading operations"),
    (r'\bmultiprocessing\b', "Multiprocessing operations"),
]

class SandboxedEnvironment:
    """Advanced sandboxed execution environment for AI-generated code"""

    def __init__(self, strict_mode=True):
        self.strict_mode = strict_mode
        self.original_modules = {}
        self.restricted_builtins = {}
        self.original_import = None
        self.execution_stats = {
            'operations_count': 0,
            'max_operations': 10000,
            'start_time': None,
            'max_execution_time': 30.0  # seconds
        }

    def __enter__(self):
        """Enter sandbox mode with comprehensive restrictions"""
        import builtins
        import time

        # Store original state
        self.original_modules = sys.modules.copy()
        self.original_builtins = builtins.__dict__.copy()
        self.original_import = builtins.__import__
        self.execution_stats['start_time'] = time.time()

        # Create restricted import function
        def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
            # Check if module is allowed
            root_module = name.split('.')[0]

            if root_module in RESTRICTED_MODULES:
                raise ImportError(f"Module '{name}' is restricted in sandbox mode")

            if self.strict_mode and root_module not in ALLOWED_MODULES:
                raise ImportError(f"Module '{name}' is not in allowed modules list")

            # Use original import for allowed modules
            return self.original_import(name, globals, locals, fromlist, level)

        # Replace dangerous builtins
        for builtin_name in DANGEROUS_BUILTINS:
            if builtin_name in builtins.__dict__:
                self.restricted_builtins[builtin_name] = builtins.__dict__[builtin_name]

                if builtin_name == '__import__':
                    builtins.__dict__[builtin_name] = restricted_import
                else:
                    # Create a restricted version that raises an error
                    def create_restricted_func(name):
                        def restricted_func(*args, **kwargs):
                            raise PermissionError(f"Function '{name}' is restricted in sandbox mode")
                        return restricted_func

                    builtins.__dict__[builtin_name] = create_restricted_func(builtin_name)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sandbox mode and restore original state"""
        import builtins

        # Restore original builtins
        for builtin_name, original_func in self.restricted_builtins.items():
            builtins.__dict__[builtin_name] = original_func

        # Clean up any new restricted modules that were imported
        current_modules = set(sys.modules.keys())
        original_modules = set(self.original_modules.keys())
        new_modules = current_modules - original_modules

        for module_name in new_modules:
            root_module = module_name.split('.')[0]
            if root_module in RESTRICTED_MODULES:
                try:
                    del sys.modules[module_name]
                except KeyError:
                    pass  # Module already removed

    def check_execution_limits(self):
        """Check if execution limits are exceeded"""
        import time

        # Check operation count
        self.execution_stats['operations_count'] += 1
        if self.execution_stats['operations_count'] > self.execution_stats['max_operations']:
            raise RuntimeError("Maximum operation count exceeded")

        # Check execution time
        if self.execution_stats['start_time']:
            elapsed = time.time() - self.execution_stats['start_time']
            if elapsed > self.execution_stats['max_execution_time']:
                raise TimeoutError("Maximum execution time exceeded")

def execute_code(code: str, sandbox: bool = True, strict_mode: bool = True) -> str:
    """
    Execute Python code safely with comprehensive analysis and protection

    Args:
        code: Python code to execute
        sandbox: Whether to run in sandboxed environment
        strict_mode: Whether to use strict safety checks

    Returns:
        Execution result or error message
    """
    if not code.strip():
        return "No code to execute"

    # Pre-execution safety analysis
    safety_analysis = analyze_code_safety(code, strict_mode)

    if not safety_analysis['is_safe']:
        error_msg = f"Code execution blocked due to safety concerns:\n"
        error_msg += f"Risk Level: {safety_analysis['risk_level'].upper()}\n\n"

        if safety_analysis['errors']:
            error_msg += "Critical Issues:\n"
            for error in safety_analysis['errors']:
                error_msg += f"  Line {error['line']}: {error['description']}\n"

        if safety_analysis['warnings']:
            error_msg += "\nWarnings:\n"
            for warning in safety_analysis['warnings'][:5]:  # Limit to first 5
                error_msg += f"  Line {warning['line']}: {warning['description']}\n"

        if safety_analysis['recommendations']:
            error_msg += "\nRecommendations:\n"
            for rec in safety_analysis['recommendations']:
                error_msg += f"  • {rec}\n"

        return error_msg

    # Capture output and errors
    output_buffer = io.StringIO()
    error_buffer = io.StringIO()
    execution_start_time = None

    try:
        import time
        execution_start_time = time.time()

        # Create safe execution environment
        exec_globals = create_enhanced_execution_context()

        # Execute code with appropriate protection level
        if sandbox:
            with SandboxedEnvironment(strict_mode=strict_mode):
                with contextlib.redirect_stdout(output_buffer), \
                     contextlib.redirect_stderr(error_buffer):
                    exec(code, exec_globals)
        else:
            with contextlib.redirect_stdout(output_buffer), \
                 contextlib.redirect_stderr(error_buffer):
                exec(code, exec_globals)

        # Calculate execution time
        execution_time = time.time() - execution_start_time if execution_start_time else 0

        # Get output and format results
        output = output_buffer.getvalue()
        errors = error_buffer.getvalue()

        result = format_execution_output(output, errors, execution_time, safety_analysis)

        return result

    except TimeoutError as e:
        return f"Execution Timeout: {str(e)}\nExecution was terminated due to time limit."

    except PermissionError as e:
        return f"Permission Denied: {str(e)}\nOperation blocked by sandbox security."

    except Exception as e:
        execution_time = time.time() - execution_start_time if execution_start_time else 0
        error_msg = f"Execution Error: {str(e)}\n"
        error_msg += f"Execution Time: {execution_time:.3f}s\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        return error_msg

    finally:
        output_buffer.close()
        error_buffer.close()

def validate_imports(code: str) -> tuple[bool, list[str]]:
    """
    Validate that code only imports allowed modules
    
    Returns:
        Tuple of (is_valid, list_of_violations)
    """
    violations = []
    
    # Simple regex-based check for import statements
    import re
    
    # Find all import statements
    import_patterns = [
        r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
        r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
    ]
    
    lines = code.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern in import_patterns:
            match = re.match(pattern, line)
            if match:
                module_name = match.group(1).split('.')[0]  # Get root module
                
                if module_name in RESTRICTED_MODULES:
                    violations.append(f"Line {line_num}: Restricted module '{module_name}'")
                elif module_name not in ALLOWED_MODULES and not module_name.startswith('bpy'):
                    violations.append(f"Line {line_num}: Unknown module '{module_name}' (may be restricted)")
    
    return len(violations) == 0, violations

def get_execution_stats() -> Dict[str, Any]:
    """Get execution statistics"""
    # This could be expanded to track more detailed stats
    scene = bpy.context.scene
    props = scene.s647
    
    return {
        "total_executions": props.code_executions,
        "sandbox_mode": True,  # This would come from preferences
        "last_execution": props.code_execution_result,
    }

def create_safe_execution_context() -> Dict[str, Any]:
    """Create a safe execution context with limited scope"""
    context = {
        # Blender modules
        'bpy': bpy,
        
        # Math and utility modules
        'math': __import__('math'),
        'random': __import__('random'),
        'time': __import__('time'),
        'datetime': __import__('datetime'),
        'json': __import__('json'),
        're': __import__('re'),
        'collections': __import__('collections'),
        'itertools': __import__('itertools'),
        'functools': __import__('functools'),
        
        # Safe builtins
        'print': print,
        'len': len,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'sorted': sorted,
        'reversed': reversed,
        'sum': sum,
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'list': list,
        'tuple': tuple,
        'dict': dict,
        'set': set,
    }
    
    # Try to add optional Blender modules
    try:
        context['bmesh'] = __import__('bmesh')
    except ImportError:
        pass
    
    try:
        context['mathutils'] = __import__('mathutils')
    except ImportError:
        pass
    
    try:
        context['bpy_extras'] = __import__('bpy_extras')
    except ImportError:
        pass
    
    return context

def format_execution_result(result: str, max_lines: int = 50) -> str:
    """Format execution result for display"""
    if not result:
        return "No output"

    lines = result.split('\n')
    if len(lines) <= max_lines:
        return result

    # Truncate long output
    truncated = '\n'.join(lines[:max_lines])
    remaining = len(lines) - max_lines
    truncated += f'\n... ({remaining} more lines truncated)'

    return truncated

def analyze_code_safety(code: str, strict_mode: bool = True) -> Dict[str, Any]:
    """
    Comprehensive code safety analysis

    Returns:
        Dictionary with safety analysis results
    """
    import re

    analysis = {
        'is_safe': True,
        'risk_level': 'low',  # low, medium, high, critical
        'warnings': [],
        'errors': [],
        'destructive_operations': [],
        'file_operations': [],
        'network_operations': [],
        'system_operations': [],
        'blender_operations': [],
        'recommendations': []
    }

    # Check for dangerous patterns
    for pattern, description in DANGEROUS_PATTERNS:
        matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            warning = {
                'type': 'dangerous_pattern',
                'description': description,
                'line': line_num,
                'code_snippet': match.group(0),
                'pattern': pattern
            }

            # Categorize the warning
            if 'file' in description.lower() or 'read' in description.lower() or 'write' in description.lower():
                analysis['file_operations'].append(warning)
            elif 'network' in description.lower() or 'http' in description.lower() or 'socket' in description.lower():
                analysis['network_operations'].append(warning)
            elif 'system' in description.lower() or 'os' in description.lower() or 'subprocess' in description.lower():
                analysis['system_operations'].append(warning)
            elif 'delete' in description.lower() or 'remove' in description.lower() or 'clear' in description.lower():
                analysis['destructive_operations'].append(warning)
            elif 'bpy' in description.lower() or 'blender' in description.lower():
                analysis['blender_operations'].append(warning)

            analysis['warnings'].append(warning)

    # Analyze import statements
    import_analysis = analyze_imports_detailed(code)
    analysis['warnings'].extend(import_analysis['warnings'])
    analysis['errors'].extend(import_analysis['errors'])

    # Analyze Blender-specific operations
    blender_analysis = analyze_blender_operations(code)
    analysis['blender_operations'].extend(blender_analysis['operations'])
    analysis['warnings'].extend(blender_analysis['warnings'])

    # Determine risk level
    total_warnings = len(analysis['warnings'])
    destructive_count = len(analysis['destructive_operations'])
    system_count = len(analysis['system_operations'])

    if analysis['errors'] or destructive_count > 0 or system_count > 0:
        analysis['risk_level'] = 'critical'
        analysis['is_safe'] = False
    elif total_warnings > 5 or len(analysis['file_operations']) > 0:
        analysis['risk_level'] = 'high'
        analysis['is_safe'] = not strict_mode
    elif total_warnings > 2:
        analysis['risk_level'] = 'medium'

    # Generate recommendations
    if analysis['file_operations']:
        analysis['recommendations'].append("Consider using Blender's data API instead of file operations")
    if analysis['destructive_operations']:
        analysis['recommendations'].append("Review destructive operations carefully - consider backup first")
    if analysis['system_operations']:
        analysis['recommendations'].append("System operations are not allowed in sandbox mode")

    return analysis

def analyze_imports_detailed(code: str) -> Dict[str, List]:
    """Analyze import statements in code with detailed information"""
    import re

    analysis = {'warnings': [], 'errors': []}

    # Find all import statements
    import_patterns = [
        r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
        r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
    ]

    lines = code.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern in import_patterns:
            match = re.match(pattern, line)
            if match:
                module_name = match.group(1).split('.')[0]

                if module_name in RESTRICTED_MODULES:
                    analysis['errors'].append({
                        'type': 'restricted_import',
                        'description': f"Module '{module_name}' is restricted",
                        'line': line_num,
                        'module': module_name,
                        'severity': 'critical'
                    })
                elif module_name not in ALLOWED_MODULES and not module_name.startswith('bpy'):
                    analysis['warnings'].append({
                        'type': 'unknown_import',
                        'description': f"Module '{module_name}' may be restricted",
                        'line': line_num,
                        'module': module_name,
                        'severity': 'medium'
                    })

    return analysis

def analyze_blender_operations(code: str) -> Dict[str, List]:
    """Analyze Blender-specific operations with risk assessment"""
    import re

    analysis = {'operations': [], 'warnings': []}

    # Blender operation patterns with risk levels
    blender_patterns = [
        (r'bpy\.ops\.wm\.quit', 'critical', "Blender quit operation"),
        (r'bpy\.ops\.wm\.save', 'high', "File save operation"),
        (r'bpy\.ops\.wm\.open', 'medium', "File open operation"),
        (r'bpy\.data\..*\.remove\s*\(', 'high', "Data removal operation"),
        (r'bpy\.ops\..*\.delete', 'high', "Delete operation"),
        (r'bpy\.context\.scene\.objects\.unlink', 'medium', "Object unlink operation"),
        (r'\.clear\s*\(', 'medium', "Clear operation"),
        (r'bpy\.ops\.mesh\.delete', 'medium', "Mesh delete operation"),
        (r'bpy\.ops\.object\.delete', 'medium', "Object delete operation"),
        (r'bpy\.ops\.scene\.delete', 'high', "Scene delete operation"),
        (r'bpy\.ops\.material\.new', 'low', "Material creation"),
        (r'bpy\.ops\.mesh\.primitive', 'low', "Primitive creation"),
        (r'bpy\.ops\.transform\.', 'low', "Transform operation"),
    ]

    for pattern, severity, description in blender_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            operation = {
                'type': 'blender_operation',
                'severity': severity,
                'description': description,
                'line': line_num,
                'code_snippet': match.group(0),
                'pattern': pattern
            }

            analysis['operations'].append(operation)

            if severity in ['high', 'critical']:
                analysis['warnings'].append(operation)

    return analysis

def create_enhanced_execution_context() -> Dict[str, Any]:
    """Create an enhanced safe execution context with comprehensive Blender support"""
    context = {
        # Core Python builtins (safe subset)
        '__name__': '__main__',
        '__builtins__': {
            # Safe built-in functions
            'print': print, 'len': len, 'range': range, 'enumerate': enumerate,
            'zip': zip, 'map': map, 'filter': filter, 'sorted': sorted,
            'reversed': reversed, 'sum': sum, 'min': min, 'max': max,
            'abs': abs, 'round': round, 'pow': pow,

            # Safe type constructors
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'tuple': tuple, 'dict': dict, 'set': set,

            # Safe utility functions
            'isinstance': isinstance, 'issubclass': issubclass,
            'type': type, 'id': id, 'hash': hash,

            # Safe iteration
            'iter': iter, 'next': next, 'any': any, 'all': all,
        },

        # Blender modules
        'bpy': bpy,
    }

    # Try to add optional Blender modules
    try:
        import bmesh
        context['bmesh'] = bmesh
    except ImportError:
        pass

    try:
        import mathutils
        context['mathutils'] = mathutils
        # Add common mathutils classes directly
        context['Vector'] = mathutils.Vector
        context['Matrix'] = mathutils.Matrix
        context['Euler'] = mathutils.Euler
        context['Quaternion'] = mathutils.Quaternion
    except ImportError:
        pass

    try:
        import bpy_extras
        context['bpy_extras'] = bpy_extras
    except ImportError:
        pass

    # Safe standard library modules
    safe_stdlib = {
        'math': 'math', 'random': 'random', 'time': 'time',
        'datetime': 'datetime', 'json': 'json', 're': 're',
        'collections': 'collections', 'itertools': 'itertools',
        'functools': 'functools', 'copy': 'copy', 'uuid': 'uuid'
    }

    for name, module_name in safe_stdlib.items():
        try:
            context[name] = __import__(module_name)
        except ImportError:
            pass

    return context

def format_execution_output(output: str, errors: str, execution_time: float,
                          safety_analysis: Dict[str, Any]) -> str:
    """Format execution output with comprehensive information"""
    result_parts = []

    # Execution summary
    result_parts.append(f"Execution completed in {execution_time:.3f}s")
    result_parts.append(f"Risk Level: {safety_analysis['risk_level'].title()}")

    if safety_analysis['warnings']:
        warning_count = len(safety_analysis['warnings'])
        result_parts.append(f"Warnings: {warning_count}")

    result_parts.append("-" * 40)

    # Standard output
    if output.strip():
        result_parts.append("Output:")
        result_parts.append(output.rstrip())
        result_parts.append("")

    # Error output
    if errors.strip():
        result_parts.append("Errors/Warnings:")
        result_parts.append(errors.rstrip())
        result_parts.append("")

    # Safety warnings (if any)
    if safety_analysis['warnings']:
        result_parts.append("Safety Warnings:")
        for warning in safety_analysis['warnings'][:3]:  # Show first 3
            result_parts.append(f"  Line {warning['line']}: {warning['description']}")

        if len(safety_analysis['warnings']) > 3:
            remaining = len(safety_analysis['warnings']) - 3
            result_parts.append(f"  ... and {remaining} more warnings")
        result_parts.append("")

    # Blender operations summary
    if safety_analysis['blender_operations']:
        result_parts.append("Blender Operations Detected:")
        for op in safety_analysis['blender_operations'][:5]:  # Show first 5
            severity_icon = {"low": "✓", "medium": "⚠", "high": "⚠", "critical": "✗"}
            icon = severity_icon.get(op['severity'], "•")
            result_parts.append(f"  {icon} Line {op['line']}: {op['description']}")
        result_parts.append("")

    # Success message if no output
    if not output.strip() and not errors.strip():
        result_parts.append("✓ Code executed successfully (no output)")

    return "\n".join(result_parts)
