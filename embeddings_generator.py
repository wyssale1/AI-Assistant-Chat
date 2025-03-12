# embeddings_generator.py
from sentence_transformers import SentenceTransformer
import pickle
import os
import numpy as np

def generate_embeddings(documents):
    """Generate embeddings for text chunks using a local model."""
    # Using a lightweight model for local processing
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    embeddings = []
    for doc in documents:
        embedding = model.encode(doc["content"])
        embeddings.append(embedding)
    
    return embeddings

if __name__ == "__main__":
    # Load chunked documents
    if os.path.exists("processed_docs/chunked_docs.pkl"):
        with open("processed_docs/chunked_docs.pkl", "rb") as f:
            chunked_docs = pickle.load(f)
        
        print(f"Generating embeddings for {len(chunked_docs)} chunks...")
        embeddings = generate_embeddings(chunked_docs)
        
        # Save embeddings
        os.makedirs("processed_docs", exist_ok=True)
        with open("processed_docs/embeddings.pkl", "wb") as f:
            pickle.dump(embeddings, f)
        
        print(f"Generated and saved {len(embeddings)} embeddings")
    else:
        print("No chunked documents found. Run document_chunker.py first.")