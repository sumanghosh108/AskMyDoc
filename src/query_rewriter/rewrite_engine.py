"""
Query rewriting module for improving retrieval recall.
Handles spelling normalization, acronym expansion, and query expansion.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.core.config import LLM_MODEL, OPENROUTER_API_KEY
from src.utils.logger import get_logger

log = get_logger(__name__)


class QueryRewriter:
    """
    Rewrites user queries to improve retrieval quality.
    
    Strategies:
    - Spelling normalization
    - Acronym expansion
    - Query expansion (generate alternative phrasings)
    - Multi-query generation
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or LLM_MODEL
        self._llm = None
        self._chain = None

    def _get_llm(self) -> ChatOpenAI:
        """Lazy-load the LLM."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.3,
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Ask My Doc - Query Rewriter",
                }
            )
        return self._llm

    def _build_chain(self):
        """Build the query rewriting chain."""
        if self._chain is not None:
            return self._chain

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query rewriting assistant. Your task is to improve search queries.

Given a user query, generate 3 alternative versions that:
1. Fix any spelling errors
2. Expand acronyms and abbreviations
3. Rephrase using synonyms and related terms
4. Make the query more specific and searchable

Return ONLY the 3 rewritten queries, one per line, without numbering or explanation."""),
            ("human", "Original query: {query}\n\nGenerate 3 improved search queries:")
        ])

        self._chain = prompt | self._get_llm() | StrOutputParser()
        return self._chain

    def rewrite(self, query: str, include_original: bool = True) -> list[str]:
        """
        Generate multiple rewritten versions of the query.

        Args:
            query: Original user query.
            include_original: Whether to include the original query in results.

        Returns:
            List of query variations (including original if specified).
        """
        log.info("Rewriting query", original_query=query)

        chain = self._build_chain()
        
        try:
            result = chain.invoke({"query": query})
            
            # Parse the result into individual queries
            rewritten_queries = [
                q.strip() 
                for q in result.strip().split('\n') 
                if q.strip()
            ]
            
            # Deduplicate and filter
            unique_queries = []
            seen = set()
            
            if include_original and query.lower() not in seen:
                unique_queries.append(query)
                seen.add(query.lower())
            
            for q in rewritten_queries:
                if q.lower() not in seen:
                    unique_queries.append(q)
                    seen.add(q.lower())
            
            log.info(
                "Query rewriting complete",
                original=query,
                generated_count=len(rewritten_queries),
                unique_count=len(unique_queries)
            )
            
            return unique_queries
            
        except Exception as e:
            log.error("Query rewriting failed", error=str(e))
            # Fallback to original query
            return [query]

    def expand_acronyms(self, query: str) -> str:
        """
        Expand common acronyms in the query.
        
        This is a simple rule-based expansion. For production,
        consider using a domain-specific acronym dictionary.
        """
        acronym_map = {
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "nlp": "natural language processing",
            "llm": "large language model",
            "rag": "retrieval augmented generation",
            "api": "application programming interface",
            "db": "database",
            "sql": "structured query language",
        }
        
        words = query.split()
        expanded = []
        
        for word in words:
            lower_word = word.lower().strip('.,!?')
            if lower_word in acronym_map:
                expanded.append(f"{word} ({acronym_map[lower_word]})")
            else:
                expanded.append(word)
        
        return ' '.join(expanded)
