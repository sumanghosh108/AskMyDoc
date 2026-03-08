"""
Retrieval module.
Provides vector-based document retrieval from ChromaDB.
"""

from typing import Optional
from langchain_core.documents import Document

from src.indexing.ingest import get_vector_store
from src.core.config import TOP_K


def retrieve_chunks(query: str, top_k: Optional[int] = None) -> list[Document]:
    """
    Retrieve the top-k most relevant chunks for a query using vector similarity.

    Args:
        query: The user's question.
        top_k: Number of chunks to retrieve (default from config).

    Returns:
        List of Document objects with metadata and relevance scores.
    """
    k = top_k or TOP_K
    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_relevance_scores(query, k=k)

    documents = []
    for doc, score in results:
        doc.metadata["relevance_score"] = round(score, 4)
        documents.append(doc)

    return documents


def format_context(documents: list[Document]) -> str:
    """
    Format retrieved documents into a context string for the LLM.

    Args:
        documents: List of retrieved Document objects.

    Returns:
        Formatted context string with source citations.
    """
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", None)
        chunk_idx = doc.metadata.get("chunk_index", "?")
        score = doc.metadata.get("relevance_score", "N/A")

        header = f"[Chunk {i}] Source: {source}"
        if page is not None:
            header += f", Page: {page + 1}"  # 0-indexed to 1-indexed
        header += f", Chunk: {chunk_idx} (relevance: {score})"

        context_parts.append(f"{header}\n{doc.page_content}")

    return "\n\n---\n\n".join(context_parts)
