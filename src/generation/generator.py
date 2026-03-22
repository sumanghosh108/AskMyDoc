"""
Answer generation module.
Loads versioned prompts, builds LLM chain, generates cited answers.
Supports both basic vector retrieval and hybrid retrieval + reranking.

Uses Groq (free tier) for LLM inference.
"""

from pathlib import Path
from typing import Optional

import yaml
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from src.core.config import (
    LLM_MODEL,
    GROQ_API_KEY,
    get_prompt_config_path,
)
from src.retrieval.base import retrieve_chunks, format_context
from src.utils.logger import get_logger

log = get_logger(__name__)


def _load_prompts(config_path: Optional[Path] = None) -> dict:
    """Load prompt templates from versioned YAML config."""
    path = config_path or get_prompt_config_path()
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config["qa_prompt"]


def build_chain(prompts: Optional[dict] = None):
    """
    Build the generation chain: prompt -> LLM -> output parser.

    Uses Groq API with free-tier models (e.g., llama-3.3-70b-versatile).

    Returns:
        A LangChain runnable chain.
    """
    if prompts is None:
        prompts = _load_prompts()

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"]),
    ])

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=0.1,
        api_key=GROQ_API_KEY,
    )

    chain = prompt | llm | StrOutputParser()
    return chain


def generate_answer(
    question: str,
    retrieved_docs: Optional[list[Document]] = None,
    top_k: Optional[int] = None,
    use_hybrid: bool = True,
    use_reranker: bool = True,
) -> dict:
    """
    Generate an answer with citations for a given question.

    Args:
        question: The user's question.
        retrieved_docs: Optional pre-retrieved documents.
        top_k: Number of chunks to retrieve if retrieved_docs not provided.
        use_hybrid: Whether to use hybrid retrieval (BM25 + vector).
        use_reranker: Whether to apply cross-encoder reranking.

    Returns:
        Dictionary with 'answer', 'sources', and 'context'.
    """
    # Retrieve if not already provided
    if retrieved_docs is None:
        if use_hybrid:
            from src.retrieval.hybrid import HybridRetriever
            log.info("Using Hybrid Retriever (BM25 + Vector)")
            retriever = HybridRetriever(top_k=top_k)
            retrieved_docs = retriever.retrieve(question)
        else:
            log.info("Using standard Vector Retriever")
            retrieved_docs = retrieve_chunks(question, top_k=top_k)

    if not retrieved_docs:
        return {
            "answer": "I couldn't find any relevant documents to answer your question. "
                      "Please make sure documents have been ingested first.",
            "sources": [],
            "context": "",
        }

    # Rerank if enabled
    if use_reranker:
        from src.retrieval.reranker import Reranker
        log.info("Re-ranking documents")
        reranker = Reranker(top_k=top_k)
        retrieved_docs = reranker.rerank(question, retrieved_docs)

    # Format context
    context = format_context(retrieved_docs)

    # Generate
    log.info("Invoking LLM chain (Groq)")
    chain = build_chain()
    answer = chain.invoke({
        "context": context,
        "question": question,
    })
    log.info("Generation complete", context_chunks=len(retrieved_docs))

    # Extract unique sources
    sources = []
    seen = set()
    for doc in retrieved_docs:
        src = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", None)
        key = (src, page)
        if key not in seen:
            seen.add(key)
            source_info = {"source": src}
            if page is not None:
                source_info["page"] = page + 1
            source_info["relevance_score"] = doc.metadata.get("relevance_score", None)
            source_info["reranker_score"] = doc.metadata.get("reranker_score", None)
            sources.append(source_info)

    return {
        "answer": answer,
        "sources": sources,
        "context": context,
    }
