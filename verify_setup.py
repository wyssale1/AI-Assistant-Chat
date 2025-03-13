# Create setup verification script
cat > verify_setup.py << EOF
import sys
import subprocess

# Print Python version
print(f"Python version: {sys.version}")

# Check dependencies
dependencies = [
    "flask", "dotenv", "chromadb", "sentence_transformers", 
    "pypdf", "langchain", "fitz", "pytesseract", "PIL", 
    "pdf2image", "tabula", "pandas"
]

print("\nChecking dependencies:")
for dep in dependencies:
    try:
        if dep == "PIL":
            import PIL
            print(f"✓ {dep}: {PIL.__version__}")
        elif dep == "dotenv":
            import dotenv
            print(f"✓ {dep}: {dotenv.__version__}")
        elif dep == "fitz":
            import fitz
            print(f"✓ PyMuPDF (fitz): {fitz.__version__}")
        else:
            module = __import__(dep)
            print(f"✓ {dep}: {module.__version__}")
    except (ImportError, AttributeError):
        print(f"✗ {dep}: Not found")

# Check external dependencies
print("\nChecking external tools:")
tools = ["tesseract", "pdfinfo", "java"]
for tool in tools:
    try:
        version = subprocess.check_output([tool, "--version"], stderr=subprocess.STDOUT).decode().strip()
        print(f"✓ {tool}: {version.split('\\n')[0]}")
    except:
        print(f"✗ {tool}: Not found or not in PATH")

print("\nSetup verification complete")