#!/usr/bin/env python3
"""
AI-Powered Error Analysis using FREE Groq API
"""

import os
import sys
import json
from datetime import datetime

def analyze_error_with_groq(error_message):
    """Analyze error using FREE Groq API"""
    try:
        import requests
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return None
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analyze this programming error and provide fix suggestions.

Error: {error_message}

Provide a JSON response with:
1. root_cause: Brief explanation of why this error occurred
2. solutions: Array of 3 solution objects, each with:
   - option: number (1, 2, 3)
   - title: short title
   - description: detailed explanation
   - code_example: code snippet showing the fix

Respond with valid JSON only, no markdown formatting."""

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert software debugging assistant. Provide clear, actionable solutions in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result['choices'][0]['message']['content']
            
            # Clean up response - remove markdown if present
            ai_text = ai_text.strip()
            if '```json' in ai_text:
                ai_text = ai_text.split('```json')[1].split('```')[0]
            elif '```' in ai_text:
                ai_text = ai_text.split('```')[1].split('```')[0]
            
            # Parse JSON
            try:
                ai_suggestions = json.loads(ai_text.strip())
                return ai_suggestions
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text
                return {"analysis": ai_text}
        else:
            error_detail = response.text
            print(f"Groq API error: {response.status_code} - {error_detail}", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error calling Groq API: {e}", file=sys.stderr)
        return None


def get_fallback_suggestions(error_type):
    """Provide fallback suggestions when AI is unavailable"""
    
    common_suggestions = {
        "SyntaxError": [
            "Check for missing parentheses, brackets, or quotes",
            "Verify proper indentation (Python requires consistent indentation)",
            "Look for unclosed code blocks or missing colons after function/class definitions"
        ],
        "ImportError": [
            "Verify the module is installed: pip install <module_name>",
            "Check if the module name is spelled correctly",
            "Ensure the module is in your Python path or virtual environment"
        ],
        "ModuleNotFoundError": [
            "Install the missing module: pip install <module_name>",
            "Check your virtual environment is activated",
            "Verify the package name (some packages have different import names)"
        ],
        "NameError": [
            "Check if the variable is defined before use",
            "Verify the variable name spelling (Python is case-sensitive)",
            "Ensure the variable is in the correct scope (not defined inside a function when used outside)"
        ],
        "TypeError": [
            "Check the data types being used in the operation",
            "Verify function arguments match expected types",
            "Look for missing or extra function arguments"
        ],
        "AttributeError": [
            "Verify the object has the attribute you are trying to access",
            "Check for typos in attribute names",
            "Ensure the object is properly initialized before accessing attributes"
        ],
        "IndexError": [
            "Check that your index is within the valid range of the list/array",
            "Remember that Python uses 0-based indexing",
            "Verify the list/array is not empty before accessing elements"
        ],
        "KeyError": [
            "Check that the dictionary key exists before accessing it",
            "Use dict.get(key, default) for safer dictionary access",
            "Verify the key spelling and type (keys are case-sensitive)"
        ],
        "ValueError": [
            "Check that the value being passed is of the correct format",
            "Verify conversions between data types (e.g., string to integer)",
            "Ensure the value is within the expected range"
        ],
        "default": [
            "Read the error message carefully for specific clues about the issue",
            "Check the line number mentioned in the error",
            "Review recent code changes that might have introduced the error",
            "Search for the exact error message online for similar cases",
            "Check documentation for the function or feature causing the error"
        ]
    }
    
    return common_suggestions.get(error_type, common_suggestions["default"])


def analyze_error(error_message):
    """Main function to analyze errors with AI and fallback"""
    
    # Extract error type from message
    error_type = error_message.split(':')[0].strip() if ':' in error_message else "Unknown"
    
    result = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "error_info": {
            "error_type": error_type,
            "message": error_message
        },
        "ai_provider": "groq-llama-3.3-70b"
    }
    
    # Try AI analysis first
    ai_suggestions = analyze_error_with_groq(error_message)
    
    if ai_suggestions:
        result["ai_suggestions"] = ai_suggestions
        result["fallback_used"] = False
        result["status"] = "AI analysis successful"
    else:
        result["ai_suggestions"] = "AI analysis unavailable - using intelligent fallback"
        result["fallback_suggestions"] = get_fallback_suggestions(error_type)
        result["fallback_used"] = True
        result["status"] = "Using fallback suggestions"
    
    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python error_analyzer.py \"error message\"")
        print("\nExample:")
        print('  python error_analyzer.py "ImportError: No module named flask"')
        sys.exit(1)
    
    error_message = sys.argv[1]
    
    result = analyze_error(error_message)
    
    # Pretty print JSON output
    print(json.dumps(result, indent=2))