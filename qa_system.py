# qa_system.py
import os
import json
import time
import hashlib
import chromadb
from dotenv import load_dotenv
import requests
from functools import lru_cache
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("qa_system.log"), logging.StreamHandler()]
)
logger = logging.getLogger("qa_system")

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "8000"))
N_RESULTS = int(os.getenv("N_RESULTS", "5"))
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "100"))
USE_STREAMING = os.getenv("USE_STREAMING", "false").lower() == "true"

# Cache directory
CACHE_DIR = "response_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_relevant_context(query, n_results=N_RESULTS, rerank=True):
    """
    Retrieve and potentially rerank relevant document chunks based on the query.
    
    Args:
        query: The user's question
        n_results: Number of chunks to retrieve
        rerank: Whether to rerank results by relevance score
        
    Returns:
        List of context objects with content and metadata
    """
    try:
        client = chromadb.PersistentClient("./chroma_db")
        collection = client.get_collection("smc_documentation")
        
        # Get more results than needed for reranking
        fetch_count = n_results * 2 if rerank else n_results
        
        results = collection.query(
            query_texts=[query],
            n_results=fetch_count,
            include=["documents", "metadatas", "distances"]
        )
        
        context = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0], 
            results["metadatas"][0],
            results["distances"][0]
        )):
            # Calculate a relevance score (inverted distance)
            relevance = 1.0 - (distance / 2.0)  # Normalize to 0-1 scale
            
            context.append({
                "content": doc,
                "source": metadata["source"],
                "page": metadata.get("page", 0),
                "heading": metadata.get("heading", ""),
                "relevance": relevance
            })
        
        # Rerank results if enabled
        if rerank:
            # Simple keyword-based reranking
            query_terms = set(query.lower().split())
            
            for ctx in context:
                # Count query terms in content
                content_lower = ctx["content"].lower()
                term_matches = sum(1 for term in query_terms if term in content_lower)
                
                # Adjust relevance score based on term matches
                ctx["relevance"] = ctx["relevance"] * (1.0 + 0.1 * term_matches)
            
            # Sort by adjusted relevance and take top n_results
            context = sorted(context, key=lambda x: x["relevance"], reverse=True)[:n_results]
        
        return context
    
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return []

def format_context_for_llm(context, max_length=CONTEXT_WINDOW):
    """Format context data for the LLM prompt with smart truncation."""
    formatted_chunks = []
    total_length = 0
    
    # First pass: format all chunks with metadata
    for i, ctx in enumerate(context):
        chunk = f"Document: {ctx['source']}, Page: {ctx['page']}\n"
        if ctx.get("heading"):
            chunk += f"Section: {ctx['heading']}\n"
        
        # Truncate very long content chunks
        content = ctx['content']
        if len(content) > 1500:
            content = content[:1450] + "... [content truncated]"
            
        chunk += f"{content}\n\n"
        
        # Add to our list with relevance as priority
        formatted_chunks.append({
            "text": chunk,
            "relevance": ctx.get("relevance", 0),
            "length": len(chunk)
        })
    
    # Sort chunks by relevance
    formatted_chunks.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Second pass: build context string respecting max length
    context_text = ""
    for chunk in formatted_chunks:
        # If adding this chunk would exceed our max length, skip it
        if total_length + chunk["length"] > max_length:
            # But always include at least one chunk
            if total_length == 0:
                context_text = chunk["text"][:max_length]
                break
            else:
                continue
                
        context_text += chunk["text"]
        total_length += chunk["length"]
    
    return context_text

def generate_llm_prompt(query, context_text):
    """Generate a well-structured prompt for the LLM."""
    return f"""You are a precise, helpful assistant for SMC device documentation. 
Your task is to answer the user's question about SMC devices by carefully analyzing the provided context.

INSTRUCTION GUIDELINES:
1. Answer ONLY based on the information in the context below
2. If the answer isn't in the context, say "I don't have enough information about that in the documentation."
3. ALWAYS cite your sources with document names and page numbers after each relevant piece of information
4. Be direct and concise in your answers
5. If context contains conflicting information, acknowledge it and explain the discrepancy
6. When providing steps or procedures, use numbered lists
7. Format your answer for clarity

CONTEXT:
{context_text}

USER QUESTION: {query}

YOUR ANSWER:"""

def get_cached_response(query, context):
    """Check for cached response to avoid duplicate API calls."""
    # Create a unique hash of the query and context
    context_str = json.dumps([c["content"] for c in context])
    combined = query + context_str
    hash_key = hashlib.md5(combined.encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{hash_key}.json")
    
    # Check if we have a cached response
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Check if cache is still valid (less than 1 day old)
            if time.time() - cache_data.get("timestamp", 0) < 86400:
                logger.info(f"Using cached response for: {query[:50]}...")
                return cache_data.get("response")
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
    
    return None

def save_to_cache(query, context, response):
    """Save response to cache."""
    try:
        # Create a unique hash of the query and context
        context_str = json.dumps([c["content"] for c in context])
        combined = query + context_str
        hash_key = hashlib.md5(combined.encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{hash_key}.json")
        
        cache_data = {
            "query": query,
            "timestamp": time.time(),
            "response": response
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
            
        # Cleanup old cache files if we have too many
        cache_files = os.listdir(CACHE_DIR)
        if len(cache_files) > CACHE_SIZE:
            # Remove oldest files based on modification time
            cache_files = [os.path.join(CACHE_DIR, f) for f in cache_files]
            cache_files.sort(key=os.path.getmtime)
            for old_file in cache_files[:len(cache_files) - CACHE_SIZE]:
                os.remove(old_file)
                
    except Exception as e:
        logger.warning(f"Error saving to cache: {str(e)}")

def answer_with_local_llm(query, context=None):
    """
    Generate an answer using a locally running LLM with Ollama.
    
    Args:
        query: The user's question
        context: Optional pre-retrieved context (if None, retrieves context)
        
    Returns:
        Tuple of (answer, context)
    """
    # Get context if not provided
    if context is None:
        context = get_relevant_context(query)
    
    # Check if we have enough context
    if not context:
        return "I couldn't find any relevant information in the documentation for your question.", []
    
    # Check cache first
    cached_response = get_cached_response(query, context)
    if cached_response:
        return cached_response, context
        
    # Format context for the LLM
    context_text = format_context_for_llm(context)
    
    # Generate prompt
    prompt = generate_llm_prompt(query, context_text)
    
    # Prepare the API request
    request_body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": USE_STREAMING,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS
        }
    }
    
    try:
        start_time = time.time()
        logger.info(f"Sending request to Ollama: {OLLAMA_MODEL}")
        
        # Make the API call
        response = requests.post(
            OLLAMA_URL,
            json=request_body,
            timeout=180  # 3-minute timeout
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Ollama response received in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract answer from response
            if USE_STREAMING:
                # For streaming, concatenate all the responses
                answer = "".join([r.get("response", "") for r in result])
            else:
                answer = result.get("response", "")
            
            # Post-process answer
            answer = post_process_answer(answer, context)
            
            # Cache the result
            save_to_cache(query, context, answer)
            
            return answer, context
        else:
            error_msg = f"Error: Unable to get response from Ollama (Status code: {response.status_code})"
            logger.error(error_msg)
            return error_msg, context
            
    except requests.exceptions.Timeout:
        error_msg = "Error: Request to Ollama timed out. The query might be too complex or the system is overloaded."
        logger.error(error_msg)
        return error_msg, context
        
    except requests.exceptions.ConnectionError:
        error_msg = "Error: Unable to connect to Ollama. Make sure it's installed and running on your system."
        logger.error(error_msg)
        return error_msg, context
        
    except Exception as e:
        error_msg = f"Error: An unexpected error occurred: {str(e)}"
        logger.error(error_msg)
        return error_msg, context

def post_process_answer(answer, context):
    """Clean up and improve the LLM's answer."""
    # Ensure proper citation format
    for ctx in context:
        source = ctx['source']
        page = ctx['page']
        
        # Check if source is mentioned but not properly formatted
        if source in answer and f"({source}, Page {page})" not in answer:
            # Try to add the page number where the source is mentioned
            answer = answer.replace(f"{source}", f"{source}, Page {page}")
    
    # Sometimes the model repeats "I don't have enough information"
    if answer.count("I don't have enough information") > 1:
        # Keep only the first instance
        first_idx = answer.find("I don't have enough information")
        end_idx = answer.find("\n", first_idx)
        if end_idx > 0:
            answer = answer[:end_idx]
    
    return answer

# Simple retrieval function for fallback
def simple_answer(query):
    """Simple answering function that just returns relevant contexts."""
    context = get_relevant_context(query, n_results=5)
    
    if not context:
        return "I couldn't find any relevant information in the documentation for your question.", []
        
    answer = f"Here's what I found in the documentation for '{query}':\n\n"
    
    for i, ctx in enumerate(context, 1):
        answer += f"Source: {ctx['source']}, Page {ctx['page']}\n"
        
        # Add heading if available
        if ctx.get('heading'):
            answer += f"Section: {ctx['heading']}\n"
            
        # Add a short excerpt (first 300 chars)
        excerpt = ctx['content']
        if len(excerpt) > 300:
            excerpt = excerpt[:300] + "..."
            
        answer += f"Excerpt {i}: {excerpt}\n\n"
    
    return answer, context

if __name__ == "__main__":
    # Test the QA system
    test_query = "How do I reset the device?"
    
    print("Testing Local LLM for answering...")
    answer, context = answer_with_local_llm(test_query)
    
    print(f"Query: {test_query}")
    print(f"Answer: {answer}")
    print(f"Using {len(context)} context chunks")