"""
Cross-encoder re-ranker module.
Re-scores (query, chunk) pairs using a cross-encoder model
for more accurate relevance ranking.
"""

from typing import Optional

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from src.logger import get_logger
from src.config import RERANKER_MODEL, TOP_K

log = get_logger(__name__)


class Reranker:
    """
    Cross-encoder re-ranker that evaluates query-document pairs together
    for more accurate relevance scoring.
    """

    def __init__(self, model_name: Optional[str] = None, top_k: Optional[int] = None):
        self.model_name = model_name or RERANKER_MODEL
        self.top_k = top_k or TOP_K
        self._model = None

    def _get_model(self) -> CrossEncoder:
        """Lazy-load the cross-encoder model."""
        if self._model is None:
            log.info("Loading reranker model", model_name=self.model_name)
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, documents: list[Document]) -> list[Document]:
        """
        Re-rank documents using the cross-encoder.

        Args:
            query: The user's query.
            documents: List of candidate documents to re-rank.

        Returns:
            Top-k documents sorted by cross-encoder relevance score.
        """
        if not documents:
            return []

        model = self._get_model()

        # Create (query, document) pairs
        pairs = [(query, doc.page_content) for doc in documents]

        # Get cross-encoder scores
        scores = model.predict(pairs)

        # Attach scores and sort
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Take top-k and enrich metadata
        results = []
        for rank, (doc, score) in enumerate(scored_docs[:self.top_k]):
            doc.metadata["reranker_score"] = round(float(score), 4)
            doc.metadata["reranker_rank"] = rank + 1
            results.append(doc)

        log.info("Re-ranking complete", input_docs=len(documents), output_docs=len(results))

        return results
