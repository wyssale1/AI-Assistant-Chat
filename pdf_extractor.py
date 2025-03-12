# pdf_extractor.py
import os
from pypdf import PdfReader
import re

def extract_text_with_metadata(pdf_path):
    """Extract text from PDF along with page numbers and headings."""
    reader = PdfReader(pdf_path)
    filename = os.path.basename(pdf_path)
    documents = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            # Simple heading detection (could be improved)
            headings = re.findall(r'^.*(?:Troubleshooting|Installation|Setup|Configuration|Maintenance).*$', 
                                 text, re.MULTILINE)
            heading = headings[0] if headings else ""
            
            documents.append({
                "content": text,
                "metadata": {
                    "source": filename,
                    "page": i + 1,
                    "heading": heading
                }
            })
    
    return documents

def process_directory(directory_path):
    """Process all PDFs in a directory."""
    all_documents = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing {filename}...")
            documents = extract_text_with_metadata(file_path)
            all_documents.extend(documents)
    
    return all_documents

if __name__ == "__main__":
    docs_dir = "docs"
    all_docs = process_directory(docs_dir)
    print(f"Extracted {len(all_docs)} document chunks")