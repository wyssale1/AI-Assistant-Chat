# SMC Documentation Q&A System (Simplified)

A vector search-based documentation assistant that helps users query PDF technical documentation through a simple web interface.

## Overview

This system processes PDF documentation, converts it into searchable vector embeddings, and provides a web interface for querying information. It uses:

- **Flask** for the web server
- **ChromaDB** for vector storage
- **SentenceTransformers** for document embeddings
- **PyMuPDF** for PDF text extraction with layout preservation
- **Tesseract OCR** for text extraction from images
- **Optional**: Local LLM support via Ollama

## Installation

### Prerequisites

- Python 3.8+
- Tesseract OCR (optional, for better text extraction)

### Quick Start

1. Clone the repository or download the files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your PDF documentation in the `docs` directory
4. Run the processing pipeline:
   ```bash
   python process_docs.py
   ```
5. Start the web application:
   ```bash
   python app.py
   ```
6. Visit http://127.0.0.1:5000 in your browser

## Using the Application

1. Type your question about SMC devices in the input box
2. Click "Send" or press Enter
3. The system will search documentation and return relevant information
4. Source references (document name and page number) will be displayed with each answer

## Advanced Configuration

You can modify settings in `config.py`, including:

- Document chunking parameters
- OCR settings
- QA method (simple retrieval vs. local LLM)
- Server configuration

## Using a Local LLM

For AI-generated answers rather than just document retrieval:

```bash
# Install Ollama
brew install ollama  # on macOS

# Start Ollama service
ollama serve

# In a new terminal, pull a model
ollama pull phi4

# Update the QA method in .env file
echo "QA_METHOD=local" > .env

# Restart the Flask app
python app.py
```

## Troubleshooting

- **Missing Dependencies**: Run `pip install -r requirements.txt`
- **PDF Extraction Issues**: Install Tesseract OCR for better text extraction
- **Ollama Connection Error**: Ensure Ollama is running with `ps aux | grep ollama`
- **ChromaDB Errors**: Remove the `chroma_db` directory and rerun the pipeline

## Project Structure

```
smc_qa_system/
├── app.py                  # Flask web application
├── config.py               # Central configuration 
├── document_processor.py   # Unified document processing
├── embeddings.py           # Embeddings and vector DB
├── process_docs.py         # Main processing pipeline
├── qa_system.py            # Question answering logic
├── requirements.txt        # Dependencies
├── docs/                   # PDF documentation files
├── processed_docs/         # Processed document data
├── templates/              # HTML templates
│   └── index.html
└── static/                 # Static CSS files
    └── style.css
```