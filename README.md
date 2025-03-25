# SMC Documentation Q&A System

A powerful documentation assistant that helps technical support staff quickly find information in SMC product documentation using advanced AI models.

## Architecture Overview

This system leverages two AI models to create an intelligent PDF documentation system:

1. **LLaVA**: Used for document pre-processing, particularly for analyzing images and diagrams in technical documents
2. **Phi-4**: Used for the chat interface to answer user questions based on the processed documentation

The system creates a modern, web-based question-answering interface that:

1. Pre-processes PDF documentation using LLaVA for enhanced image understanding
2. Converts documents into searchable vector embeddings
3. Retrieves relevant document chunks when queried
4. Uses the Phi-4 model to generate accurate, contextual answers
5. Provides source references so staff can verify information

## Features

- **Advanced PDF Processing**: Extracts text with layout preservation and uses LLaVA for image analysis
- **Vector-Based Retrieval**: Uses ChromaDB and sentence transformers for semantic search
- **Local Model Integration**: Uses Ollama to run both LLaVA and Phi-4 locally
- **Source Traceability**: All answers include references to source documents and page numbers
- **Smart Caching**: Frequently asked questions are cached for faster response times
- **User Feedback System**: Collects feedback to improve system performance
- **Modern React UI**: Clean, responsive interface that works on desktop and mobile devices

## Requirements

- Python 3.8+
- Node.js 18+ and npm
- Ollama (for running LLaVA and Phi-4)
- Tesseract OCR (optional, for better text extraction)

## Quick Start

### 1. Install Dependencies and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/smc-documentation-qa.git
cd smc-documentation-qa

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Make start script executable
chmod +x start-app.sh
```

### 2. Process Documentation

```bash
# Place your PDF documentation in the 'backend/docs' directory

# Run the processing pipeline
cd backend
python process_docs.py
cd ..
```

### 3. Start the Web Application

```bash
# Start both frontend and backend with a single command
./start-app.sh
```

Access the application at http://127.0.0.1:5000

## Repository Structure

```
smc-documentation-qa/
├── backend/
│   ├── app.py                  # Web application (Flask)
│   ├── config.py               # Configuration settings
│   ├── document_processor.py   # LLaVA-enhanced document processor
│   ├── embeddings.py           # Vector embeddings generator
│   ├── process_docs.py         # Main processing pipeline
│   ├── qa_system.py            # Phi-4 question answering system
│   ├── setup.py                # Setup script for dependencies
│   ├── requirements.txt        # Python dependencies
│   ├── docs/                   # Place PDF documents here
│   ├── processed_docs/         # Processed document data
│   ├── chroma_db/              # Vector database
│   ├── response_cache/         # Cached responses
│   ├── feedback/               # User feedback storage
│   ├── logs/                   # Log files
│   ├── static/                 # Static web assets
│   └── templates/              # HTML templates
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── types/              # TypeScript type definitions
│   │   ├── App.tsx             # Main application component
│   │   └── ...                 # Other React files
│   ├── public/                 # Public assets
│   ├── package.json            # Node.js dependencies
│   └── ...                     # Other configuration files
└── start-app.sh                # Script to build and run the application
```

## Configuration

The system can be configured through the `backend/.env` file (automatically created on first run):

### LLaVA and Phi-4 Settings

```
# LLaVA for Document Pre-processing
LLAVA_MODEL=llava
LLAVA_TEMPERATURE=0.2

# Phi-4 for Chat
OLLAMA_MODEL=phi4
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000
```

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

## Development

### Backend Development

```bash
cd backend
python app.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

## Advanced Usage

### Using Alternative Models

While the default configuration uses LLaVA for document processing and Phi-4 for chat, you can use any models supported by Ollama:

```bash
# Pull alternative models
ollama pull llama3
ollama pull bakllava

# Update your .env file
echo "OLLAMA_MODEL=llama3" >> backend/.env
echo "LLAVA_MODEL=bakllava" >> backend/.env

# Restart the application
./start-app.sh
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
- **Slow Responses**: Try using smaller models or reducing `SEARCH_TOP_K`
- **Out of Memory**: Reduce `LLM_CONTEXT_WINDOW` or `CHUNK_SIZE` values
- **Frontend Build Errors**: Make sure you have Node.js 18+ installed

## License

This project is provided as-is for SMC internal use.