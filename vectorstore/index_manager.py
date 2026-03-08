"""
Index Manager Module
Handles document indexing, chunking, and management for the vector database.
"""

import uuid
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Use simple text splitter to avoid PyTorch dependency
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.text_splitter import SimpleTextSplitter

# Import from src package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from vectorstore.chroma_client import get_chroma_client
from src.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.logger import get_logger

log = get_logger(__name__)


class IndexManager:
    """
    Manages document indexing and chunking for the vector database.
    
    Features:
    - Document chunking with overlap
    - Metadata enrichment
    - Batch indexing
    - Source tracking
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        """
        Initialize index manager.
        
        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or CHUNK_OVERLAP
        self.chroma_client = get_chroma_client()
        
        # Initialize text splitter (simple version without PyTorch)
        self.text_splitter = SimpleTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        log.info(
            "Index manager initialized",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text to chunk
            metadata: Base metadata to attach to all chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            # Split text
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk objects with metadata
            chunk_objects = []
            for idx, chunk_text in enumerate(chunks):
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk_text),
                    "indexed_at": datetime.utcnow().isoformat()
                })
                
                chunk_objects.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata,
                    "id": str(uuid.uuid4())
                })
            
            log.info("Text chunked", chunk_count=len(chunks), text_length=len(text))
            return chunk_objects
            
        except Exception as e:
            log.error("Failed to chunk text", text_length=len(text), error=str(e))
            raise
    
    def index_document(
        self,
        text: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Index a single document into the vector database.
        
        Args:
            text: Document text
            source: Source identifier (filename, URL, etc.)
            metadata: Additional metadata
            
        Returns:
            Number of chunks indexed
        """
        try:
            # Prepare base metadata
            base_metadata = {
                "source": source,
                "source_type": self._detect_source_type(source),
                "document_length": len(text)
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            # Chunk the document
            chunks = self.chunk_text(text, base_metadata)
            
            # Extract data for ChromaDB
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["id"] for chunk in chunks]
            
            # Add to vector database
            count = self.chroma_client.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            log.info(
                "Document indexed",
                source=source,
                chunks=count,
                document_length=len(text)
            )
            
            return count
            
        except Exception as e:
            log.error("Failed to index document", source=source, error=str(e))
            raise
    
    def index_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Index multiple documents in batch.
        
        Args:
            documents: List of dicts with 'text', 'source', and optional 'metadata'
            
        Returns:
            Total number of chunks indexed
        """
        total_chunks = 0
        
        for doc in documents:
            try:
                count = self.index_document(
                    text=doc["text"],
                    source=doc["source"],
                    metadata=doc.get("metadata")
                )
                total_chunks += count
            except Exception as e:
                log.error("Failed to index document in batch", source=doc.get("source"), error=str(e))
                # Continue with other documents
        
        log.info("Batch indexing complete", total_chunks=total_chunks, documents=len(documents))
        return total_chunks
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the vector database.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of search results with text, metadata, and score
        """
        try:
            results = self.chroma_client.query(
                query_text=query,
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i],
                        "relevance_score": 1 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            log.info("Search completed", query_length=len(query), results_found=len(formatted_results))
            return formatted_results
            
        except Exception as e:
            log.error("Search failed", query=query[:100], error=str(e))
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get indexing statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.chroma_client.get_collection_stats()
            stats.update({
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            })
            return stats
        except Exception as e:
            log.error("Failed to get stats", error=str(e))
            raise
    
    def _detect_source_type(self, source: str) -> str:
        """
        Detect source type from source string.
        
        Args:
            source: Source identifier
            
        Returns:
            Source type string
        """
        if source.startswith("http://") or source.startswith("https://"):
            return "web"
        
        ext = Path(source).suffix.lower()
        if ext == ".pdf":
            return "pdf"
        elif ext in [".md", ".markdown"]:
            return "markdown"
        elif ext == ".txt":
            return "text"
        else:
            return "unknown"


# Singleton instance
_index_manager_instance = None


def get_index_manager(
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> IndexManager:
    """
    Get or create singleton IndexManager instance.
    
    Args:
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        
    Returns:
        IndexManager instance
    """
    global _index_manager_instance
    
    if _index_manager_instance is None:
        _index_manager_instance = IndexManager(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    return _index_manager_instance
