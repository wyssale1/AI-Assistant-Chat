# qa_system.py (updated with improved formatting and using config)
import os
import json
import time
import hashlib
import chromadb
import requests
import logging

# Import configuration
from config import (
    OLLAMA_URL, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    LLM_CONTEXT_WINDOW, SEARCH_TOP_K, CACHE_SIZE, LLM_USE_STREAMING,
    CHROMA_DB_DIR, COLLECTION_NAME, CACHE_DIR
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("qa_system.log"), logging.StreamHandler()]
)
logger = logging.getLogger("qa_system")

# Cache directory
os.makedirs(CACHE_DIR, exist_ok=True)

def get_relevant_context(query, n_results=SEARCH_TOP_K, rerank=True):
    """
    Retrieve and potentially rerank relevant document chunks based on the query.
    """
    try:
        client = chromadb.PersistentClient(CHROMA_DB_DIR)
        collection = client.get_collection(COLLECTION_NAME)
        
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
            # Sort by adjusted relevance and take top n_results
            context = sorted(context, key=lambda x: x["relevance"], reverse=True)[:n_results]
        
        return context
    
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return []

def format_context_for_llm(context, max_length=LLM_CONTEXT_WINDOW):
    """Format context data for the LLM prompt with smart truncation and improved source tracking."""
    formatted_chunks = []
    total_length = 0
    
    # First pass: format all chunks with metadata and clear boundaries
    for i, ctx in enumerate(context):
        # Format each chunk with clear section boundaries
        chunk = f"--- START EXCERPT FROM {ctx['source']}, PAGE {ctx['page']} ---\n"
        
        if ctx.get("heading"):
            chunk += f"SECTION: {ctx['heading']}\n"
        
        # Truncate very long content chunks
        content = ctx['content']
        if len(content) > 1500:
            content = content[:1450] + "... [content truncated]"
            
        chunk += f"{content}\n"
        chunk += f"--- END EXCERPT FROM {ctx['source']}, PAGE {ctx['page']} ---\n\n"
        
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
    """Generate a well-structured prompt for the LLM with improved citation instructions."""
    return f"""You are a precise, helpful assistant for SMC device documentation. 
Your task is to answer the user's question about SMC devices by carefully analyzing the provided context.

INSTRUCTION GUIDELINES:
1. Answer ONLY based on the information in the provided context excerpts
2. If the answer isn't in the context, say "I don't have enough information about that in the documentation."
3. VERY IMPORTANT: When citing sources, ONLY use the exact page numbers as provided in the context excerpts
4. Each excerpt is clearly marked with "START EXCERPT FROM [document], PAGE [number]"
5. When including information from an excerpt, cite it as ([document], Page [number])
6. The context may include both text and image descriptions
7. Be direct and concise in your answers
8. When providing steps or procedures, use numbered lists

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
        "stream": LLM_USE_STREAMING,
        "options": {
            "temperature": LLM_TEMPERATURE,
            "num_predict": LLM_MAX_TOKENS
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
            if LLM_USE_STREAMING:
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
    # Create a mapping of source document to pages
    source_pages = {}
    for ctx in context:
        source = ctx['source']
        page = ctx['page']
        if source not in source_pages:
            source_pages[source] = set()
        source_pages[source].add(page)
    
    # Add a clean source summary at the end if not already present
    if "**Sources:**" not in answer:
        sources_summary = "\n\n**Sources:**"
        for source, pages in source_pages.items():
            sources_summary += f"\n**{source}**"
            for page in sorted(pages):
                sources_summary += f"\n* Page {page}"
        
        answer += sources_summary
    
    return answer

if __name__ == "__main__":
    # Test the QA system
    test_query = "How do I reset the device?"
    
    print("Testing Local LLM for answering...")
    answer, context = answer_with_local_llm(test_query)
    
    print(f"Query: {test_query}")
    print(f"Answer: {answer}")
    print(f"Using {len(context)} context chunks")