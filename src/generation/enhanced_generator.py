"""
Enhanced answer generation module with all production features.
Integrates query rewriting, multi-hop retrieval, context building, and caching.
"""

import hashlib
from typing import Optional
from langchain_core.documents import Document

from src.core.config import (
    CACHE_ENABLED,
    REDIS_HOST,
    REDIS_PORT,
    MAX_CONTEXT_TOKENS,
    QUERY_REWRITING_ENABLED,
    MULTI_HOP_ENABLED,
    MAX_HOPS,
)
from src.generation.generator import build_chain
from src.query_rewriter import QueryRewriter
from src.multi_hop import MultiHopController
from src.context import ContextBuilder
from src.caching import get_cache
from src.observability import LatencyTracker, get_metrics
from src.utils.logger import get_logger

log = get_logger(__name__)


def _hash_context(context: str) -> str:
    """Generate hash of context for caching."""
    return hashlib.sha256(context.encode()).hexdigest()[:16]


def generate_answer_enhanced(
    question: str,
    retrieved_docs: Optional[list[Document]] = None,
    top_k: Optional[int] = None,
    use_hybrid: bool = True,
    use_reranker: bool = True,
    use_query_rewriting: Optional[bool] = None,
    use_multi_hop: Optional[bool] = None,
    use_cache: Optional[bool] = None,
    max_context_tokens: Optional[int] = None,
) -> dict:
    """
    Enhanced answer generation with all production features.

    Features:
    - Query rewriting for better retrieval
    - Multi-hop retrieval for complex questions
    - Context building with deduplication and token limits
    - Redis caching for retrieval and responses
    - Comprehensive latency tracking

    Args:
        question: The user's question.
        retrieved_docs: Optional pre-retrieved documents.
        top_k: Number of chunks to retrieve.
        use_hybrid: Whether to use hybrid retrieval.
        use_reranker: Whether to apply reranking.
        use_query_rewriting: Whether to rewrite queries (default from config).
        use_multi_hop: Whether to use multi-hop retrieval (default from config).
        use_cache: Whether to use caching (default from config).
        max_context_tokens: Maximum context tokens (default from config).

    Returns:
        Dictionary with 'answer', 'sources', 'context', 'metadata'.
    """
    # Initialize tracker
    tracker = LatencyTracker()
    tracker.start()

    # Apply defaults from config
    use_query_rewriting = use_query_rewriting if use_query_rewriting is not None else QUERY_REWRITING_ENABLED
    use_multi_hop = use_multi_hop if use_multi_hop is not None else MULTI_HOP_ENABLED
    use_cache = use_cache if use_cache is not None else CACHE_ENABLED
    max_context_tokens = max_context_tokens or MAX_CONTEXT_TOKENS

    # Initialize cache
    cache = get_cache(host=REDIS_HOST, port=REDIS_PORT, enabled=use_cache)

    # Build retrieval config for cache key
    retrieval_config = {
        "top_k": top_k,
        "use_hybrid": use_hybrid,
        "use_reranker": use_reranker,
        "use_query_rewriting": use_query_rewriting,
        "use_multi_hop": use_multi_hop,
    }

    # Check response cache first
    if use_cache and retrieved_docs is None:
        with tracker.track("cache_check", cache_type="response"):
            # We'll check after retrieval since we need context hash
            pass

    # Query rewriting
    queries_to_search = [question]
    if use_query_rewriting and retrieved_docs is None:
        with tracker.track("query_rewriting"):
            try:
                rewriter = QueryRewriter()
                queries_to_search = rewriter.rewrite(question, include_original=True)
                log.info("Query rewriting enabled", query_count=len(queries_to_search))
            except Exception as e:
                log.error("Query rewriting failed, using original", error=str(e))
                
                # Log error to database
                try:
                    from database.error_logger import get_error_logger
                    error_logger = get_error_logger()
                    error_logger.log_exception(
                        exception=e,
                        pipeline_stage="query_rewriting",
                        query_text=question,
                        severity="ERROR"
                    )
                except Exception as log_error:
                    log.error("Error logging failed", error=str(log_error))
                
                queries_to_search = [question]

    # Retrieval
    if retrieved_docs is None:
        # Check retrieval cache
        cached_docs = None
        if use_cache:
            with tracker.track("cache_check", cache_type="retrieval"):
                cached_docs = cache.get_retrieval(question, retrieval_config)

        if cached_docs:
            retrieved_docs = cached_docs
            log.info("Using cached retrieval results", doc_count=len(cached_docs))
        else:
            # Perform retrieval for each query variation
            all_docs = []
            
            for query in queries_to_search:
                with tracker.track("retrieval", query=query[:50], method="hybrid" if use_hybrid else "vector"):
                    if use_hybrid:
                        from src.retrieval.hybrid import HybridRetriever
                        retriever = HybridRetriever(top_k=top_k)
                        docs = retriever.retrieve(query)
                    else:
                        from src.retrieval.base import retrieve_chunks
                        docs = retrieve_chunks(query, top_k=top_k)
                    
                    all_docs.extend(docs)
            
            retrieved_docs = all_docs
            
            # Cache retrieval results
            if use_cache:
                with tracker.track("cache_set", cache_type="retrieval"):
                    cache.set_retrieval(question, retrieval_config, retrieved_docs)

    if not retrieved_docs:
        tracker.end()
        return {
            "answer": "I couldn't find any relevant documents to answer your question.",
            "sources": [],
            "context": "",
            "metadata": {
                "timings": tracker.get_summary(),
                "features_used": {
                    "query_rewriting": use_query_rewriting,
                    "multi_hop": False,
                    "cache": use_cache,
                }
            }
        }

    # Multi-hop retrieval
    multi_hop_used = False
    if use_multi_hop:
        with tracker.track("multi_hop_analysis"):
            try:
                controller = MultiHopController(max_hops=MAX_HOPS)
                
                # Create retriever function for multi-hop
                def retriever_fn(query: str) -> list[Document]:
                    if use_hybrid:
                        from src.retrieval.hybrid import HybridRetriever
                        retriever = HybridRetriever(top_k=top_k)
                        return retriever.retrieve(query)
                    else:
                        from src.retrieval.base import retrieve_chunks
                        return retrieve_chunks(query, top_k=top_k)
                
                # Execute multi-hop
                multi_hop_result = controller.execute_multi_hop_retrieval(
                    question,
                    retriever_fn,
                    initial_docs=retrieved_docs
                )
                
                retrieved_docs = multi_hop_result["documents"]
                multi_hop_used = multi_hop_result["multi_hop_used"]
                
                log.info(
                    "Multi-hop retrieval complete",
                    hop_count=multi_hop_result["hop_count"],
                    multi_hop_used=multi_hop_used
                )
            except Exception as e:
                log.error("Multi-hop retrieval failed, using initial docs", error=str(e))
                
                # Log error to database
                try:
                    from database.error_logger import get_error_logger
                    error_logger = get_error_logger()
                    error_logger.log_exception(
                        exception=e,
                        pipeline_stage="multi_hop",
                        query_text=question,
                        severity="ERROR"
                    )
                except Exception as log_error:
                    log.error("Error logging failed", error=str(log_error))

    # Reranking
    if use_reranker:
        with tracker.track("reranking", doc_count=len(retrieved_docs)):
            try:
                from src.retrieval.reranker import Reranker
                reranker = Reranker(top_k=top_k)
                retrieved_docs = reranker.rerank(question, retrieved_docs)
            except Exception as e:
                log.error("Reranking failed, using unranked docs", error=str(e))
                
                # Log error to database
                try:
                    from database.error_logger import get_error_logger
                    error_logger = get_error_logger()
                    error_logger.log_exception(
                        exception=e,
                        pipeline_stage="reranking",
                        query_text=question,
                        severity="ERROR"
                    )
                except Exception as log_error:
                    log.error("Error logging failed", error=str(log_error))

    # Context building
    with tracker.track("context_building", max_tokens=max_context_tokens):
        builder = ContextBuilder(max_tokens=max_context_tokens)
        context_result = builder.build(retrieved_docs, max_tokens=max_context_tokens)
        
        context = context_result["context"]
        final_docs = context_result["documents"]
        context_stats = context_result["stats"]

    # Check response cache
    context_hash = _hash_context(context)
    generation_config = {"model": "default", "temperature": 0.1}
    
    cached_response = None
    if use_cache:
        with tracker.track("cache_check", cache_type="response"):
            cached_response = cache.get_response(question, context_hash, generation_config)

    if cached_response:
        log.info("Using cached response")
        tracker.end()
        
        # Add timing metadata
        cached_response["metadata"]["timings"] = tracker.get_summary()
        cached_response["metadata"]["cache_hit"] = True
        
        return cached_response

    # LLM generation
    with tracker.track("llm_generation", context_tokens=context_stats["tokens_used"]):
        chain = build_chain()
        answer = chain.invoke({
            "context": context,
            "question": question,
        })

    # Extract sources
    sources = []
    seen = set()
    for doc in final_docs:
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

    # Build response
    response = {
        "answer": answer,
        "sources": sources,
        "context": context,
        "metadata": {
            "context_stats": context_stats,
            "features_used": {
                "query_rewriting": use_query_rewriting,
                "multi_hop": multi_hop_used,
                "reranking": use_reranker,
                "cache": use_cache,
            },
            "queries_used": queries_to_search if use_query_rewriting else [question],
        }
    }

    # Cache response
    if use_cache:
        with tracker.track("cache_set", cache_type="response"):
            cache.set_response(question, context_hash, generation_config, response)

    # Finalize tracking
    tracker.end()
    tracker.log_summary(question)
    
    response["metadata"]["timings"] = tracker.get_summary()
    response["metadata"]["cache_hit"] = False

    # Record metrics
    metrics = get_metrics()
    metrics.record(tracker, question, success=True)

    # Log query to PostgreSQL database
    try:
        from database.query_logger import get_query_logger
        
        query_logger = get_query_logger()
        summary = tracker.get_summary()
        
        # Extract component latencies
        retrieval_latency = None
        rerank_latency = None
        llm_latency = None
        
        if "retrieval" in summary.get("components", {}):
            retrieval_latency = summary["components"]["retrieval"]["total_ms"]
        if "reranking" in summary.get("components", {}):
            rerank_latency = summary["components"]["reranking"]["total_ms"]
        if "llm_generation" in summary.get("components", {}):
            llm_latency = summary["components"]["llm_generation"]["total_ms"]
        
        query_log_id = query_logger.log_query(
            query_text=question,
            total_latency=summary.get("total_time_ms", 0),
            retrieval_latency=retrieval_latency,
            rerank_latency=rerank_latency,
            llm_latency=llm_latency,
            retrieved_chunks=len(retrieved_docs) if retrieved_docs else None,
            reranked_chunks=len(final_docs) if use_reranker else None,
            model_used="default",
            query_rewriting_enabled=use_query_rewriting,
            multi_hop_enabled=multi_hop_used,
            cache_hit=False,
            answer_length=len(answer) if answer else None,
            source_count=len(sources)
        )
        
        if query_log_id:
            log.debug("Query logged to database", record_id=query_log_id)
            
            # Log component latencies retroactively
            try:
                for component, timings in tracker.timings.items():
                    for timing in timings:
                        query_logger.log_component_latency(
                            query_log_id=query_log_id,
                            component_name=component,
                            latency_ms=timing["duration_ms"],
                            metadata=timing.get("metadata")
                        )
            except Exception as comp_error:
                log.error("Component latency logging failed", error=str(comp_error))
        else:
            log.warning("Query logging returned None, continuing without database logging")
            
    except Exception as e:
        log.error("Query logging failed", error=str(e))
        # Continue execution - don't raise

    return response
