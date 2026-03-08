"""
ChromaDB Inspection Script
Manually inspect the contents of the ChromaDB vector database
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import ChromaDB
import chromadb
from chromadb.config import Settings

# Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "rag_documents")

def inspect_chromadb():
    """Inspect ChromaDB contents"""
    print("=" * 80)
    print("ChromaDB Inspection")
    print("=" * 80)
    print(f"Persist Directory: {CHROMA_PERSIST_DIR}")
    print(f"Collection Name: {CHROMA_COLLECTION_NAME}")
    print()
    
    try:
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # List all collections
        collections = client.list_collections()
        print(f"Total Collections: {len(collections)}")
        print()
        
        if not collections:
            print("No collections found in ChromaDB")
            return
        
        # Display collection details
        for coll in collections:
            print(f"Collection: {coll.name}")
            print(f"  ID: {coll.id}")
            print()
        
        # Get the main collection
        try:
            collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        except Exception as e:
            print(f"Error: Collection '{CHROMA_COLLECTION_NAME}' not found")
            print(f"Available collections: {[c.name for c in collections]}")
            return
        
        # Get collection stats
        count = collection.count()
        print(f"Documents in '{CHROMA_COLLECTION_NAME}': {count}")
        print()
        
        if count == 0:
            print("No documents in collection")
            return
        
        # Get all documents (limit to first 10 for display)
        limit = min(10, count)
        results = collection.get(
            limit=limit,
            include=["documents", "metadatas", "embeddings"]
        )
        
        print(f"Showing first {limit} documents:")
        print("-" * 80)
        
        for i, (doc_id, document, metadata) in enumerate(zip(
            results['ids'],
            results['documents'],
            results['metadatas']
        ), 1):
            print(f"\nDocument {i}:")
            print(f"  ID: {doc_id}")
            print(f"  Metadata: {metadata}")
            print(f"  Content Preview: {document[:200]}...")
            if len(document) > 200:
                print(f"  Full Length: {len(document)} characters")
        
        print()
        print("-" * 80)
        
        # Show metadata statistics
        print("\nMetadata Statistics:")
        sources = set()
        chunk_indices = []
        
        all_results = collection.get(include=["metadatas"])
        for metadata in all_results['metadatas']:
            if metadata:
                if 'source' in metadata:
                    sources.add(metadata['source'])
                if 'chunk_index' in metadata:
                    chunk_indices.append(metadata['chunk_index'])
        
        print(f"  Unique Sources: {len(sources)}")
        if sources:
            print(f"  Sources:")
            for source in sorted(sources):
                source_count = sum(1 for m in all_results['metadatas'] 
                                 if m and m.get('source') == source)
                print(f"    - {source}: {source_count} chunks")
        
        if chunk_indices:
            print(f"  Chunk Index Range: {min(chunk_indices)} - {max(chunk_indices)}")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"Error inspecting ChromaDB: {e}")
        import traceback
        traceback.print_exc()


def search_chromadb(query_text: str, n_results: int = 5):
    """Search ChromaDB with a query"""
    print("=" * 80)
    print(f"Searching ChromaDB for: '{query_text}'")
    print("=" * 80)
    
    try:
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        
        # Search
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"\nFound {len(results['ids'][0])} results:")
        print("-" * 80)
        
        for i, (doc_id, document, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"\nResult {i}:")
            print(f"  ID: {doc_id}")
            print(f"  Distance: {distance:.4f}")
            print(f"  Metadata: {metadata}")
            print(f"  Content: {document[:300]}...")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"Error searching ChromaDB: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Search mode
        query = " ".join(sys.argv[1:])
        search_chromadb(query)
    else:
        # Inspection mode
        inspect_chromadb()
        
        print("\nTo search the database, run:")
        print("  python inspect_chromadb.py <your search query>")
        print("\nExample:")
        print("  python inspect_chromadb.py what is machine learning")
