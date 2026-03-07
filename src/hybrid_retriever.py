"""
Hybrid retrieval module.
Combines BM25 keyword search with vector-based semantic search
using Reciprocal Rank Fusion (RRF).
"""

from typing import Optional

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from src.ingest import get_vector_store
from src.config import TOP_K, TOP_K_INITIAL
from src.logger import get_logger

log = get_logger(__name__)


class HybridRetriever:
    """
    Combines BM25 keyword search with ChromaDB vector search
    using Reciprocal Rank Fusion for result merging.
    """

    def __init__(self, top_k: Optional[int] = None, top_k_initial: Optional[int] = None):
        self.top_k = top_k or TOP_K
        self.top_k_initial = top_k_initial or TOP_K_INITIAL
        self.vector_store = get_vector_store()
        self._bm25_index = None
        self._bm25_docs = None

    def _build_bm25_index(self):
        """Build BM25 index from all documents in ChromaDB."""
        if self._bm25_index is not None:
            return

        collection = self.vector_store._collection
        all_data = collection.get(include=["documents", "metadatas"])

        if not all_data["documents"]:
            self._bm25_docs = []
            self._bm25_index = None
            return

        self._bm25_docs = []
        tokenized_corpus = []

        for i, (doc_text, metadata) in enumerate(zip(all_data["documents"], all_data["metadatas"])):
            self._bm25_docs.append(Document(
                page_content=doc_text,
                metadata=metadata or {},
            ))
            # Tokenize for BM25
            tokenized_corpus.append(doc_text.lower().split())

        self._bm25_index = BM25Okapi(tokenized_corpus)

    def _bm25_search(self, query: str, top_k: int) -> list[tuple[Document, float]]:
        """Perform BM25 keyword search."""
        self._build_bm25_index()

        if not self._bm25_docs or self._bm25_index is None:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25_index.get_scores(tokenized_query)

        # Get top-k indices
        scored_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for idx, score in scored_indices:
            if score > 0:
                doc = self._bm25_docs[idx]
                results.append((doc, score))

        return results

    def _vector_search(self, query: str, top_k: int) -> list[tuple[Document, float]]:
        """Perform vector similarity search."""
        # Use simple similarity search to avoid Langchain warnings about 
        # local embeddings returning distances that are negative / outside 0-1 bounds
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        return results

    def _reciprocal_rank_fusion(
        self,
        bm25_results: list[tuple[Document, float]],
        vector_results: list[tuple[Document, float]],
        k: int = 60,
    ) -> list[Document]:
        """
        Merge results using Reciprocal Rank Fusion (RRF).

        RRF score = sum(1 / (k + rank_i)) for each ranking list.

        Args:
            bm25_results: Results from BM25 search.
            vector_results: Results from vector search.
            k: RRF parameter (default 60).

        Returns:
            Merged and sorted list of Documents.
        """
        doc_scores = {}
        doc_map = {}

        # Score BM25 results
        for rank, (doc, _) in enumerate(bm25_results):
            doc_key = doc.page_content[:100]  # Use content prefix as key
            rrf_score = 1.0 / (k + rank + 1)
            doc_scores[doc_key] = doc_scores.get(doc_key, 0) + rrf_score
            doc.metadata["bm25_rank"] = rank + 1
            doc_map[doc_key] = doc

        # Score vector results
        for rank, (doc, similarity_score) in enumerate(vector_results):
            doc_key = doc.page_content[:100]
            rrf_score = 1.0 / (k + rank + 1)
            doc_scores[doc_key] = doc_scores.get(doc_key, 0) + rrf_score
            if doc_key not in doc_map:
                doc_map[doc_key] = doc
            doc_map[doc_key].metadata["vector_rank"] = rank + 1
            doc_map[doc_key].metadata["vector_similarity"] = round(similarity_score, 4)

        # Sort by RRF score
        sorted_keys = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)

        results = []
        for key in sorted_keys[:self.top_k_initial]:
            doc = doc_map[key]
            doc.metadata["rrf_score"] = round(doc_scores[key], 6)
            results.append(doc)

        return results

    def retrieve(self, query: str) -> list[Document]:
        """
        Perform hybrid retrieval: BM25 + Vector search + RRF fusion.

        Args:
            query: The user's question.

        Returns:
            Merged list of Documents sorted by RRF score.
        """
        # Get results from both retrievers
        bm25_results = self._bm25_search(query, top_k=self.top_k_initial)
        vector_results = self._vector_search(query, top_k=self.top_k_initial)

        # Merge with RRF
        merged = self._reciprocal_rank_fusion(bm25_results, vector_results)

        log.info(
            "Hybrid retrieval complete",
            bm25_candidates=len(bm25_results),
            vector_candidates=len(vector_results),
            merged_results=len(merged)
        )

        return merged
