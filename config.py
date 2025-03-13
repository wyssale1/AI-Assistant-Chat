# config.py
"""
Central configuration file for SMC Documentation Q&A System
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
DOCS_DIR = "docs"
PROCESSED_DIR = "processed_docs"
CHROMA_DB_DIR = "./chroma_db"
STATIC_DIR = "static"
TEMPLATES_DIR = "templates"

# Create directories if they don't exist
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Document processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EXTRACT_IMAGES = True
IMAGE_MIN_SIZE = 100  # Minimum width/height to extract
OCR_ENABLED = True

# QA System settings
QA_METHOD = os.getenv("QA_METHOD", "simple").lower()  # Options: "simple", "local"
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "phi4"  # Default model for Ollama
LLM_TEMPERATURE = 0.3
SEARCH_TOP_K = 3  # Number of chunks to retrieve

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight model for embeddings

# Server settings
DEBUG_MODE = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))