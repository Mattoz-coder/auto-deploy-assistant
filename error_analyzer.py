#!/usr/bin/env python3
"""
Error Analyzer Script
Uses LLM to analyze build errors and generate fix suggestions
"""

import os
import sys
import json
import re
from datetime import datetime

# Check if OpenAI library is available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai library not installed. Install with: pip install openai", file=sys.stderr)

# Alternative: Anthropic Claude
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

def extract_code_context(file_path, line_number, context_lines=5):
    """Extract code snippet around the error location"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        code_snippet = ''.join(lines[start:end])
        return {
            'code': code_snippet,
            'start_line': start + 1,
            'end_line': end,
            'error_line': line_number
        }
    except Exception as e:
        return {
            'code': '',
            'error': f'Could not extract code: {str(e)}'
        }

def parse_error_log(error_log):
    """Parse error log to extract key information"""
    # Common error patterns
    python_error = re.search(r'File "(.+?)", line (\d+)', error_log)
    js_error = re.search(r'at (.+?):(\d+):(\d+)', error_log)
    
    error_info = {
        'error_type': 'Unknown',
        'file_path': None,
        'line_number': None,
        'message': error_log
    }
    
    # Extract error type
    if 'SyntaxError' in error_log:
        error_info['error_type'] = 'SyntaxError'
    elif 'TypeError' in error_log:
        error_info['error_type'] = 'TypeError'
    elif 'ImportError' in error_log or 'ModuleNotFoundError' in error_log:
        error_info['error_type'] = 'ImportError'
    elif 'NameError' in error_log:
        error_info['error_type'] = 'NameError'
    elif 'AttributeError' in error_log:
        error_info['error_type'] = 'AttributeError'
    
    # Extract file and line for Python
    if python_error:
        error_info['file_path'] = python_error.group(1)
        error_info['line_number'] = int(python_error.group(2))
    
    # Extract file and line for JavaScript
    elif js_error:
        error_info['file_path'] = js_error.group(1)
        error_info['line_number'] = int(js_error.group(2))
    
    return error_info

def analyze_with_openai(error_log, code_snippet):
    """Use OpenAI to analyze error and generate suggestions"""
    if not OPENAI_AVAILABLE:
        return "OpenAI library not available"
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "OPENAI_API_KEY environment variable not set"
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Analyze this build error and provide actionable fix suggestions:

ERROR LOG:
{error_log}

CODE SNIPPET:
{code_snippet}

Please provide:
1. Root cause of the error
2. Specific fix suggestions (2-3 options)
3. Code example of the fix if applicable

Keep suggestions concise and actionable."""

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'You are a helpful coding assistant that analyzes errors and suggests fixes.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

def analyze_with_anthropic(error_log, code_snippet):
    """Use Anthropic Claude to analyze error and generate suggestions"""
    if not ANTHROPIC_AVAILABLE:
        return "Anthropic library not available"
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return "ANTHROPIC_API_KEY environment variable not set"
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Analyze this build error and provide actionable fix suggestions:

ERROR LOG:
{error_log}

CODE SNIPPET:
{code_snippet}

Please provide:
1. Root cause of the error
2. Specific fix suggestions (2-3 options)
3. Code example of the fix if applicable

Keep suggestions concise and actionable."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"Error calling Anthropic API: {str(e)}"

def generate_fallback_suggestions(error_info):
    """Generate basic suggestions without AI"""
    error_type = error_info.get('error_type', 'Unknown')
    
    suggestions = {
        'SyntaxError': [
            'Check for missing parentheses, brackets, or quotes',
            'Verify proper indentation (especially in Python)',
            'Look for unclosed code blocks'
        ],
        'ImportError': [
            'Verify the module is installed: pip install <module>',
            'Check if the import path is correct',
            'Ensure the module is in your requirements.txt'
        ],
        'TypeError': [
            'Check if you\'re passing the correct data types',
            'Verify function arguments match expected types',
            'Review type conversions (str, int, float, etc.)'
        ],
        'NameError': [
            'Check if the variable is defined before use',
            'Verify correct spelling of variable names',
            'Ensure variable is in correct scope'
        ],
        'AttributeError': [
            'Verify the object has the attribute you\'re accessing',
            'Check if object is None before accessing attributes',
            'Review the object\'s available methods and properties'
        ]
    }
    
    return suggestions.get(error_type, [
        'Review the error message carefully',
        'Check the documentation for the failing component',
        'Try searching for similar errors online'
    ])

def main():
    # Get error log from command line or stdin
    if len(sys.argv) > 1:
        error_log = sys.argv[1]
    else:
        error_log = sys.stdin.read()
    
    if not error_log.strip():
        print(json.dumps({
            'success': False,
            'error': 'No error log provided'
        }))
        sys.exit(1)
    
    # Parse error information
    error_info = parse_error_log(error_log)
    
    # Extract code context if file path is available
    code_context = None
    if error_info['file_path'] and error_info['line_number']:
        code_context = extract_code_context(
            error_info['file_path'],
            error_info['line_number']
        )
    
    # Generate AI suggestions
    ai_suggestions = None
    if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        ai_suggestions = analyze_with_openai(
            error_log,
            code_context['code'] if code_context else ''
        )
    elif ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
        ai_suggestions = analyze_with_anthropic(
            error_log,
            code_context['code'] if code_context else ''
        )
    
    # Generate fallback suggestions
    fallback_suggestions = generate_fallback_suggestions(error_info)
    
    # Build result
    result = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'error_info': error_info,
        'code_context': code_context,
        'ai_suggestions': ai_suggestions,
        'fallback_suggestions': fallback_suggestions,
        'ai_provider': 'openai' if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY') 
                      else 'anthropic' if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY')
                      else 'none'
    }
    
    # Output JSON result
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
