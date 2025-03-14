# SMC Documentation Q&A System with Local LLM

A powerful documentation assistant that helps technical support staff quickly find information in SMC product documentation using vector search and a local LLM integration via Ollama.

## Overview

This system creates a web-based question-answering interface that:

1. Processes PDF documentation into searchable vector embeddings
2. Retrieves relevant document chunks when queried
3. Uses a local LLM (Phi-4 via Ollama) to generate accurate, contextual answers
4. Provides source references so staff can verify information
5. Offers a clean, user-friendly web interface

## Features

- **Advanced PDF Processing**: Extracts text with layout preservation, handles tables, and supports OCR for images
- **Vector-Based Retrieval**: Uses ChromaDB and sentence transformers for semantic search
- **Local LLM Integration**: Leverages Ollama to run Phi-4 locally for generating answers
- **Source Traceability**: All answers include references to source documents and page numbers
- **Smart Caching**: Frequently asked questions are cached for faster response times
- **User Feedback System**: Collects feedback to improve system performance
- **Responsive UI**: Clean, modern interface that works on desktop and mobile devices

## Requirements

- Python 3.8+
- Ollama (for running local LLM)
- Tesseract OCR (optional, for better text extraction)

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Install and Configure Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# On Windows, download from: https://ollama.com/download/windows

# Start the Ollama service
ollama serve

# Pull the Phi-4 model (in a new terminal)
ollama pull phi4
```

### 3. Process Documentation

```bash
# Place your PDF documentation in the 'docs' directory

# Run the processing pipeline
python process_docs.py
```

### 4. Start the Web Application

```bash
python app.py
```

Access the application at http://127.0.0.1:5000

## Configuration

The system can be configured through the `.env` file (automatically created on first run):

### LLM Settings

```
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=phi4
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000
```

You can change `OLLAMA_MODEL` to any model supported by Ollama, such as:
- `phi4` (default, best balance of quality and speed)
- `llama3`
- `mistral`
- `llama3:8b` (smaller model)
- `mixtral`

### Retrieval Settings

```
SEARCH_TOP_K=5
RERANK_RESULTS=true
CACHE_SIZE=100
```

### Server Settings

```
DEBUG=true
HOST=127.0.0.1
PORT=5000
LOG_LEVEL=INFO
```

## Architecture

The system consists of several components:

1. **Document Processor**: Extracts and processes text from PDFs
2. **Embeddings Engine**: Generates vector embeddings and manages the vector database
3. **QA System**: Handles retrieval and LLM integration
4. **Web Application**: Provides the user interface

## Advanced Usage

### Using Other Models

While Phi-4 is the default model, you can use any model supported by Ollama:

```bash
# Pull another model
ollama pull llama3

# Update your .env file
echo "OLLAMA_MODEL=llama3" >> .env

# Restart the application
```

### Processing Large Document Collections

For large document sets, you can adjust chunking settings in the `.env` file:

```
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

## Troubleshooting

- **PDF Extraction Issues**: Install Tesseract OCR for better text extraction
- **Ollama Connection Error**: Ensure Ollama is running with `ps aux | grep ollama`
- **Slow Responses**: Try using a smaller model like `phi4:mini` or reducing `SEARCH_TOP_K`
- **Out of Memory**: Reduce `LLM_CONTEXT_WINDOW` or `CHUNK_SIZE` values

## Logs and Debugging

Logs are stored in the `logs` directory. To increase log verbosity:

```
LOG_LEVEL=DEBUG
```

## Feedback and Improvements

The system collects user feedback through the UI. Feedback data is stored in the `feedback` directory for future improvements.

## License

This project is provided as-is for SMC internal use.