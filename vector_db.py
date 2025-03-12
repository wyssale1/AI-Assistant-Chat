# vector_db.py
import chromadb
from chromadb.utils import embedding_functions
import pickle
import os

def setup_chroma_db(documents, embeddings):
    """Set up a ChromaDB collection with documents and embeddings."""
    # Initialize ChromaDB (persistent client)
    client = chromadb.PersistentClient("./chroma_db")
    
    # Create embedding function (this is just a placeholder as we're using our own embeddings)
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="smc_documentation",
        embedding_function=embedding_function
    )
    
    # Prepare data for insertion
    ids = [f"doc_{i}" for i in range(len(documents))]
    contents = [doc["content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    # Add documents to collection (using our precomputed embeddings)
    collection.add(
        ids=ids,
        documents=contents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    print(f"Added {len(documents)} documents to ChromaDB")
    return collection

if __name__ == "__main__":
    # Load chunked documents and embeddings
    if (os.path.exists("processed_docs/chunked_docs.pkl") and 
        os.path.exists("processed_docs/embeddings.pkl")):
        
        with open("processed_docs/chunked_docs.pkl", "rb") as f:
            chunked_docs = pickle.load(f)
        
        with open("processed_docs/embeddings.pkl", "rb") as f:
            embeddings = pickle.load(f)
        
        print(f"Setting up ChromaDB with {len(chunked_docs)} documents...")
        collection = setup_chroma_db(chunked_docs, embeddings)
        
        # Test query
        results = collection.query(
            query_texts=["How to troubleshoot power issues"],
            n_results=2
        )
        
        print("\nTest query results:")
        for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            print(f"Result {i+1}:")
            print(f"Source: {metadata['source']}, Page: {metadata['page']}")
            print(f"Content: {doc[:150]}...\n")
    else:
        print("Missing processed documents or embeddings. Run previous scripts first.")