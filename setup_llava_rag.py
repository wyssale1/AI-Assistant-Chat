# setup_llava_rag.py
import os
import subprocess
import sys
import requests
import time

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return True
        return False
    except:
        return False

def pull_required_models():
    """Pull the required models from Ollama."""
    models = ["llava", "phi4"]
    
    for model in models:
        print(f"Pulling {model} model...")
        subprocess.run(["ollama", "pull", model], check=True)

def create_directories():
    """Create necessary directories."""
    dirs = ["docs", "processed_docs", "chroma_db"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def install_dependencies():
    """Install required Python dependencies."""
    requirements = [
        "pymupdf>=1.22.5",
        "pillow>=10.1.0",
        "requests>=2.31.0",
        "tqdm>=4.66.1",
        "sentence-transformers>=2.2.2",
        "chromadb>=0.4.18"
    ]
    
    # Install dependencies
    for req in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def setup_system():
    """Set up the LLaVA-Phi4 RAG system."""
    print("Setting up LLaVA-Phi4 RAG system...")
    
    # Check Ollama
    if not check_ollama_installation():
        print("Ollama is not installed or not running.")
        print("Please install Ollama and start the service.")
        print("Visit https://ollama.com/download for installation instructions.")
        sys.exit(1)
    
    # Install dependencies
    print("Installing Python dependencies...")
    install_dependencies()
    
    # Pull required models
    pull_required_models()
    
    # Create directories
    create_directories()
    
    print("\nSetup complete!")
    print("\nTo use the system:")
    print("1. Place your PDF documents in the 'docs' directory")
    print("2. Run 'python document_processor_llava.py' to process documents")
    print("3. Run 'python embeddings.py' to create embeddings and vector database")
    print("4. Start the interface with 'python app.py'")

if __name__ == "__main__":
    setup_system()