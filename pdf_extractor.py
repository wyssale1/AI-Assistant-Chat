# pdf_extractor.py
import os
from pypdf import PdfReader
import re
from pypdf.errors import PdfReadError
import pickle

def extract_text_with_metadata(pdf_path):
    """Extract text from PDF along with page numbers and headings."""
    documents = []
    filename = os.path.basename(pdf_path)
    
    try:
        reader = PdfReader(pdf_path)
        
        for i, page in enumerate(reader.pages):
            try:
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
                else:
                    print(f"  Page {i+1} contains no extractable text, skipping...")
            except PdfReadError as e:
                print(f"  Error extracting text from page {i+1}: {str(e)}")
                # Add a placeholder with error information
                documents.append({
                    "content": f"[PDF TEXT EXTRACTION ERROR: {str(e)}]",
                    "metadata": {
                        "source": filename,
                        "page": i + 1,
                        "heading": "ERROR_PAGE"
                    }
                })
            except Exception as e:
                print(f"  Unexpected error on page {i+1}: {str(e)}")
    except Exception as e:
        print(f"  Failed to process PDF: {str(e)}")
        # Add a placeholder entry for the whole document
        documents.append({
            "content": f"[FAILED TO PROCESS PDF: {str(e)}]",
            "metadata": {
                "source": filename,
                "page": 0,
                "heading": "ERROR_DOCUMENT"
            }
        })
    
    return documents

def process_directory(directory_path):
    """Process all PDFs in a directory."""
    all_documents = []
    processed_files = 0
    failed_files = 0
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return all_documents
    
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return all_documents
    
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    for filename in pdf_files:
        file_path = os.path.join(directory_path, filename)
        print(f"Processing {filename}...")
        try:
            documents = extract_text_with_metadata(file_path)
            if documents:
                all_documents.extend(documents)
                print(f"  Successfully extracted {len(documents)} document chunks")
                processed_files += 1
            else:
                print(f"  No content extracted from {filename}")
                failed_files += 1
        except Exception as e:
            print(f"  Failed to process {filename}: {str(e)}")
            failed_files += 1
    
    print(f"Processing complete: {processed_files} files processed successfully, {failed_files} files failed")
    
    # Save the extracted documents
    os.makedirs("processed_docs", exist_ok=True)
    with open("processed_docs/extracted_docs.pkl", "wb") as f:
        pickle.dump(all_documents, f)
    
    return all_documents

if __name__ == "__main__":
    docs_dir = "docs"
    all_docs = process_directory(docs_dir)
    print(f"Extracted {len(all_docs)} document chunks")
    print(f"Saved to processed_docs/extracted_docs.pkl")