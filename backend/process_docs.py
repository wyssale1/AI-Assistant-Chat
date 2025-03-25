# process_docs.py
"""
Main processing pipeline that uses LLaVA for document analysis 
and sets up the vector database for Phi-4 QA system.
"""
import os
import sys
import argparse
import time
import logging
import platform
import subprocess
import requests

from config import (
    DOCS_DIR, PROCESSED_DIR, OLLAMA_MODEL, LLAVA_MODEL, 
    CHROMA_DB_DIR, OCR_ENABLED
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("process_docs.log"), logging.StreamHandler()]
)
logger = logging.getLogger("process_docs")

def check_dependencies():
    """Check if all required dependencies are installed."""
    dependencies = [
        "flask", "python-dotenv", "chromadb", "sentence_transformers", 
        "pypdf", "langchain", "fitz", "pytesseract", "PIL", 
        "pdf2image", "tabula", "pandas", "requests", "tqdm"
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == "PIL":
                import PIL
            elif dep == "fitz":
                import fitz
            else:
                __import__(dep)
        except ImportError:
            missing.append(dep)
    
    return missing

def verify_setup():
    """Verify the system setup and install missing dependencies."""
    print("=" * 60)
    print("SYSTEM VERIFICATION")
    print("=" * 60)
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    if int(python_version.split('.')[0]) < 3 or int(python_version.split('.')[1]) < 8:
        print("WARNING: Python 3.8+ is recommended for this application.")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        install = input("Do you want to install them now? (y/n): ").lower() == 'y'
        
        if install:
            # Create requirements.txt if it doesn't exist
            if not os.path.exists("requirements.txt"):
                with open("requirements.txt", "w") as f:
                    f.write("""flask>=2.3.3
python-dotenv>=1.0.0
chromadb>=0.4.18
sentence-transformers>=2.2.2
pypdf>=3.17.1
langchain>=0.0.267
requests>=2.31.0
pymupdf>=1.22.5
pytesseract>=0.3.10
pillow>=10.1.0
pdf2image>=1.16.3
tabula-py>=2.7.0
pandas>=2.0.3
tqdm>=4.66.1
pydantic>=2.0.0""")
            
            print("Installing missing dependencies...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("Dependencies installed successfully.")
            except subprocess.CalledProcessError:
                print("Failed to install dependencies. Please install them manually.")
                return False
        else:
            print("Please install the missing dependencies before running the application.")
            return False
    else:
        print("\nAll required Python dependencies are installed.")
    
    # Check for Tesseract (for OCR)
    if OCR_ENABLED:
        try:
            tesseract_version = subprocess.check_output(["tesseract", "--version"], 
                                                      stderr=subprocess.STDOUT).decode().split('\n')[0]
            print(f"Tesseract OCR: {tesseract_version}")
        except:
            print("Tesseract OCR: Not found")
            print("For OCR functionality, please install Tesseract:")
            if platform.system() == "Darwin":  # macOS
                print("  brew install tesseract")
            elif platform.system() == "Linux":
                print("  sudo apt-get install tesseract-ocr")
            elif platform.system() == "Windows":
                print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            
            proceed_without_ocr = input("Do you want to proceed without OCR support? (y/n): ").lower() == 'y'
            if not proceed_without_ocr:
                return False
    
    # Check for Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json()
            print(f"Ollama: Installed and running")
            
            # Get available models
            available_models = [m['name'] for m in models.get('models', [])]
            print(f"Available models: {', '.join(available_models)}")
            
            # Check if the configured models are available
            required_models = [OLLAMA_MODEL, LLAVA_MODEL]
            missing_models = [m for m in required_models if m not in available_models]
            
            if missing_models:
                print(f"WARNING: The following required models are not installed: {', '.join(missing_models)}")
                for model in missing_models:
                    print(f"Please install with: ollama pull {model}")
                
                install_models = input("Do you want to install these models now? (y/n): ").lower() == 'y'
                if install_models:
                    for model in missing_models:
                        try:
                            print(f"Pulling {model}...")
                            subprocess.run(["ollama", "pull", model], check=True)
                        except Exception as e:
                            print(f"Failed to pull {model}: {str(e)}")
                            return False
                else:
                    print("Please install the required models before running the pipeline.")
                    return False
        else:
            print("Ollama: Service is not responding properly")
            return False
    except:
        print("Ollama: Not running or not installed")
        print("For LLM and LLaVA functionality, please install Ollama:")
        if platform.system() == "Darwin":  # macOS
            print("  curl -fsSL https://ollama.com/install.sh | sh")
        elif platform.system() == "Windows":
            print("  Download from: https://ollama.com/download/windows")
        else:
            print("  curl -fsSL https://ollama.com/install.sh | sh")
        print(f"And then pull the required models:")
        print(f"  ollama pull {OLLAMA_MODEL}")
        print(f"  ollama pull {LLAVA_MODEL}")
        return False
    
    print("\nSetup verification complete. System is ready for processing.")
    return True

def run_pipeline(skip_processing=False, skip_embeddings=False, force=False):
    """Run the complete processing pipeline."""
    start_time = time.time()
    
    print("=" * 60)
    print("SMC DOCUMENTATION Q&A SYSTEM - PROCESSING PIPELINE")
    print("=" * 60)
    
    # Step 0: Check for PDF files
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"Created '{DOCS_DIR}' directory. Please add PDF files before running again.")
        return False
    
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in '{DOCS_DIR}'. Please add PDF files before running again.")
        return False
    
    print(f"Found {len(pdf_files)} PDF files in '{DOCS_DIR}'.")
    
    # Step 1: Process documents with LLaVA
    if not skip_processing:
        print("\nSTEP 1: DOCUMENT PROCESSING WITH LLAVA")
        print("-" * 60)
        
        # Clear existing processed files if force flag is set
        if force and os.path.exists(os.path.join(PROCESSED_DIR, "chunked_docs.pkl")):
            os.remove(os.path.join(PROCESSED_DIR, "chunked_docs.pkl"))
            print("Forced removal of existing processed documents.")
        
        # Run document processor
        from document_processor import process_directory
        chunked_docs = process_directory(DOCS_DIR)
        
        if not chunked_docs:
            print("Document processing failed or no content was extracted.")
            return False
    else:
        print("\nSKIPPING DOCUMENT PROCESSING (--skip-processing flag used)")
        
        # Check if processed documents exist
        if not os.path.exists(os.path.join(PROCESSED_DIR, "chunked_docs.pkl")):
            print("ERROR: Cannot skip processing - no processed documents found.")
            print(f"Run without --skip-processing flag first.")
            return False
    
    # Step 2: Generate embeddings and setup vector database
    if not skip_embeddings:
        print("\nSTEP 2: EMBEDDINGS & VECTOR DATABASE")
        print("-" * 60)
        
        # Clear existing database if force flag is set
        if force and os.path.exists(CHROMA_DB_DIR):
            import shutil
            try:
                # Attempt to delete the directory
                shutil.rmtree(CHROMA_DB_DIR)
                print(f"Forced removal of existing vector database at {CHROMA_DB_DIR}")
            except Exception as e:
                print(f"Warning: Failed to remove existing vector database: {str(e)}")
        
        from embeddings import process_embeddings_and_db
        try:
            collection = process_embeddings_and_db()
        except Exception as e:
            print(f"Error in embeddings processing: {str(e)}")
            return False
    else:
        print("\nSKIPPING EMBEDDINGS & VECTOR DB (--skip-embeddings flag used)")
        
        # Check if vector database exists
        if not os.path.exists(CHROMA_DB_DIR):
            print("ERROR: Cannot skip embeddings - no vector database found.")
            print(f"Run without --skip-embeddings flag first.")
            return False
    
    elapsed_time = time.time() - start_time
    print("\nPROCESSING PIPELINE COMPLETE")
    print("-" * 60)
    print(f"Total processing time: {elapsed_time:.2f} seconds")
    print(f"Document analysis: LLaVA ({LLAVA_MODEL})")
    print(f"Chat interface: Phi-4 ({OLLAMA_MODEL})")
    print("\nTo start the web application, run:")
    print("    python app.py")
    
    return True

def run_test_query():
    """Run a test query to verify the system is working."""
    print("\nRunning a test query to verify system...")
    
    from qa_system import answer_with_local_llm
    
    try:
        query = "What are the main components of the system?"
        answer, context = answer_with_local_llm(query)
        
        print(f"\nTest Query: {query}")
        print(f"\nAnswer: {answer[:200]}...")
        print(f"\nFound {len(context)} relevant context chunks")
        print("\nSystem is working correctly!")
        return True
    except Exception as e:
        print(f"\nError running test query: {str(e)}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="SMC Documentation Q&A System Processing Pipeline")
    parser.add_argument("--skip-processing", action="store_true", 
                        help="Skip document processing (use existing processed files)")
    parser.add_argument("--skip-embeddings", action="store_true", 
                        help="Skip embeddings generation and vector DB setup")
    parser.add_argument("--verify", action="store_true", 
                        help="Verify system setup without running the pipeline")
    parser.add_argument("--force", action="store_true", 
                        help="Force overwrite of existing processed files")
    parser.add_argument("--test", action="store_true",
                        help="Run a test query after processing")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_setup()
    else:
        if verify_setup():
            success = run_pipeline(
                skip_processing=args.skip_processing,
                skip_embeddings=args.skip_embeddings,
                force=args.force
            )
            
            if success and args.test:
                run_test_query()