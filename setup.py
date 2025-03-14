# setup.py
"""
Setup script for SMC Documentation Q&A System.
Handles installation of dependencies and setup of Ollama models.
"""
import os
import subprocess
import sys
import requests
import platform

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
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"Successfully pulled {model}")
        except subprocess.CalledProcessError as e:
            print(f"Error pulling {model}: {e}")
            return False
    return True

def create_directories():
    """Create necessary directories."""
    dirs = ["docs", "processed_docs", "chroma_db", "static", "templates", "response_cache", "logs"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("Created necessary directories")
    return True

def install_dependencies():
    """Install required Python dependencies."""
    requirements = [
        "flask>=2.3.3",
        "python-dotenv>=1.0.0",
        "chromadb>=0.4.18",
        "sentence-transformers>=2.2.2",
        "pypdf>=3.17.1",
        "langchain>=0.0.267",
        "requests>=2.31.0",
        "pymupdf>=1.22.5",
        "pytesseract>=0.3.10",
        "pillow>=10.1.0",
        "pdf2image>=1.16.3",
        "tabula-py>=2.7.0",
        "pandas>=2.0.3",
        "tqdm>=4.66.1",
        "pydantic>=2.0.0"
    ]
    
    # Save requirements to file
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Successfully installed Python dependencies")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        tesseract_version = subprocess.check_output(["tesseract", "--version"], 
                                                   stderr=subprocess.STDOUT).decode().split('\n')[0]
        print(f"Tesseract OCR: {tesseract_version} (installed)")
        return True
    except:
        print("Tesseract OCR: Not found")
        print("For OCR functionality, please install Tesseract:")
        if platform.system() == "Darwin":  # macOS
            print("  brew install tesseract")
        elif platform.system() == "Linux":
            print("  sudo apt-get install tesseract-ocr")
        elif platform.system() == "Windows":
            print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def setup_system():
    """Set up the SMC Documentation Q&A System."""
    print("=" * 60)
    print("SMC DOCUMENTATION Q&A SYSTEM SETUP")
    print("=" * 60)
    
    success = True
    
    # Create directories
    print("\nStep 1: Creating directories...")
    success = create_directories() and success
    
    # Install dependencies
    print("\nStep 2: Installing Python dependencies...")
    success = install_dependencies() and success
    
    # Check Ollama
    print("\nStep 3: Checking Ollama installation...")
    if not check_ollama_installation():
        print("Ollama is not installed or not running.")
        print("Please install Ollama and start the service.")
        print("Visit https://ollama.com/download for installation instructions.")
        success = False
    else:
        print("Ollama is installed and running.")
        
        # Pull required models
        print("\nStep 4: Pulling required models...")
        success = pull_required_models() and success
    
    # Check Tesseract (optional)
    print("\nStep 5: Checking Tesseract OCR (optional)...")
    tesseract_installed = check_tesseract()
    if not tesseract_installed:
        print("Tesseract is not required but recommended for better OCR capabilities.")
    
    # Final status
    print("\n" + "=" * 60)
    if success:
        print("Setup completed successfully!")
    else:
        print("Setup completed with some issues. Please address them before proceeding.")
    
    # Usage instructions
    print("\nTo use the system:")
    print("1. Place your PDF documents in the 'docs' directory")
    print("2. Run 'python process_docs.py' to process documents")
    print("3. Start the web interface with 'python app.py'")
    print("=" * 60)

if __name__ == "__main__":
    setup_system()