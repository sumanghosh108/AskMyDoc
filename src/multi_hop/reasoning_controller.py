"""
Multi-hop retrieval controller.
Detects when additional context is needed and triggers iterative retrieval.
"""

from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from src.core.config import LLM_MODEL, GROQ_API_KEY
from src.utils.logger import get_logger

log = get_logger(__name__)


class MultiHopController:
    """
    Controls multi-hop retrieval for complex questions requiring multiple reasoning steps.
    
    Example:
        "Which drugs approved in 2022 treat diseases discovered after 2015?"
        
        Step 1: Retrieve drugs approved in 2022
        Step 2: Extract diseases from those drugs
        Step 3: Retrieve disease discovery dates
        Step 4: Filter and combine results
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        max_hops: int = 3,
        min_confidence: float = 0.6
    ):
        self.model_name = model_name or LLM_MODEL
        self.max_hops = max_hops
        self.min_confidence = min_confidence
        self._llm = None

    def _get_llm(self) -> ChatGroq:
        """Lazy-load the LLM."""
        if self._llm is None:
            self._llm = ChatGroq(
                model=self.model_name,
                temperature=0.1,
                api_key=GROQ_API_KEY,
            )
        return self._llm

    def needs_multi_hop(self, question: str, initial_context: str) -> dict:
        """
        Determine if the question requires multi-hop retrieval.

        Args:
            question: The user's question.
            initial_context: Context from initial retrieval.

        Returns:
            Dictionary with 'needs_hop' (bool) and 'reason' (str).
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an analysis assistant. Determine if a question requires multiple retrieval steps.

A question needs multi-hop retrieval if:
1. It asks about relationships between entities (e.g., "drugs that treat diseases discovered after X")
2. It requires information from multiple documents to be combined
3. The initial context is incomplete or missing key information
4. It involves temporal reasoning or comparisons

Respond with ONLY "YES" or "NO" followed by a brief reason (one sentence)."""),
            ("human", """Question: {question}

Initial Context:
{context}

Does this require multi-hop retrieval?""")
        ])

        chain = prompt | self._get_llm() | StrOutputParser()
        
        try:
            result = chain.invoke({
                "question": question,
                "context": initial_context[:1000]  # Limit context size
            })
            
            result_lower = result.lower()
            needs_hop = result_lower.startswith("yes")
            
            log.info(
                "Multi-hop analysis complete",
                question=question[:100],
                needs_hop=needs_hop,
                reason=result
            )
            
            return {
                "needs_hop": needs_hop,
                "reason": result,
                "confidence": 0.8 if needs_hop else 0.9
            }
            
        except Exception as e:
            log.error("Multi-hop analysis failed", error=str(e))
            return {"needs_hop": False, "reason": "Analysis failed", "confidence": 0.0}

    def generate_follow_up_query(
        self,
        original_question: str,
        current_context: str,
        hop_number: int
    ) -> Optional[str]:
        """
        Generate a follow-up query for the next retrieval hop.

        Args:
            original_question: The original user question.
            current_context: Context gathered so far.
            hop_number: Current hop number (1-indexed).

        Returns:
            Follow-up query string, or None if no more hops needed.
        """
        if hop_number >= self.max_hops:
            log.info("Max hops reached", max_hops=self.max_hops)
            return None

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query generation assistant for multi-hop retrieval.

Given an original question and the context gathered so far, generate a focused follow-up query
to retrieve missing information.

The follow-up query should:
1. Target specific missing information
2. Be concise and searchable
3. Build on what we already know
4. Help answer the original question

Respond with ONLY the follow-up query, or "COMPLETE" if no more information is needed."""),
            ("human", """Original Question: {question}

Context Gathered So Far:
{context}

Hop Number: {hop_number}

Generate the next follow-up query:""")
        ])

        chain = prompt | self._get_llm() | StrOutputParser()
        
        try:
            result = chain.invoke({
                "question": original_question,
                "context": current_context[:2000],
                "hop_number": hop_number
            })
            
            result = result.strip()
            
            if result.upper() == "COMPLETE" or not result:
                log.info("Multi-hop retrieval complete", hop_number=hop_number)
                return None
            
            log.info(
                "Follow-up query generated",
                hop_number=hop_number,
                query=result
            )
            
            return result
            
        except Exception as e:
            log.error("Follow-up query generation failed", error=str(e))
            return None

    def merge_contexts(
        self,
        contexts: list[str],
        original_question: str
    ) -> str:
        """
        Merge multiple contexts from different hops into a coherent context.

        Args:
            contexts: List of context strings from each hop.
            original_question: The original question for relevance filtering.

        Returns:
            Merged context string.
        """
        if not contexts:
            return ""
        
        if len(contexts) == 1:
            return contexts[0]

        # Simple merging: concatenate with separators
        # In production, you might want to use LLM-based summarization
        merged = "\n\n--- Retrieved Context (Multiple Hops) ---\n\n"
        
        for i, ctx in enumerate(contexts, 1):
            merged += f"[Hop {i}]\n{ctx}\n\n"
        
        log.info(
            "Contexts merged",
            hop_count=len(contexts),
            total_length=len(merged)
        )
        
        return merged

    def execute_multi_hop_retrieval(
        self,
        question: str,
        retriever_fn,
        initial_docs: Optional[list[Document]] = None
    ) -> dict:
        """
        Execute multi-hop retrieval pipeline.

        Args:
            question: The user's question.
            retriever_fn: Function that takes a query and returns documents.
            initial_docs: Optional initial documents from first retrieval.

        Returns:
            Dictionary with 'documents', 'contexts', and 'hop_count'.
        """
        all_documents = []
        contexts = []
        
        # Start with initial retrieval
        if initial_docs is None:
            log.info("Executing initial retrieval")
            initial_docs = retriever_fn(question)
        
        all_documents.extend(initial_docs)
        initial_context = "\n\n".join([doc.page_content for doc in initial_docs])
        contexts.append(initial_context)
        
        # Check if multi-hop is needed
        analysis = self.needs_multi_hop(question, initial_context)
        
        if not analysis["needs_hop"]:
            log.info("Single-hop retrieval sufficient")
            return {
                "documents": all_documents,
                "contexts": contexts,
                "hop_count": 1,
                "multi_hop_used": False
            }
        
        # Execute additional hops
        current_context = initial_context
        hop_number = 1
        
        while hop_number < self.max_hops:
            hop_number += 1
            
            # Generate follow-up query
            follow_up_query = self.generate_follow_up_query(
                question,
                current_context,
                hop_number
            )
            
            if follow_up_query is None:
                break
            
            # Retrieve with follow-up query
            log.info("Executing hop retrieval", hop_number=hop_number, query=follow_up_query)
            hop_docs = retriever_fn(follow_up_query)
            
            if not hop_docs:
                log.info("No documents found in hop", hop_number=hop_number)
                break
            
            # Add to collection
            all_documents.extend(hop_docs)
            hop_context = "\n\n".join([doc.page_content for doc in hop_docs])
            contexts.append(hop_context)
            current_context = self.merge_contexts(contexts, question)
        
        log.info(
            "Multi-hop retrieval complete",
            total_hops=hop_number,
            total_documents=len(all_documents)
        )
        
        return {
            "documents": all_documents,
            "contexts": contexts,
            "hop_count": hop_number,
            "multi_hop_used": True
        }
