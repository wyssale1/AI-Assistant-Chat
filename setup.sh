#!/bin/bash
# setup.sh - Automated setup script for SMC Documentation Q&A System

echo "SMC Documentation Q&A System - Setup Script"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Found Python $PYTHON_VERSION"
    PYTHON="python3"
else
    echo "Python 3 not found. Please install Python 3.7 or later."
    echo "You can install it with: brew install python3"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt..."
    cat > requirements.txt << EOF
flask==2.3.3
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
pandas==2.0.3
EOF
    echo "requirements.txt created."
else
    echo "requirements.txt already exists."
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for Tesseract installation
echo "Checking for Tesseract OCR..."
if command -v tesseract &>/dev/null; then
    echo "Tesseract is installed: $(tesseract --version | head -n 1)"
else
    echo "Tesseract not found. Installing with Homebrew..."
    if command -v brew &>/dev/null; then
        brew install tesseract
    else
        echo "Homebrew not found. Please install Tesseract manually."
        echo "You can install Homebrew with:"
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        echo "Then run: brew install tesseract"
    fi
fi

# Create directory structure
echo "Creating directory structure..."
mkdir -p docs processed_docs templates static

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "QA_METHOD=simple" > .env
    echo ".env file created."
else
    echo ".env file already exists."
fi

echo ""
echo "Setup complete! Your environment is ready."
echo ""
echo "Next steps:"
echo "1. Place your PDF files in the 'docs' directory"
echo "2. Run the processing pipeline:"
echo "   python enhanced_pdf_extractor.py"
echo "   python document_chunker.py"
echo "   python embeddings_generator.py"
echo "   python vector_db.py"
echo "3. Start the application: python app.py"
echo ""
echo "Note: To reactivate the virtual environment in the future, run:"
echo "source venv/bin/activate"