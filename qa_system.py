# qa_system.py
import os
import chromadb
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Helper function to get relevant context (used by all options)
def get_relevant_context(query, n_results=3):
    """Retrieve relevant document chunks based on the query."""
    client = chromadb.PersistentClient("./chroma_db")
    collection = client.get_collection("smc_documentation")
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    context = []
    for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        context.append({
            "content": doc,
            "source": metadata["source"],
            "page": metadata["page"]
        })
    
    return context
    """Generate an answer using OpenAI API with retrieved context."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    context_text = "\n\n".join([f"Document: {ctx['source']}, Page: {ctx['page']}\n{ctx['content']}" 
                               for ctx in context])
    
    system_prompt = """You are an AI assistant for SMC device documentation. 
    Answer the question based on the context provided. 
    If the answer is not in the context, say "I don't have enough information about that in the documentation."
    Always include the source document and page number when providing information."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
    ]
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    
    answer = response.choices[0].message.content
    return answer, context

# Option 2: Simple retrieval only (no LLM)
def simple_answer(query):
    """Simple answering function that just returns relevant contexts."""
    context = get_relevant_context(query, n_results=3)
    answer = f"Here's what I found in the documentation for '{query}':\n\n"
    
    for i, ctx in enumerate(context):
        answer += f"Source: {ctx['source']}, Page {ctx['page']}\n"
        answer += f"Excerpt: {ctx['content'][:300]}...\n\n"
    
    return answer, context

# Option 3: Local LLM using Ollama
def answer_with_local_llm(query, context):
    """Generate an answer using a locally running LLM with Ollama."""
    import requests
    
    context_text = "\n\n".join([f"Document: {ctx['source']}, Page: {ctx['page']}\n{ctx['content']}" 
                               for ctx in context])
    
    prompt = f"""You are an AI assistant for SMC device documentation. 
    Answer the following question based only on the context provided below.
    If the answer is not in the context, say "I don't have enough information about that in the documentation."
    Always include the source document and page number when providing information.
    
    Context:
    {context_text}
    
    Question: {query}
    
    Answer:"""
    
    try:
        # Ollama API call (make sure Ollama is running)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi4",  # Can be changed to other models like mistral, llama3 etc.
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result["response"]
            return answer, context
        else:
            return f"Error: Unable to get response from local LLM (Status code: {response.status_code})", context
    except Exception as e:
        return f"Error: Unable to connect to Ollama. Make sure it's installed and running. Error: {str(e)}", context

if __name__ == "__main__":
    # Test the QA system
    test_query = "How do I reset the device?"
    
    # Choose which method to use
    qa_method = os.getenv("QA_METHOD", "simple").lower()
    
    if qa_method == "local":
        print("Using local LLM for answering...")
        answer, context = answer_with_local_llm(test_query, get_relevant_context(test_query))
    else:
        print("Using simple context retrieval for answering...")
        answer, context = simple_answer(test_query)
    
    print(f"Query: {test_query}")
    print(f"Answer: {answer}")