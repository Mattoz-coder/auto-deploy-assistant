"""
Sample Flask Application for Testing Route Checker
This app intentionally has some routes for testing the auto-deploy system
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Auto-Deploy Assistant Demo',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/api/deployments')
def get_deployments():
    """Get deployment history"""
    return jsonify({
        'deployments': [
            {'id': 1, 'status': 'success', 'timestamp': '2025-01-01T10:00:00Z'},
            {'id': 2, 'status': 'success', 'timestamp': '2025-01-01T11:00:00Z'}
        ]
    })

@app.route('/api/errors')
def get_errors():
    """Get error history"""
    return jsonify({
        'errors': [
            {'id': 1, 'type': 'SyntaxError', 'resolved': True},
            {'id': 2, 'type': 'ImportError', 'resolved': False}
        ]
    })

@app.route('/api/routes')
def list_routes():
    """List all available routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify({'routes': routes})

# This route has an issue - duplicate path (intentional for testing)
@app.route('/api/test')
def test_route_1():
    return jsonify({'test': 'route 1'})

# Uncomment to create duplicate route error for testing
# @app.route('/api/test')
# def test_route_2():
#     return jsonify({'test': 'route 2'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
