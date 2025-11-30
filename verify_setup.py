#!/usr/bin/env python3
"""
Setup Verification Script
Tests that all components are properly configured
"""

import os
import sys
import json

def check_python_version():
    """Verify Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro}"
    return False, f"✗ Python version too old: {version.major}.{version.minor}.{version.micro} (need 3.8+)"

def check_dependencies():
    """Check if required packages are installed"""
    results = []
    
    # Check OpenAI
    try:
        import openai
        results.append((True, "✓ OpenAI library installed"))
    except ImportError:
        results.append((False, "✗ OpenAI library not found (pip install openai)"))
    
    # Check Anthropic (optional)
    try:
        import anthropic
        results.append((True, "✓ Anthropic library installed"))
    except ImportError:
        results.append((False, "⚠ Anthropic library not found (optional)"))
    
    # Check Flask (optional)
    try:
        import flask
        results.append((True, "✓ Flask installed"))
    except ImportError:
        results.append((False, "⚠ Flask not found (optional)"))
    
    return results

def check_environment_variables():
    """Check if API keys are configured"""
    results = []
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        masked = openai_key[:8] + '...' + openai_key[-4:] if len(openai_key) > 12 else '***'
        results.append((True, f"✓ OPENAI_API_KEY set: {masked}"))
    else:
        results.append((False, "✗ OPENAI_API_KEY not set"))
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        masked = anthropic_key[:8] + '...' + anthropic_key[-4:] if len(anthropic_key) > 12 else '***'
        results.append((True, f"✓ ANTHROPIC_API_KEY set: {masked}"))
    else:
        results.append((False, "⚠ ANTHROPIC_API_KEY not set (optional)"))
    
    return results

def check_files():
    """Check if required files exist"""
    required_files = [
        'route_checker.py',
        'error_analyzer.py',
        'requirements.txt'
    ]
    
    optional_files = [
        '.github/workflows/deploy.yml',
        'sample_app.py',
        'README.md'
    ]
    
    results = []
    
    for file in required_files:
        if os.path.exists(file):
            results.append((True, f"✓ {file} exists"))
        else:
            results.append((False, f"✗ {file} not found"))
    
    for file in optional_files:
        if os.path.exists(file):
            results.append((True, f"✓ {file} exists"))
        else:
            results.append((False, f"⚠ {file} not found (optional)"))
    
    return results

def test_route_checker():
    """Test route checker functionality"""
    try:
        import subprocess
        
        # Create a simple test file
        test_code = """
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello'

@app.route('/api/test')
def test():
    return 'Test'
"""
        
        with open('_test_app.py', 'w') as f:
            f.write(test_code)
        
        # Run route checker
        result = subprocess.run(
            ['python', 'route_checker.py', '_test_app.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up
        os.remove('_test_app.py')
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get('routes_valid') and len(data.get('routes', [])) == 2:
                    return True, "✓ Route checker working correctly"
                else:
                    return False, f"✗ Route checker found issues: {data}"
            except json.JSONDecodeError:
                return False, f"✗ Route checker output not valid JSON"
        else:
            return False, f"✗ Route checker failed: {result.stderr}"
    
    except Exception as e:
        return False, f"✗ Error testing route checker: {str(e)}"

def test_error_analyzer():
    """Test error analyzer functionality"""
    try:
        import subprocess
        
        test_error = "SyntaxError: invalid syntax at line 10"
        
        result = subprocess.run(
            ['python', 'error_analyzer.py', test_error],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get('success'):
                    return True, "✓ Error analyzer working correctly"
                else:
                    return False, f"✗ Error analyzer failed"
            except json.JSONDecodeError:
                return False, f"✗ Error analyzer output not valid JSON"
        else:
            return False, f"⚠ Error analyzer had issues (may need API key)"
    
    except Exception as e:
        return False, f"⚠ Error testing error analyzer: {str(e)}"

def main():
    print("=" * 60)
    print("AUTO-DEPLOY ASSISTANT - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Python version
    print("1. PYTHON VERSION")
    print("-" * 60)
    passed, message = check_python_version()
    print(message)
    if not passed:
        all_passed = False
    print()
    
    # Dependencies
    print("2. DEPENDENCIES")
    print("-" * 60)
    dep_results = check_dependencies()
    for passed, message in dep_results:
        print(message)
        if not passed and "✗" in message:
            all_passed = False
    print()
    
    # Environment variables
    print("3. ENVIRONMENT VARIABLES")
    print("-" * 60)
    env_results = check_environment_variables()
    for passed, message in env_results:
        print(message)
        if not passed and "✗" in message:
            all_passed = False
    print()
    
    # Files
    print("4. REQUIRED FILES")
    print("-" * 60)
    file_results = check_files()
    for passed, message in file_results:
        print(message)
        if not passed and "✗" in message:
            all_passed = False
    print()
    
    # Test route checker
    print("5. ROUTE CHECKER TEST")
    print("-" * 60)
    if os.path.exists('route_checker.py'):
        passed, message = test_route_checker()
        print(message)
        if not passed:
            all_passed = False
    else:
        print("⚠ Skipping (route_checker.py not found)")
    print()
    
    # Test error analyzer
    print("6. ERROR ANALYZER TEST")
    print("-" * 60)
    if os.path.exists('error_analyzer.py'):
        passed, message = test_error_analyzer()
        print(message)
        # Don't fail if API key is missing
    else:
        print("⚠ Skipping (error_analyzer.py not found)")
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✓ ALL CRITICAL CHECKS PASSED!")
        print("\nYou're ready to start implementing!")
        print("\nNext steps:")
        print("  1. Setup GitHub repository")
        print("  2. Create Airtable base")
        print("  3. Configure Zapier workflow")
        print("  4. Test end-to-end")
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues marked with ✗ above")
        print("Issues marked with ⚠ are optional")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
