# SMC Documentation Q&A System

A vector search-based documentation assistant that helps users query PDF technical documentation through a simple web interface.

## Overview

This system processes PDF documentation, converts it into searchable vector embeddings, and provides a web interface for querying information. It uses:

- **Flask** for the web server
- **ChromaDB** for vector storage
- **SentenceTransformers** for document embeddings
- **PyPDF** for PDF text extraction
- **Optional**: Local LLM support via Ollama

## Installation

### Prerequisites

- macOS 10.14+ (also works on Linux/Windows with minor adjustments)
- Python 3.8+
- Admin access to your computer

### Step 1: Install Python

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python

# Verify installation
python3 --version
```

### Step 2: Clone and Set Up the Project

```bash
# Clone repository (if using git)
git clone https://github.com/yourusername/smc-documentation-qa.git
cd smc-documentation-qa

# Or create directories manually
mkdir -p smc_qa_system/{templates,static,docs,processed_docs}
cd smc_qa_system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install flask==2.3.3 python-dotenv==1.0.0 chromadb==0.4.18 sentence-transformers==2.2.2 pypdf==3.17.1 langchain==0.0.267 requests==2.31.0
```

Or create `requirements.txt` with these dependencies and run:

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root:

```
QA_METHOD=simple
```

### Step 5: Add Documents

Place your PDF documentation files in the `docs` directory:

```bash
# Example
cp /path/to/your/pdfs/*.pdf docs/
```

### Step 6: Process Documents

Run these scripts in sequence:

```bash
# Extract text from PDFs
python pdf_extractor.py

# Split documents into chunks
python document_chunker.py

# Generate embeddings
python embeddings_generator.py

# Create vector database
python vector_db.py
```

### Step 7: Run the Application

```bash
python app.py
```

Visit http://127.0.0.1:5000 in your browser.

## Using the Application

1. Type your question about SMC devices in the input box
2. Click "Send" or press Enter
3. The system will search documentation and return relevant information
4. Source references (document name and page number) will be displayed with each answer

## Advanced: Using a Local LLM

For AI-generated answers rather than just document retrieval:

```bash
# Install Ollama
brew install ollama

# Start Ollama service
ollama serve

# In a new terminal, pull a model
ollama pull phi4

# Update .env file
echo "QA_METHOD=local" > .env

# Restart the Flask app
python app.py
```

## Project Structure

```
smc_qa_system/
├── app.py                  # Flask web application
├── pdf_extractor.py        # Extracts text from PDFs
├── document_chunker.py     # Splits documents into chunks
├── embeddings_generator.py # Generates vector embeddings
├── vector_db.py            # Sets up ChromaDB
├── qa_system.py            # Question answering logic
├── .env                    # Environment configuration
├── docs/                   # PDF documentation files
├── processed_docs/         # Processed document data
├── templates/              # HTML templates
│   └── index.html
└── static/                 # Static CSS files
    └── style.css
```

## Troubleshooting

- **Missing Dependencies**: Run `pip install -r requirements.txt`
- **PDF Extraction Issues**: Ensure PDFs are not password-protected
- **Ollama Connection Error**: Check if Ollama is running with `ps aux | grep ollama`
- **ChromaDB Errors**: Try removing the `chroma_db` directory: `rm -rf ./chroma_db` and rerun `python vector_db.py`

## License

[MIT](LICENSE)

## Acknowledgements

- Built with [Flask](https://flask.palletsprojects.com/)
- Vector search by [ChromaDB](https://github.com/chroma-core/chroma)
- Embeddings by [SentenceTransformers](https://www.sbert.net/)