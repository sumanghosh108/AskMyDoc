"""
ChromaDB Client Module
Handles persistent ChromaDB initialization, collection management, and vector operations.
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer

# Import from src package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
)
from src.utils.logger import get_logger

log = get_logger(__name__)


class ChromaClient:
    """
    Persistent ChromaDB client for vector storage and retrieval.
    
    Features:
    - Persistent storage on disk
    - Automatic collection creation
    - Document embedding and storage
    - Similarity search with metadata filtering
    """
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None
    ):
        """
        Initialize ChromaDB client with persistent storage.
        
        Args:
            persist_directory: Directory to persist the database (default from config)
            collection_name: Name of the collection (default from config)
            embedding_model: Sentence transformer model name (default from config)
        """
        self.persist_dir = Path(persist_directory or CHROMA_PERSIST_DIR)
        self.collection_name = collection_name or CHROMA_COLLECTION_NAME
        self.embedding_model_name = embedding_model or EMBEDDING_MODEL
        
        # Ensure persist directory exists
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self._client = None
        self._collection = None
        self._embedding_model = None
        
        self._initialize_client()
        self._initialize_embedding_model()
        self._initialize_collection()
        
        log.info(
            "ChromaDB client initialized",
            persist_dir=str(self.persist_dir),
            collection=self.collection_name,
            embedding_model=self.embedding_model_name
        )
    
    def _initialize_client(self):
        """Initialize persistent ChromaDB client."""
        try:
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            log.info("ChromaDB persistent client created")
        except Exception as e:
            log.error("Failed to initialize ChromaDB client", error=str(e))
            raise
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer embedding model."""
        try:
            self._embedding_model = SentenceTransformer(self.embedding_model_name)
            log.info("Embedding model loaded", model=self.embedding_model_name)
        except Exception as e:
            log.error("Failed to load embedding model", model=self.embedding_model_name, error=str(e))
            raise
    
    def _initialize_collection(self):
        """Get or create ChromaDB collection."""
        try:
            # Try to get existing collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "RAG system document embeddings"}
            )
            
            count = self._collection.count()
            log.info(
                "Collection initialized",
                name=self.collection_name,
                document_count=count
            )
        except Exception as e:
            log.error("Failed to initialize collection", collection=self.collection_name, error=str(e))
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self._embedding_model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            log.error("Failed to generate embeddings", text_count=len(texts), error=str(e))
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> int:
        """
        Add documents to the collection with automatic embedding.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dicts for each document
            ids: Optional list of unique IDs for each document
            
        Returns:
            Number of documents added
        """
        if not documents:
            log.warning("No documents to add")
            return 0
        
        try:
            # Generate embeddings
            log.info("Generating embeddings", document_count=len(documents))
            embeddings = self.embed_texts(documents)
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            # Add to collection
            self._collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            log.info("Documents added to collection", count=len(documents))
            return len(documents)
            
        except Exception as e:
            log.error("Failed to add documents", document_count=len(documents), error=str(e))
            raise
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the collection for similar documents.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions
            
        Returns:
            Dictionary with 'documents', 'metadatas', 'distances', 'ids'
        """
        try:
            # Generate query embedding
            query_embedding = self.embed_texts([query_text])[0]
            
            # Query collection
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"]
            )
            
            log.info(
                "Query executed",
                query_length=len(query_text),
                n_results=n_results,
                results_found=len(results['ids'][0]) if results['ids'] else 0
            )
            
            return results
            
        except Exception as e:
            log.error("Query failed", query=query_text[:100], error=str(e))
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self._collection.count()
            
            # Get sample to check metadata
            sample = self._collection.peek(limit=1)
            
            stats = {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": str(self.persist_dir),
                "embedding_model": self.embedding_model_name,
                "has_documents": count > 0
            }
            
            if sample and sample.get('metadatas'):
                stats["sample_metadata_keys"] = list(sample['metadatas'][0].keys()) if sample['metadatas'][0] else []
            
            return stats
            
        except Exception as e:
            log.error("Failed to get collection stats", error=str(e))
            raise
    
    def delete_collection(self):
        """Delete the entire collection (use with caution)."""
        try:
            self._client.delete_collection(name=self.collection_name)
            log.warning("Collection deleted", collection=self.collection_name)
            
            # Reinitialize collection
            self._initialize_collection()
            
        except Exception as e:
            log.error("Failed to delete collection", collection=self.collection_name, error=str(e))
            raise
    
    def reset_database(self):
        """Reset the entire database (use with extreme caution)."""
        try:
            self._client.reset()
            log.warning("Database reset - all collections deleted")
            
            # Reinitialize collection
            self._initialize_collection()
            
        except Exception as e:
            log.error("Failed to reset database", error=str(e))
            raise


# Singleton instance
_chroma_client_instance = None


def get_chroma_client(
    persist_directory: Optional[str] = None,
    collection_name: Optional[str] = None,
    embedding_model: Optional[str] = None
) -> ChromaClient:
    """
    Get or create singleton ChromaDB client instance.
    
    Args:
        persist_directory: Directory to persist the database
        collection_name: Name of the collection
        embedding_model: Sentence transformer model name
        
    Returns:
        ChromaClient instance
    """
    global _chroma_client_instance
    
    if _chroma_client_instance is None:
        _chroma_client_instance = ChromaClient(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_model=embedding_model
        )
    
    return _chroma_client_instance
