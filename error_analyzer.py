#!/usr/bin/env python3
"""
AI-Powered Error Analysis using FREE Google Gemini
"""

import os
import sys
import json
from datetime import datetime

def analyze_error_with_gemini(error_message):
    """Analyze error using FREE Google Gemini API"""
    try:
        import requests
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return None
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        prompt = f"""Analyze this programming error and provide fix suggestions in JSON format:

Error: {error_message}

Respond with ONLY valid JSON (no markdown, no code blocks):
{{
  "root_cause": "brief explanation",
  "solutions": [
    {{
      "option": 1,
      "title": "solution title",
      "description": "detailed explanation",
      "code_example": "code snippet"
    }}
  ]
}}"""

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up response
            ai_text = ai_text.strip()
            if '```json' in ai_text:
                ai_text = ai_text.split('```json')[1].split('```')[0]
            elif '```' in ai_text:
                ai_text = ai_text.split('```')[1].split('```')[0]
            
            try:
                return json.loads(ai_text.strip())
            except:
                return {"analysis": ai_text}
        else:
            return None
            
    except Exception as e:
        print(f"Gemini API error: {e}", file=sys.stderr)
        return None

def get_fallback_suggestions(error_type):
    """Provide fallback suggestions when AI is unavailable"""
    
    common_suggestions = {
        "SyntaxError": [
            "Check for missing parentheses, brackets, or quotes",
            "Verify proper indentation",
            "Look for unclosed code blocks or missing colons"
        ],
        "ImportError": [
            "Verify the module is installed: pip install <module_name>",
            "Check if the module name is spelled correctly",
            "Ensure the module is in your Python path"
        ],
        "NameError": [
            "Check if the variable is defined before use",
            "Verify the variable name spelling",
            "Ensure the variable is in the correct scope"
        ],
        "default": [
            "Read the error message carefully",
            "Check the line number mentioned",
            "Review recent code changes",
            "Search for the error online"
        ]
    }
    
    return common_suggestions.get(error_type, common_suggestions["default"])

def analyze_error(error_message):
    """Main function to analyze errors"""
    
    error_type = error_message.split(':')[0].strip() if ':' in error_message else "Unknown"
    
    result = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "error_info": {
            "error_type": error_type,
            "message": error_message
        },
        "ai_provider": "google-gemini"
    }
    
    ai_suggestions = analyze_error_with_gemini(error_message)
    
    if ai_suggestions:
        result["ai_suggestions"] = ai_suggestions
        result["fallback_used"] = False
    else:
        result["ai_suggestions"] = "AI unavailable"
        result["fallback_suggestions"] = get_fallback_suggestions(error_type)
        result["fallback_used"] = True
    
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python error_analyzer.py \"error message\"")
        sys.exit(1)
    
    result = analyze_error(sys.argv[1])
    print(json.dumps(result, indent=2))