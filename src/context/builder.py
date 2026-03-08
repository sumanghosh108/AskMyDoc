"""
Context builder module.
Handles deduplication, relevance ordering, token limits, and metadata preservation.
"""

import tiktoken
from typing import Optional
from langchain_core.documents import Document

from src.core.config import LLM_MODEL
from src.utils.logger import get_logger

log = get_logger(__name__)


class ContextBuilder:
    """
    Builds optimized context for LLM generation.
    
    Features:
    - Remove duplicate chunks
    - Order by relevance score
    - Enforce token limits
    - Preserve source metadata
    - Format for LLM consumption
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        model_name: Optional[str] = None,
        preserve_order: bool = False
    ):
        self.max_tokens = max_tokens
        self.model_name = model_name or LLM_MODEL
        self.preserve_order = preserve_order
        self._tokenizer = None

    def _get_tokenizer(self):
        """Lazy-load the tokenizer."""
        if self._tokenizer is None:
            try:
                # Try to get encoding for the specific model
                self._tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
            except KeyError:
                # Fallback to cl100k_base (used by GPT-3.5 and GPT-4)
                self._tokenizer = tiktoken.get_encoding("cl100k_base")
        return self._tokenizer

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        tokenizer = self._get_tokenizer()
        return len(tokenizer.encode(text))

    def deduplicate(self, documents: list[Document]) -> list[Document]:
        """
        Remove duplicate documents based on content similarity.

        Uses content hash for exact duplicates and first 200 chars for near-duplicates.
        """
        if not documents:
            return []

        seen_hashes = set()
        seen_prefixes = set()
        unique_docs = []

        for doc in documents:
            content = doc.page_content.strip()
            
            # Check exact duplicate
            content_hash = hash(content)
            if content_hash in seen_hashes:
                continue
            
            # Check near-duplicate (first 200 chars)
            prefix = content[:200].lower()
            if prefix in seen_prefixes:
                continue
            
            seen_hashes.add(content_hash)
            seen_prefixes.add(prefix)
            unique_docs.append(doc)

        log.info(
            "Deduplication complete",
            original_count=len(documents),
            unique_count=len(unique_docs),
            duplicates_removed=len(documents) - len(unique_docs)
        )

        return unique_docs

    def sort_by_relevance(self, documents: list[Document]) -> list[Document]:
        """
        Sort documents by relevance score.

        Checks for multiple score fields in metadata:
        - reranker_score (highest priority)
        - rrf_score
        - vector_similarity
        """
        if not documents:
            return []

        def get_relevance_score(doc: Document) -> float:
            """Extract the best available relevance score."""
            metadata = doc.metadata
            
            # Priority order: reranker > rrf > vector similarity
            if "reranker_score" in metadata:
                return float(metadata["reranker_score"])
            elif "rrf_score" in metadata:
                return float(metadata["rrf_score"])
            elif "vector_similarity" in metadata:
                return float(metadata["vector_similarity"])
            else:
                return 0.0

        sorted_docs = sorted(
            documents,
            key=get_relevance_score,
            reverse=True
        )

        log.info("Documents sorted by relevance", count=len(sorted_docs))
        return sorted_docs

    def enforce_token_limit(
        self,
        documents: list[Document],
        max_tokens: Optional[int] = None
    ) -> list[Document]:
        """
        Truncate documents to fit within token limit.

        Args:
            documents: List of documents (should be sorted by relevance).
            max_tokens: Maximum tokens allowed (uses instance default if None).

        Returns:
            Truncated list of documents that fit within token limit.
        """
        limit = max_tokens or self.max_tokens
        
        if not documents:
            return []

        selected_docs = []
        total_tokens = 0

        for doc in documents:
            doc_tokens = self.count_tokens(doc.page_content)
            
            if total_tokens + doc_tokens <= limit:
                selected_docs.append(doc)
                total_tokens += doc_tokens
            else:
                # Check if we can fit a truncated version
                remaining_tokens = limit - total_tokens
                if remaining_tokens > 100:  # Only truncate if we have reasonable space
                    # Estimate characters per token (rough: 4 chars per token)
                    chars_to_keep = remaining_tokens * 4
                    truncated_content = doc.page_content[:chars_to_keep] + "..."
                    
                    truncated_doc = Document(
                        page_content=truncated_content,
                        metadata={**doc.metadata, "truncated": True}
                    )
                    selected_docs.append(truncated_doc)
                    total_tokens += self.count_tokens(truncated_content)
                
                break

        log.info(
            "Token limit enforced",
            original_docs=len(documents),
            selected_docs=len(selected_docs),
            total_tokens=total_tokens,
            limit=limit
        )

        return selected_docs

    def format_context(self, documents: list[Document]) -> str:
        """
        Format documents into a context string for LLM.

        Includes source metadata and chunk numbering.
        """
        if not documents:
            return ""

        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            source = metadata.get("source", "Unknown")
            page = metadata.get("page")
            
            # Build source citation
            citation = f"[Source {i}: {source}"
            if page is not None:
                citation += f", Page {page + 1}"
            citation += "]"
            
            # Add relevance info if available
            if "reranker_score" in metadata:
                citation += f" (Relevance: {metadata['reranker_score']:.3f})"
            
            # Format chunk
            chunk = f"{citation}\n{doc.page_content}\n"
            context_parts.append(chunk)

        context = "\n".join(context_parts)
        
        log.info(
            "Context formatted",
            chunks=len(documents),
            total_chars=len(context)
        )
        
        return context

    def build(
        self,
        documents: list[Document],
        max_tokens: Optional[int] = None
    ) -> dict:
        """
        Build optimized context from documents.

        Pipeline:
        1. Deduplicate
        2. Sort by relevance (unless preserve_order is True)
        3. Enforce token limit
        4. Format for LLM

        Args:
            documents: Raw documents from retrieval.
            max_tokens: Override instance max_tokens.

        Returns:
            Dictionary with 'context' (str), 'documents' (list), and 'stats' (dict).
        """
        if not documents:
            return {
                "context": "",
                "documents": [],
                "stats": {
                    "original_count": 0,
                    "final_count": 0,
                    "duplicates_removed": 0,
                    "tokens_used": 0
                }
            }

        original_count = len(documents)
        
        # Step 1: Deduplicate
        unique_docs = self.deduplicate(documents)
        duplicates_removed = original_count - len(unique_docs)
        
        # Step 2: Sort by relevance
        if not self.preserve_order:
            sorted_docs = self.sort_by_relevance(unique_docs)
        else:
            sorted_docs = unique_docs
        
        # Step 3: Enforce token limit
        final_docs = self.enforce_token_limit(sorted_docs, max_tokens)
        
        # Step 4: Format
        context = self.format_context(final_docs)
        tokens_used = self.count_tokens(context)

        stats = {
            "original_count": original_count,
            "final_count": len(final_docs),
            "duplicates_removed": duplicates_removed,
            "tokens_used": tokens_used,
            "token_limit": max_tokens or self.max_tokens
        }

        log.info("Context building complete", **stats)

        return {
            "context": context,
            "documents": final_docs,
            "stats": stats
        }
