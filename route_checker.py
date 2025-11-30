#!/usr/bin/env python3
"""
Route Checker Script
Analyzes application code to verify routing configuration
"""

import json
import re
import sys
import os
from pathlib import Path

def check_flask_routes(file_path):
    """Check Flask application routes"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Find Flask route decorators
        routes = re.findall(r'@app\.route\(["\'](.+?)["\']\)', code)
        
        issues = []
        
        # Check for common issues
        if not routes:
            issues.append("No routes found in application")
        
        # Check for duplicate routes
        duplicate_routes = [r for r in routes if routes.count(r) > 1]
        if duplicate_routes:
            issues.append(f"Duplicate routes found: {set(duplicate_routes)}")
        
        # Check for routes with no function
        route_functions = re.findall(r'@app\.route\(["\'].+?["\']\)\s*def\s+(\w+)', code)
        if len(routes) != len(route_functions):
            issues.append("Some routes may not have associated functions")
        
        return {
            'routes_valid': len(issues) == 0,
            'routes': routes,
            'route_count': len(routes),
            'issues': issues,
            'framework': 'Flask'
        }
    except Exception as e:
        return {
            'routes_valid': False,
            'routes': [],
            'route_count': 0,
            'issues': [f"Error reading file: {str(e)}"],
            'framework': 'Unknown'
        }

def check_express_routes(file_path):
    """Check Express.js application routes"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Find Express route definitions
        get_routes = re.findall(r'app\.get\(["\'](.+?)["\']\s*,', code)
        post_routes = re.findall(r'app\.post\(["\'](.+?)["\']\s*,', code)
        all_routes = get_routes + post_routes
        
        issues = []
        
        if not all_routes:
            issues.append("No routes found in application")
        
        # Check for duplicate routes
        duplicate_routes = [r for r in all_routes if all_routes.count(r) > 1]
        if duplicate_routes:
            issues.append(f"Duplicate routes found: {set(duplicate_routes)}")
        
        return {
            'routes_valid': len(issues) == 0,
            'routes': all_routes,
            'route_count': len(all_routes),
            'get_routes': len(get_routes),
            'post_routes': len(post_routes),
            'issues': issues,
            'framework': 'Express.js'
        }
    except Exception as e:
        return {
            'routes_valid': False,
            'routes': [],
            'route_count': 0,
            'issues': [f"Error reading file: {str(e)}"],
            'framework': 'Unknown'
        }

def check_directory_routes(directory_path):
    """Check routes in a directory of files"""
    results = []
    issues = []
    
    # Look for Python files
    python_files = list(Path(directory_path).rglob('*.py'))
    for py_file in python_files:
        result = check_flask_routes(str(py_file))
        if result['route_count'] > 0:
            results.append({
                'file': str(py_file),
                'result': result
            })
    
    # Look for JavaScript files
    js_files = list(Path(directory_path).rglob('*.js'))
    for js_file in js_files:
        result = check_express_routes(str(js_file))
        if result['route_count'] > 0:
            results.append({
                'file': str(js_file),
                'result': result
            })
    
    if not results:
        issues.append("No route files found in directory")
    
    total_routes = sum(r['result']['route_count'] for r in results)
    all_valid = all(r['result']['routes_valid'] for r in results)
    
    return {
        'routes_valid': all_valid and len(issues) == 0,
        'total_routes': total_routes,
        'files_checked': len(results),
        'results': results,
        'issues': issues
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'routes_valid': False,
            'error': 'No file or directory path provided',
            'usage': 'python route_checker.py <file_or_directory_path>'
        }))
        sys.exit(1)
    
    path = sys.argv[1]
    
    if not os.path.exists(path):
        print(json.dumps({
            'routes_valid': False,
            'error': f'Path does not exist: {path}'
        }))
        sys.exit(1)
    
    # Check if it's a directory or file
    if os.path.isdir(path):
        result = check_directory_routes(path)
    else:
        # Determine file type and check accordingly
        if path.endswith('.py'):
            result = check_flask_routes(path)
        elif path.endswith('.js'):
            result = check_express_routes(path)
        else:
            result = {
                'routes_valid': False,
                'error': 'Unsupported file type. Use .py or .js files'
            }
    
    # Output JSON result
    print(json.dumps(result, indent=2))
    
    # Return appropriate exit code
    sys.exit(0 if result.get('routes_valid', False) else 1)

if __name__ == '__main__':
    main()
