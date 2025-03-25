# app.py
"""
Flask web application for SMC Documentation Q&A System.
"""
from flask import Flask, request, jsonify, send_from_directory
import os
import json
import time
import logging
import werkzeug

from qa_system import answer_with_local_llm, get_relevant_context
from config import (
    DEBUG_MODE, HOST, PORT, OLLAMA_MODEL, LLAVA_MODEL, 
    LOG_LEVEL, COLLECTION_NAME
)

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger("app")

# Filter out frequent status endpoint requests from the werkzeug logger
class StatusEndpointFilter(logging.Filter):
    def filter(self, record):
        return not (record.getMessage().find('/status') != -1 and record.levelname == 'INFO')

# Apply the filter to werkzeug logger
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.addFilter(StatusEndpointFilter())

# Initialize Flask app
app = Flask(__name__)

# Main route - serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React frontend."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, "react", path)):
        return send_from_directory(os.path.join(app.static_folder, "react"), path)
    return send_from_directory(os.path.join(app.static_folder, "react"), "index.html")

@app.route('/ask', methods=['POST'])
def ask():
    """API endpoint to handle user questions."""
    try:
        # Extract query from request
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'error': 'Query is required',
                'answer': 'Please provide a question about SMC devices.',
                'sources': []
            }), 400
        
        # Log the query
        logger.info(f"Received query: {query}")
        start_time = time.time()
        
        # Get answer using the local LLM
        answer, context = answer_with_local_llm(query)
        
        # Log timing information
        elapsed = time.time() - start_time
        logger.info(f"Query answered in {elapsed:.2f} seconds")
        
        # Format response for the frontend
        sources = []
        for ctx in context:
            source_info = {
                'document': ctx['source'],
                'page': ctx['page']
            }
            
            # Add extra metadata if available
            if 'heading' in ctx and ctx['heading']:
                source_info['section'] = ctx['heading']
                
            sources.append(source_info)
        
        return jsonify({
            'answer': answer,
            'sources': sources,
            'timing': {
                'total_seconds': round(elapsed, 2)
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'answer': 'Sorry, there was an error processing your request.',
            'sources': []
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """API endpoint to check the system status."""
    try:
        import requests
        import chromadb
        
        status = {
            'system': 'online',
            'ollama': 'unknown',
            'vectordb': 'unknown',
            'chat_model': OLLAMA_MODEL,
            'vision_model': LLAVA_MODEL
        }
        
        # Check ChromaDB
        try:
            client = chromadb.PersistentClient("./chroma_db")
            collection = client.get_collection(COLLECTION_NAME)
            count = collection.count()
            status['vectordb'] = 'online'
            status['document_count'] = count
        except Exception as e:
            status['vectordb'] = f'error: {str(e)}'
        
        # Check Ollama
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                models = response.json()
                status['ollama'] = 'online'
                status['available_models'] = [m['name'] for m in models.get('models', [])]
            else:
                status['ollama'] = f'error: status code {response.status_code}'
        except Exception as e:
            status['ollama'] = f'error: {str(e)}'
            
        return jsonify(status)
    
    except Exception as e:
        return jsonify({
            'system': 'error',
            'error': str(e)
        })

@app.route('/feedback', methods=['POST'])
def feedback():
    """Store user feedback for future improvement."""
    try:
        data = request.json
        query = data.get('query', '')
        answer = data.get('answer', '')
        rating = data.get('rating', 0)
        comment = data.get('comment', '')
        
        # Create feedback directory if it doesn't exist
        os.makedirs('feedback', exist_ok=True)
        
        # Save feedback to file
        timestamp = int(time.time())
        feedback_file = f'feedback/feedback_{timestamp}.json'
        
        with open(feedback_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'query': query,
                'answer': answer,
                'rating': rating,
                'comment': comment
            }, f, indent=2)
            
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting SMC Documentation Assistant on {HOST}:{PORT}")
    logger.info(f"Using Ollama model for chat: {OLLAMA_MODEL}")
    logger.info(f"Using LLaVA model for document processing: {LLAVA_MODEL}")
    logger.info(f"Vector database collection: {COLLECTION_NAME}")
    app.run(debug=DEBUG_MODE, host=HOST, port=PORT)