# config.py
"""
Central configuration file for SMC Documentation Q&A System
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
DOCS_DIR = os.getenv("DOCS_DIR", "docs")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "processed_docs")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
STATIC_DIR = os.getenv("STATIC_DIR", "static")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "templates")
CACHE_DIR = os.getenv("CACHE_DIR", "response_cache")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# Create directories if they don't exist
for dir_path in [DOCS_DIR, PROCESSED_DIR, STATIC_DIR, TEMPLATES_DIR, CACHE_DIR, LOG_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Document processing settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
EXTRACT_IMAGES = os.getenv("EXTRACT_IMAGES", "True").lower() in ("true", "1", "t")
IMAGE_MIN_SIZE = int(os.getenv("IMAGE_MIN_SIZE", "100"))  # Minimum width/height to extract
OCR_ENABLED = os.getenv("OCR_ENABLED", "True").lower() in ("true", "1", "t")

# LLaVA settings for document pre-processing
LLAVA_MODEL = os.getenv("LLAVA_MODEL", "llava")
LLAVA_URL = os.getenv("LLAVA_URL", "http://localhost:11434/api/generate")
LLAVA_TEMPERATURE = float(os.getenv("LLAVA_TEMPERATURE", "0.2"))
LLAVA_CONTEXT_SIZE = int(os.getenv("LLAVA_CONTEXT_SIZE", "1000"))  # Text context size around images

# Ollama LLM settings for chat
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4")  # Default model for chat
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
LLM_FREQUENCY_PENALTY = float(os.getenv("LLM_FREQUENCY_PENALTY", "0.0"))
LLM_PRESENCE_PENALTY = float(os.getenv("LLM_PRESENCE_PENALTY", "0.0"))
LLM_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", "8000"))
LLM_USE_STREAMING = os.getenv("LLM_USE_STREAMING", "False").lower() in ("true", "1", "t")

# Retrieval settings
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "5"))  # Number of chunks to retrieve
RERANK_RESULTS = os.getenv("RERANK_RESULTS", "True").lower() in ("true", "1", "t")
MINIMUM_RELEVANCE = float(os.getenv("MINIMUM_RELEVANCE", "0.3"))  # Minimum relevance score to include
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "100"))  # Maximum number of cached responses
CACHE_TTL = int(os.getenv("CACHE_TTL", "86400"))  # Time to live for cache in seconds (default: 1 day)

# Embedding settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # Lightweight model for embeddings

# Server settings
DEBUG_MODE = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Performance settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))  # Timeout for API requests in seconds

# Collection name for vector database
COLLECTION_NAME = "smc_documentation"

# Default .env file template
DEFAULT_ENV_TEMPLATE = """# SMC Documentation Q&A System Configuration
# ------------------------------------------

# LLaVA for Document Pre-processing
LLAVA_MODEL=llava
LLAVA_TEMPERATURE=0.2

# Phi-4 for Chat
OLLAMA_MODEL=phi4
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000

# Retrieval Settings
SEARCH_TOP_K=5
RERANK_RESULTS=true
CACHE_SIZE=100

# Server Settings
DEBUG=true
HOST=127.0.0.1
PORT=5000
LOG_LEVEL=INFO

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EXTRACT_IMAGES=true
OCR_ENABLED=true
"""

# Create a default .env file if it doesn't exist
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write(DEFAULT_ENV_TEMPLATE)
    print("Created default .env configuration file")