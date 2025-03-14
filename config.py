# config.py
"""
Central configuration file for SMC Documentation Q&A System
"""
import os

# Paths
DOCS_DIR = "docs"
PROCESSED_DIR = "processed_docs"
CHROMA_DB_DIR = "./chroma_db"
STATIC_DIR = "static"
TEMPLATES_DIR = "templates"
CACHE_DIR = "response_cache"
LOG_DIR = "logs"

# Create directories if they don't exist
for dir_path in [DOCS_DIR, PROCESSED_DIR, STATIC_DIR, TEMPLATES_DIR, CACHE_DIR, LOG_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Document processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EXTRACT_IMAGES = True
IMAGE_MIN_SIZE = 100  # Minimum width/height to extract
OCR_ENABLED = True

# LLaVA settings for document pre-processing
LLAVA_MODEL = "llava"
LLAVA_URL = "http://localhost:11434/api/generate"
LLAVA_TEMPERATURE = 0.2
LLAVA_CONTEXT_SIZE = 1000  # Text context size around images

# Ollama LLM settings for chat
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi4"  # Default model for chat
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 1000
LLM_TOP_P = 0.9
LLM_FREQUENCY_PENALTY = 0.0
LLM_PRESENCE_PENALTY = 0.0
LLM_CONTEXT_WINDOW = 8000
LLM_USE_STREAMING = False

# Retrieval settings
SEARCH_TOP_K = 5  # Number of chunks to retrieve
RERANK_RESULTS = True
MINIMUM_RELEVANCE = 0.3  # Minimum relevance score to include
CACHE_SIZE = 100  # Maximum number of cached responses
CACHE_TTL = 86400  # Time to live for cache in seconds (default: 1 day)

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight model for embeddings

# Server settings
DEBUG_MODE = True
HOST = "127.0.0.1"
PORT = 5000
LOG_LEVEL = "INFO"

# Performance settings
REQUEST_TIMEOUT = 180  # Timeout for API requests in seconds

# Collection name for vector database
COLLECTION_NAME = "smc_documentation"