"""
CASEMATRIX AI - BACKEND FLASK APPLICATION
===========================================

Main Flask Application

This is the core backend server that:
1. Serves the web interface
2. Handles user queries via REST API
3. Orchestrates the RAG pipeline
4. Returns retrieved cases and generated responses

Author: Clinical AI Team
Date: 2024
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from rag_pipeline import get_rag_pipeline
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__, 
           template_folder='../frontend/templates',
           static_folder='../frontend/static')

# Enable CORS for cross-origin requests
CORS(app)

# Initialize RAG pipeline on startup
print("[APP] Initializing RAG Pipeline...")
rag_pipeline = get_rag_pipeline()
print("[APP] RAG Pipeline ready!")


# ==================== ROUTES ====================

@app.route('/')
def home():
    """
    Serve the main home page.
    
    Returns:
        Rendered index.html template
    """
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify server is running.
    
    Returns:
        JSON with server status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CaseMatrix AI - Backend API'
    }), 200


@app.route('/query', methods=['POST'])
def query_handler():
    """
    Main query endpoint for clinical case retrieval.
    This is the primary endpoint for frontend-backend communication.
    
    Request body (JSON):
    {
        "query": "Patient presenting with chest pain and shortness of breath",
        "num_results": 5  (optional, default: 5)
    }
    
    Returns:
        JSON response with retrieved cases and generated response
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query',
                'message': 'Please provide a clinical query'
            }), 400
        
        query = data.get('query', '').strip()
        num_results = int(data.get('num_results', 5))
        
        # Validate query
        if not query:
            return jsonify({
                'error': 'Empty query',
                'message': 'Please enter a clinical query'
            }), 400
        
        if len(query) > 1000:
            return jsonify({
                'error': 'Query too long',
                'message': 'Query must be less than 1000 characters'
            }), 400
        
        if num_results < 1 or num_results > 10:
            num_results = 5
        
        print(f"\n[API] Processing query: {query[:100]}...")
        
        # Process query through RAG pipeline
        result = rag_pipeline.process_query(query, num_results)
        
        return jsonify({
            'success': True,
            'query': result['query'],
            'retrieved_cases': result['retrieved_cases'],
            'response': result['response'],
            'num_results': result['num_results'],
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Exception in /query: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def search_cases():
    """
    Legacy search endpoint (for backward compatibility).
    Redirects to /query endpoint.
    
    This maintains compatibility with older frontend code.
    """
    return query_handler()


@app.route('/api/cases/stats', methods=['GET'])
def get_cases_stats():
    """
    Get statistics about indexed clinical cases.
    
    Returns:
        JSON with case statistics
    """
    try:
        if rag_pipeline.collection is None:
            return jsonify({'error': 'Collection not initialized'}), 500
        
        count = rag_pipeline.collection.count()
        
        return jsonify({
            'success': True,
            'total_cases': count,
            'embedding_model': 'all-MiniLM-L6-v2',
            'embedding_dimension': rag_pipeline.embedding_generator.get_embedding_dimension()
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Exception in /api/cases/stats: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'message': str(e)
        }), 500


@app.route('/api/cases/list', methods=['GET'])
def list_all_cases():
    """
    List all available clinical cases (for reference).
    
    Returns:
        JSON with list of all cases in database
    """
    try:
        cases = rag_pipeline.load_clinical_data()
        
        return jsonify({
            'success': True,
            'total_cases': len(cases),
            'cases': cases
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Exception in /api/cases/list: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve cases',
            'message': str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    """
    Run the Flask application.
    
    Configuration:
    - host: '127.0.0.1' - Localhost only (secure for development)
    - port: 5000 - Default Flask development port
    - debug: True - Enable auto-reload and better error messages
    """
    print("\n" + "="*60)
    print("CaseMatrix AI - Backend API Server")
    print("="*60)
    print("[APP] Starting backend server...")
    print("[APP] Frontend should call: http://127.0.0.1:5000/query")
    print("[APP] Health check: http://127.0.0.1:5000/api/health")
    print("[APP] Available endpoints:")
    print("  - POST /query - Process clinical query")
    print("  - POST /api/search - Legacy search endpoint")
    print("  - GET /api/cases/stats - Database statistics")
    print("  - GET /api/cases/list - List all cases")
    print("  - GET / - Serve frontend (if accessed from browser)")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
