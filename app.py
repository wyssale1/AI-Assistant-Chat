# app.py
from flask import Flask, render_template, request, jsonify
from qa_system import answer_with_openai, simple_answer,answer_with_local_llm, get_relevant_context
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    query = request.json['query']
    
    # Choose which answering method to use based on environment variable
    qa_method = os.getenv("QA_METHOD", "simple").lower()
    
    if qa_method == "openai" and os.getenv("OPENAI_API_KEY"):
        answer, context = answer_with_openai(query, get_relevant_context(query))
    elif qa_method == "local":
        answer, context = answer_with_local_llm(query, get_relevant_context(query))
    else:
        answer, context = simple_answer(query)
    
    return jsonify({
        'answer': answer,
        'sources': [{'document': ctx['source'], 'page': ctx['page']} for ctx in context]
    })

if __name__ == '__main__':
    app.run(debug=True)