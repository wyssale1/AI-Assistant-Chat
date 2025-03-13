# process_docs.py
"""
Main script for SMC Documentation Q&A System processing pipeline.
Executes the complete pipeline from PDF processing to vector database setup.
"""
import os
import sys
import argparse
import time
from config import DOCS_DIR, PROCESSED_DIR, QA_METHOD

def check_dependencies():
    """Check if all required dependencies are installed."""
    dependencies = [
        "flask", "python-dotenv", "chromadb", "sentence_transformers", 
        "pypdf", "langchain", "fitz", "pytesseract", "PIL", 
        "pdf2image", "tabula", "pandas"
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
    
    # Step 1: Process documents (extract text, tables, and chunk)
    if not skip_processing:
        print("\nSTEP 1: DOCUMENT PROCESSING")
        print("-" * 60)
        
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
        
        from embeddings import process_embeddings_and_db
        try:
            collection = process_embeddings_and_db()
        except Exception as e:
            print(f"Error in embeddings processing: {str(e)}")
            return False
    else:
        print("\nSKIPPING EMBEDDINGS & VECTOR DB (--skip-embeddings flag used)")
        
        # Check if vector database exists
        if not os.path.exists("./chroma_db"):
            print("ERROR: Cannot skip embeddings - no vector database found.")
            print(f"Run without --skip-embeddings flag first.")
            return False
    
    elapsed_time = time.time() - start_time
    print("\nPROCESSING PIPELINE COMPLETE")
    print("-" * 60)
    print(f"Total processing time: {elapsed_time:.2f} seconds")
    print(f"QA Method: {QA_METHOD}")
    print("\nTo start the web application, run:")
    print("    python app.py")
    
    return True


def verify_setup():
    """Verify the system setup and install missing dependencies."""
    import platform
    import subprocess
    
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
                    f.write("""flask==2.3.3
python-dotenv==1.0.0
chromadb==0.4.18
sentence-transformers==2.2.2
pypdf==3.17.1
langchain==0.0.267
requests==2.31.0
pymupdf==1.22.5
pytesseract==0.3.10
pillow==10.0.0
pdf2image==1.16.3
tabula-py==2.7.0
pandas==2.0.3""")
            
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
    
    print("\nSetup verification complete.")
    return True


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
    
    args = parser.parse_args()
    
    if args.verify:
        verify_setup()
    else:
        if verify_setup():
            run_pipeline(
                skip_processing=args.skip_processing,
                skip_embeddings=args.skip_embeddings,
                force=args.force
            )