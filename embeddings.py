# embeddings.py
"""
Generate embeddings and setup vector database for SMC Documentation Q&A system
"""
import os
import pickle
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
from config import PROCESSED_DIR, CHROMA_DB_DIR, EMBEDDING_MODEL

def generate_embeddings(documents):
    """Generate embeddings for text chunks using a local model."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError("sentence-transformers is required. Install with: pip install sentence-transformers")
    
    # Using the model specified in config
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    print(f"Generating embeddings for {len(documents)} chunks using {EMBEDDING_MODEL}...")
    
    embeddings = []
    for doc in documents:
        embedding = model.encode(doc["content"])
        embeddings.append(embedding)
    
    # Save embeddings
    with open(os.path.join(PROCESSED_DIR, "embeddings.pkl"), "wb") as f:
        pickle.dump(embeddings, f)
    
    print(f"Generated and saved {len(embeddings)} embeddings")
    return embeddings


def setup_vector_db(documents, embeddings):
    """Set up a ChromaDB collection with documents and embeddings."""
    # Initialize ChromaDB (persistent client)
    client = chromadb.PersistentClient(CHROMA_DB_DIR)
    
    # Create embedding function (this is just a placeholder as we're using our own embeddings)
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
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


def process_embeddings_and_db():
    """Load documents, generate embeddings, and setup vector database."""
    # Check if chunked documents exist
    chunked_docs_path = os.path.join(PROCESSED_DIR, "chunked_docs.pkl")
    if not os.path.exists(chunked_docs_path):
        raise FileNotFoundError(
            "Chunked documents not found. Run document_processor.py first."
        )
    
    # Load chunked documents
    with open(chunked_docs_path, "rb") as f:
        chunked_docs = pickle.load(f)
    
    # Check if embeddings already exist
    embeddings_path = os.path.join(PROCESSED_DIR, "embeddings.pkl")
    if os.path.exists(embeddings_path):
        print(f"Loading existing embeddings from {embeddings_path}")
        with open(embeddings_path, "rb") as f:
            embeddings = pickle.load(f)
    else:
        # Generate new embeddings
        embeddings = generate_embeddings(chunked_docs)
    
    # Setup ChromaDB
    print(f"Setting up ChromaDB with {len(chunked_docs)} documents...")
    collection = setup_vector_db(chunked_docs, embeddings)
    
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
    
    return collection