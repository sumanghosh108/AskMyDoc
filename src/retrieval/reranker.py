"""
LLM-based re-ranker module.
Re-scores (query, chunk) pairs using Groq LLM for relevance ranking.
Replaces the local CrossEncoder model with API-based reranking.
"""

import json
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.utils.logger import get_logger
from src.core.config import LLM_MODEL, GROQ_API_KEY, TOP_K

log = get_logger(__name__)


class Reranker:
    """
    LLM-based re-ranker that evaluates query-document relevance
    using the Groq API instead of a local cross-encoder model.
    """

    def __init__(self, model_name: Optional[str] = None, top_k: Optional[int] = None):
        self.model_name = model_name or LLM_MODEL
        self.top_k = top_k or TOP_K
        self._llm = None

    def _get_llm(self) -> ChatGroq:
        """Lazy-load the Groq LLM."""
        if self._llm is None:
            log.info("Initializing Groq LLM for reranking", model_name=self.model_name)
            self._llm = ChatGroq(
                model=self.model_name,
                temperature=0.0,
                api_key=GROQ_API_KEY,
            )
        return self._llm

    def rerank(self, query: str, documents: list[Document]) -> list[Document]:
        """
        Re-rank documents using the Groq LLM.

        Sends each document with the query to the LLM to get a relevance
        score, then sorts by score and returns the top-k results.

        Args:
            query: The user's query.
            documents: List of candidate documents to re-rank.

        Returns:
            Top-k documents sorted by LLM-assessed relevance score.
        """
        if not documents:
            return []

        llm = self._get_llm()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a relevance scoring assistant. Given a query and a list of document passages,
score each passage for relevance to the query on a scale of 0 to 10 (10 = perfectly relevant).

Return ONLY a valid JSON array of scores in the same order as the passages.
Example: [8, 3, 9, 1, 6]

Do not include any other text, explanation, or formatting."""),
            ("human", """Query: {query}

Passages:
{passages}

Return the relevance scores as a JSON array:""")
        ])

        # Format passages with indices
        passages_text = ""
        for i, doc in enumerate(documents):
            # Truncate long documents to stay within context limits
            content = doc.page_content[:500]
            passages_text += f"\n[{i+1}] {content}\n"

        chain = prompt | llm | StrOutputParser()

        try:
            result = chain.invoke({
                "query": query,
                "passages": passages_text,
            })

            # Parse scores from LLM response
            scores = json.loads(result.strip())

            if len(scores) != len(documents):
                log.warning(
                    "Score count mismatch, falling back to original order",
                    expected=len(documents),
                    got=len(scores),
                )
                return documents[:self.top_k]

        except (json.JSONDecodeError, Exception) as e:
            log.error("Failed to parse reranker scores, falling back to original order", error=str(e))
            return documents[:self.top_k]

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
