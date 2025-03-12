# document_chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pickle
import os

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into smaller chunks for better retrieval."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunked_documents = []
    
    for doc in documents:
        chunks = text_splitter.split_text(doc["content"])
        for chunk in chunks:
            chunked_documents.append({
                "content": chunk,
                "metadata": doc["metadata"]
            })
    
    return chunked_documents

if __name__ == "__main__":
    # Load documents if they exist
    if os.path.exists("processed_docs/extracted_docs.pkl"):
        with open("processed_docs/extracted_docs.pkl", "rb") as f:
            documents = pickle.load(f)
        
        chunked_docs = chunk_documents(documents)
        
        # Save chunked documents
        os.makedirs("processed_docs", exist_ok=True)
        with open("processed_docs/chunked_docs.pkl", "wb") as f:
            pickle.dump(chunked_docs, f)
        
        print(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
    else:
        print("No extracted documents found. Run pdf_extractor.py first.")