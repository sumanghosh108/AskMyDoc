"""
Test script for ChromaDB vector store functionality.
Demonstrates: initialization, indexing, querying, and stats.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from vectorstore import get_chroma_client, get_index_manager
from src.utils.logger import get_logger

log = get_logger(__name__)


def test_chroma_client():
    """Test ChromaDB client initialization and basic operations."""
    print("\n" + "="*60)
    print("Testing ChromaDB Client")
    print("="*60)
    
    # Initialize client
    client = get_chroma_client()
    print(f"✓ ChromaDB client initialized")
    print(f"  Persist directory: {client.persist_dir}")
    print(f"  Collection: {client.collection_name}")
    print(f"  Embedding model: {client.embedding_model_name}")
    
    # Get initial stats
    stats = client.get_collection_stats()
    print(f"\n✓ Collection stats:")
    print(f"  Document count: {stats['document_count']}")
    print(f"  Has documents: {stats['has_documents']}")
    
    # Add sample documents
    print(f"\n✓ Adding sample documents...")
    documents = [
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing helps computers understand human language.",
        "Computer vision enables machines to interpret visual information.",
        "Reinforcement learning trains agents through rewards and penalties."
    ]
    
    metadatas = [
        {"topic": "ML", "category": "definition"},
        {"topic": "DL", "category": "definition"},
        {"topic": "NLP", "category": "definition"},
        {"topic": "CV", "category": "definition"},
        {"topic": "RL", "category": "definition"}
    ]
    
    count = client.add_documents(documents, metadatas)
    print(f"  Added {count} documents")
    
    # Query the database
    print(f"\n✓ Querying the database...")
    query = "What is deep learning?"
    results = client.query(query, n_results=3)
    
    print(f"  Query: '{query}'")
    print(f"  Results found: {len(results['ids'][0])}")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"\n  Result {i+1}:")
        print(f"    Text: {doc}")
        print(f"    Metadata: {metadata}")
        print(f"    Distance: {distance:.4f}")
        print(f"    Similarity: {1 - distance:.4f}")
    
    # Final stats
    final_stats = client.get_collection_stats()
    print(f"\n✓ Final collection stats:")
    print(f"  Document count: {final_stats['document_count']}")


def test_index_manager():
    """Test IndexManager for document chunking and indexing."""
    print("\n" + "="*60)
    print("Testing Index Manager")
    print("="*60)
    
    # Initialize manager
    manager = get_index_manager()
    print(f"✓ Index manager initialized")
    print(f"  Chunk size: {manager.chunk_size}")
    print(f"  Chunk overlap: {manager.chunk_overlap}")
    
    # Index a document
    print(f"\n✓ Indexing a document...")
    document_text = """
    Artificial Intelligence (AI) is transforming the world. Machine learning, 
    a subset of AI, enables computers to learn from data without explicit programming.
    Deep learning, using neural networks, has achieved remarkable results in image 
    recognition, natural language processing, and game playing. The future of AI 
    holds immense potential for solving complex problems across various domains.
    """
    
    count = manager.index_document(
        text=document_text,
        source="test_document.txt",
        metadata={"author": "Test", "date": "2024-03-08"}
    )
    print(f"  Indexed {count} chunks")
    
    # Search the index
    print(f"\n✓ Searching the index...")
    query = "What is machine learning?"
    results = manager.search(query, n_results=2)
    
    print(f"  Query: '{query}'")
    print(f"  Results found: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"\n  Result {i+1}:")
        print(f"    Text: {result['text'][:100]}...")
        print(f"    Source: {result['metadata'].get('source')}")
        print(f"    Chunk index: {result['metadata'].get('chunk_index')}")
        print(f"    Relevance score: {result['relevance_score']:.4f}")
    
    # Get stats
    stats = manager.get_stats()
    print(f"\n✓ Index statistics:")
    print(f"  Total documents: {stats['document_count']}")
    print(f"  Chunk size: {stats['chunk_size']}")
    print(f"  Chunk overlap: {stats['chunk_overlap']}")


def test_batch_indexing():
    """Test batch document indexing."""
    print("\n" + "="*60)
    print("Testing Batch Indexing")
    print("="*60)
    
    manager = get_index_manager()
    
    # Prepare batch documents
    documents = [
        {
            "text": "Python is a high-level programming language known for its simplicity.",
            "source": "python_intro.txt",
            "metadata": {"language": "Python", "level": "beginner"}
        },
        {
            "text": "JavaScript is the language of the web, running in browsers and servers.",
            "source": "javascript_intro.txt",
            "metadata": {"language": "JavaScript", "level": "beginner"}
        },
        {
            "text": "Rust provides memory safety without garbage collection.",
            "source": "rust_intro.txt",
            "metadata": {"language": "Rust", "level": "advanced"}
        }
    ]
    
    print(f"✓ Indexing {len(documents)} documents in batch...")
    total_chunks = manager.index_documents_batch(documents)
    print(f"  Total chunks indexed: {total_chunks}")
    
    # Search with metadata filter
    print(f"\n✓ Searching with metadata filter...")
    results = manager.search(
        query="programming language",
        n_results=5,
        filter_metadata={"level": "beginner"}
    )
    
    print(f"  Query: 'programming language' (filter: level=beginner)")
    print(f"  Results found: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"\n  Result {i+1}:")
        print(f"    Text: {result['text']}")
        print(f"    Language: {result['metadata'].get('language')}")
        print(f"    Level: {result['metadata'].get('level')}")
        print(f"    Relevance: {result['relevance_score']:.4f}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ChromaDB Vector Store Test Suite")
    print("="*60)
    
    try:
        # Test 1: ChromaDB Client
        test_chroma_client()
        
        # Test 2: Index Manager
        test_index_manager()
        
        # Test 3: Batch Indexing
        test_batch_indexing()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
