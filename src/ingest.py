"""
Document ingestion module.
Handles loading, chunking, and embedding documents into ChromaDB.
Supports: PDF, Markdown, and web pages.
"""

import os
import glob
from pathlib import Path
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    WebBaseLoader,
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
)
from src.logger import get_logger

log = get_logger(__name__)


def _get_loader(file_path: str):
    """Return the appropriate document loader based on file extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext in (".md", ".markdown"):
        return UnstructuredMarkdownLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .md, .markdown")


def load_documents(source: str):
    """
    Load documents from a file path, directory, or URL.

    Args:
        source: A file path, directory path, or URL starting with http.

    Returns:
        List of LangChain Document objects.
    """
    documents = []

    if source.startswith("http://") or source.startswith("https://"):
        log.info("Loading web page", source=source)
        loader = WebBaseLoader(source)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = source
            doc.metadata["source_type"] = "web"
        documents.extend(docs)

    elif os.path.isfile(source):
        log.info("Loading file", source=source)
        loader = _get_loader(source)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = source
            doc.metadata["source_type"] = Path(source).suffix.lower()
        documents.extend(docs)

    elif os.path.isdir(source):
        patterns = ["**/*.pdf", "**/*.md", "**/*.markdown"]
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

    else:
        raise FileNotFoundError(f"Source not found: {source}")

    log.info("Loaded documents", count=len(documents))
    return documents


def chunk_documents(documents, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
    """
    Split documents into chunks with overlap.

    Args:
        documents: List of LangChain Document objects.
        chunk_size: Target chunk size in tokens (default from config).
        chunk_overlap: Overlap in tokens (default from config).

    Returns:
        List of chunked Document objects with metadata.
    """
    size = chunk_size or CHUNK_SIZE
    overlap = chunk_overlap or CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    # Enrich metadata with chunk index per source
    source_counters = {}
    for chunk in chunks:
        src = chunk.metadata.get("source", "unknown")
        idx = source_counters.get(src, 0)
        chunk.metadata["chunk_index"] = idx
        source_counters[src] = idx + 1

    log.info("Created chunks", count=len(chunks), chunk_size=size, chunk_overlap=overlap)
    return chunks


def get_vector_store(persist_directory: Optional[str] = None, collection_name: Optional[str] = None):
    """
    Get or create a ChromaDB vector store.

    Returns:
        Chroma vector store instance.
    """
    persist_dir = persist_directory or CHROMA_PERSIST_DIR
    col_name = collection_name or CHROMA_COLLECTION_NAME

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )

    vector_store = Chroma(
        collection_name=col_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    return vector_store


def ingest_documents(source: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
    """
    Full ingestion pipeline: load → chunk → embed → store.

    Args:
        source: File, directory, or URL to ingest.
        chunk_size: Optional override for chunk size.
        chunk_overlap: Optional override for chunk overlap.

    Returns:
        Number of chunks stored.
    """
    log.info("Ingesting documents", source=source)

    # Load
    documents = load_documents(source)
    if not documents:
        log.warning("No documents to ingest")
        return 0

    # Chunk
    chunks = chunk_documents(documents, chunk_size, chunk_overlap)

    # Store in ChromaDB
    log.info("Storing chunks in ChromaDB", count=len(chunks))
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    log.info("Successfully ingested chunks", count=len(chunks))
    return len(chunks)
