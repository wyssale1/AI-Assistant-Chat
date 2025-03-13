# table_extractor.py
import os
import pickle

# Import dependencies with fallback installation
try:
    import pandas as pd
except ImportError:
    print("Warning: pandas not found. Installing...")
    os.system("pip install pandas==2.0.3")
    import pandas as pd

try:
    import tabula
except ImportError:
    print("Warning: tabula-py not found. Installing...")
    os.system("pip install tabula-py==2.7.0")
    import tabula

try:
    from enhanced_pdf_extractor import process_directory
except ImportError:
    print("Error: enhanced_pdf_extractor.py must be created first")
    # Will fail if not found

def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF using tabula-py."""
    filename = os.path.basename(pdf_path)
    tables_data = []
    
    try:
        # Use tabula-py to find and extract tables
        print(f"Extracting tables from {filename}...")
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        if not tables:
            print(f"  No tables found in {filename}")
            return tables_data
        
        print(f"  Found {len(tables)} potential tables")
        
        # Process each table
        for i, table in enumerate(tables):
            if table.empty:
                continue
                
            # Convert the table to a string representation
            table_str = table.to_string()
            
            # Store table data with metadata
            tables_data.append({
                "content": f"TABLE CONTENT:\n{table_str}",
                "metadata": {
                    "source": filename,
                    "table_index": i,
                    "type": "table",
                    "columns": list(table.columns),
                    "rows": len(table)
                }
            })
            
            print(f"  Processed table {i+1}: {len(table)} rows, {len(table.columns)} columns")
            
    except Exception as e:
        print(f"  Error extracting tables from {filename}: {str(e)}")
    
    return tables_data

def process_tables_in_directory(directory_path):
    """Process all PDFs in a directory for tables."""
    all_tables = []
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return all_tables
    
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return all_tables
    
    print(f"Scanning {len(pdf_files)} PDF files for tables.")
    
    for filename in pdf_files:
        file_path = os.path.join(directory_path, filename)
        tables = extract_tables_from_pdf(file_path)
        all_tables.extend(tables)
    
    # Save the extracted tables
    if all_tables:
        os.makedirs("processed_docs", exist_ok=True)
        with open("processed_docs/extracted_tables.pkl", "wb") as f:
            pickle.dump(all_tables, f)
        
        print(f"Extracted and saved {len(all_tables)} tables")
    else:
        print("No tables were found in the documents")
    
    return all_tables

if __name__ == "__main__":
    docs_dir = "docs"
    
    # First extract regular content
    print("Step 1: Extracting document content...")
    process_directory(docs_dir)
    
    # Then extract tables
    print("\nStep 2: Extracting tables...")
    tables = process_tables_in_directory(docs_dir)
    
    # If tables were found, merge them with the existing documents
    if tables:
        print("\nStep 3: Merging tables with document content...")
        try:
            with open("processed_docs/extracted_docs.pkl", "rb") as f:
                documents = pickle.load(f)
            
            documents.extend(tables)
            
            with open("processed_docs/extracted_docs.pkl", "wb") as f:
                pickle.dump(documents, f)
            
            print(f"Successfully merged {len(tables)} tables with {len(documents) - len(tables)} document chunks")
        except Exception as e:
            print(f"Error merging tables with documents: {str(e)}")
    
    print("\nProcessing complete!")