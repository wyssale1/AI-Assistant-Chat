# app.py
from flask import Flask, render_template, request, jsonify, Response
from qa_system import answer_with_local_llm, get_relevant_context
import os
import json
import time
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger("app")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
DEBUG_MODE = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

@app.route('/')
def index():
    """Render the main page."""
    # Get model info for display
    model_name = os.getenv("OLLAMA_MODEL", "phi4")
    return render_template('index.html', model=model_name)

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
            'model': os.getenv("OLLAMA_MODEL", "phi4")
        }
        
        # Check ChromaDB
        try:
            client = chromadb.PersistentClient("./chroma_db")
            collection = client.get_collection("smc_documentation")
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
    logger.info(f"Using Ollama model: {os.getenv('OLLAMA_MODEL', 'phi4')}")
    app.run(debug=DEBUG_MODE, host=HOST, port=PORT)