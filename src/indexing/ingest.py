"""
Document ingestion module.
Handles loading, chunking, and embedding documents into ChromaDB.
Supports: PDF, Markdown, and web pages.
"""

import os
import glob
from pathlib import Path
from typing import Optional, List

# Use simple text splitter to avoid PyTorch dependency
from src.utils.text_splitter import SimpleTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.core.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
)
from src.utils.logger import get_logger
from src.utils.exceptions import (
    DocumentLoadError,
    ChunkingError,
    EmbeddingError,
    VectorStoreError,
    IngestionError,
)
from src.utils.exceptions.handlers import exception_handler, ExceptionContext

log = get_logger(__name__)


def _get_loader(file_path: str):
    """
    Return the appropriate document loader based on file extension.
    
    Args:
        file_path: Path to the document file
    
    Returns:
        Document loader instance
    
    Raises:
        DocumentLoadError: If file type is not supported
    """
    try:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        elif ext in (".md", ".markdown"):
            return UnstructuredMarkdownLoader(file_path)
        elif ext == ".txt":
            return TextLoader(file_path, encoding='utf-8')
        else:
            raise DocumentLoadError(
                f"Unsupported file type: {ext}",
                details={"file_path": file_path, "extension": ext, "supported": [".pdf", ".md", ".markdown", ".txt"]}
            )
    except DocumentLoadError:
        raise
    except Exception as e:
        raise DocumentLoadError(
            f"Failed to create loader for file",
            details={"file_path": file_path},
            original_error=e
        )


def load_documents(source: str) -> List:
    """
    Load documents from a file path, directory, or URL.

    Args:
        source: A file path, directory path, or URL starting with http.

    Returns:
        List of LangChain Document objects.
    
    Raises:
        DocumentLoadError: If document loading fails
    """
    documents = []

    try:
        if source.startswith("http://") or source.startswith("https://"):
            log.info("Loading web page", source=source)
            try:
                loader = WebBaseLoader(source)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = source
                    doc.metadata["source_type"] = "web"
                documents.extend(docs)
            except Exception as e:
                raise DocumentLoadError(
                    f"Failed to load web page",
                    details={"source": source, "type": "web"},
                    original_error=e
                )

        elif os.path.isfile(source):
            log.info("Loading file", source=source)
            try:
                loader = _get_loader(source)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = source
                    doc.metadata["source_type"] = Path(source).suffix.lower()
                documents.extend(docs)
            except DocumentLoadError:
                raise
            except Exception as e:
                raise DocumentLoadError(
                    f"Failed to load file",
                    details={"source": source, "type": "file"},
                    original_error=e
                )

        elif os.path.isdir(source):
            patterns = ["**/*.pdf", "**/*.md", "**/*.markdown", "**/*.txt"]
            files_found = []
            for pattern in patterns:
                files_found.extend(glob.glob(os.path.join(source, pattern), recursive=True))

            if not files_found:
                log.warning("No supported files found", source=source)
                return documents

            for file_path in sorted(files_found):
                log.info("Loading file", source=file_path)
                try:
                    loader = _get_loader(file_path)
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["source"] = file_path
                        doc.metadata["source_type"] = Path(file_path).suffix.lower()
                    documents.extend(docs)
                except Exception as e:
                    log.error("Error loading file", source=file_path, error=str(e))
                    # Continue with other files instead of failing completely

        else:
            raise DocumentLoadError(
                f"Source not found or invalid",
                details={"source": source, "exists": os.path.exists(source)}
            )

        log.info("Loaded documents", count=len(documents))
        return documents
    
    except DocumentLoadError:
        raise
    except Exception as e:
        raise DocumentLoadError(
            f"Unexpected error during document loading",
            details={"source": source},
            original_error=e
        )


def chunk_documents(documents, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
    """
    Split documents into chunks with overlap.

    Args:
        documents: List of LangChain Document objects.
        chunk_size: Target chunk size in tokens (default from config).
        chunk_overlap: Overlap in tokens (default from config).

    Returns:
        List of chunked Document objects with metadata.
    
    Raises:
        ChunkingError: If chunking fails
    """
    try:
        size = chunk_size or CHUNK_SIZE
        overlap = chunk_overlap or CHUNK_OVERLAP

        if size <= 0 or overlap < 0 or overlap >= size:
            raise ChunkingError(
                "Invalid chunk parameters",
                details={"chunk_size": size, "chunk_overlap": overlap}
            )

        splitter = SimpleTextSplitter(
            chunk_size=size,
            chunk_overlap=overlap
        )

        # Convert documents to text and split
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        chunk_dicts = splitter.create_documents(texts, metadatas)
        
        # Convert dictionaries to LangChain Document objects
        chunks = [Document(page_content=d['page_content'], metadata=d['metadata']) 
                  for d in chunk_dicts]

        # Enrich metadata with chunk index per source
        source_counters = {}
        for chunk in chunks:
            src = chunk.metadata.get("source", "unknown")
            idx = source_counters.get(src, 0)
            chunk.metadata["chunk_index"] = idx
            source_counters[src] = idx + 1

        log.info("Created chunks", count=len(chunks), chunk_size=size, chunk_overlap=overlap)
        return chunks
    
    except ChunkingError:
        raise
    except Exception as e:
        log.error("Chunking exception details", error=str(e), error_type=type(e).__name__)
        raise ChunkingError(
            "Failed to chunk documents",
            details={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap, "doc_count": len(documents)},
            original_error=e
        )


def get_vector_store(persist_directory: Optional[str] = None, collection_name: Optional[str] = None):
    """
    Get or create a ChromaDB vector store.

    Args:
        persist_directory: Directory to persist the vector store
        collection_name: Name of the collection

    Returns:
        Chroma vector store instance.
    
    Raises:
        VectorStoreError: If vector store creation fails
        EmbeddingError: If embedding model loading fails
    """
    try:
        persist_dir = persist_directory or CHROMA_PERSIST_DIR
        col_name = collection_name or CHROMA_COLLECTION_NAME

        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
            )
        except Exception as e:
            raise EmbeddingError(
                "Failed to load embedding model",
                details={"model": EMBEDDING_MODEL},
                original_error=e
            )

        try:
            vector_store = Chroma(
                collection_name=col_name,
                embedding_function=embeddings,
                persist_directory=persist_dir,
            )
        except Exception as e:
            raise VectorStoreError(
                "Failed to create vector store",
                details={"persist_dir": persist_dir, "collection": col_name},
                original_error=e
            )

        return vector_store
    
    except (VectorStoreError, EmbeddingError):
        raise
    except Exception as e:
        raise VectorStoreError(
            "Unexpected error creating vector store",
            details={"persist_dir": persist_directory, "collection": collection_name},
            original_error=e
        )


def ingest_documents(source: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> int:
    """
    Full ingestion pipeline: load → chunk → embed → store.

    Args:
        source: File, directory, or URL to ingest.
        chunk_size: Optional override for chunk size.
        chunk_overlap: Optional override for chunk overlap.

    Returns:
        Number of chunks stored.
    
    Raises:
        IngestionError: If any step of ingestion fails
    """
    log.info("Ingesting documents", source=source)

    try:
        # Load
        try:
            documents = load_documents(source)
            if not documents:
                log.warning("No documents to ingest")
                return 0
        except DocumentLoadError as e:
            raise IngestionError(
                "Document loading failed",
                details={"source": source, "step": "load"},
                original_error=e
            )

        # Chunk
        try:
            chunks = chunk_documents(documents, chunk_size, chunk_overlap)
        except ChunkingError as e:
            raise IngestionError(
                "Document chunking failed",
                details={"source": source, "step": "chunk", "doc_count": len(documents)},
                original_error=e
            )

        # Store in ChromaDB
        log.info("Storing chunks in ChromaDB", count=len(chunks))
        try:
            vector_store = get_vector_store()
            vector_store.add_documents(chunks)
        except (VectorStoreError, EmbeddingError) as e:
            raise IngestionError(
                "Vector store operation failed",
                details={"source": source, "step": "store", "chunk_count": len(chunks)},
                original_error=e
            )

        log.info("Successfully ingested chunks", count=len(chunks))
        return len(chunks)
    
    except IngestionError:
        raise
    except Exception as e:
        raise IngestionError(
            "Unexpected error during ingestion",
            details={"source": source},
            original_error=e
        )
