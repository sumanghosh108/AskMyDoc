"""
Ask My Doc — CLI Entry Point

Usage:
    python main.py ingest --source ./sample_docs/
    python main.py ingest --source https://example.com/page
    python main.py query "What is machine learning?"
    python main.py query "Explain the architecture" --top-k 10
"""

import argparse
import sys
import json
import uvicorn

from src.core.config import validate_config, LLM_MODEL
from src.utils.logger import get_logger

log = get_logger(__name__)


def cmd_ingest(args):
    """Handle the 'ingest' command."""
    from src.indexing.ingest import ingest_documents

    for source in args.source:
        try:
            count = ingest_documents(
                source,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
            )
            log.info("Ingestion complete", chunks=count, source=source)
        except Exception as e:
            log.error("Ingestion failed", source=source, error=str(e))
            sys.exit(1)


def cmd_query(args):
    """Handle the 'query' command."""
    from src.generation.enhanced_generator import generate_answer_enhanced

    question = args.question
    use_hybrid = not args.no_hybrid
    use_reranker = not args.no_reranker
    log.info("Starting query", question=question, hybrid=use_hybrid, reranker=use_reranker)

    result = generate_answer_enhanced(
        question,
        top_k=args.top_k,
        use_hybrid=use_hybrid,
        use_reranker=use_reranker,
        use_query_rewriting=args.query_rewriting,
        use_multi_hop=args.multi_hop,
        use_cache=args.cache,
    )

    # JSON output if requested
    if args.json:
        output = {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "metadata": result.get("metadata", {})
        }
        print(json.dumps(output, indent=2))
        return

    # Print answer using basic print for easy reading
    print("=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(result["answer"])

    # Print sources
    if result["sources"]:
        print("\n" + "-" * 60)
        print("SOURCES")
        print("-" * 60)
        for i, src in enumerate(result["sources"], 1):
            source_str = f"  {i}. {src['source']}"
            if "page" in src:
                source_str += f" (Page {src['page']})"
            if src.get("reranker_score") is not None:
                source_str += f" [score: {src['reranker_score']:.3f}]"
            print(source_str)
    
    # Print metadata if verbose
    if args.verbose and 'metadata' in result:
        print("\n" + "-" * 60)
        print("METADATA")
        print("-" * 60)
        metadata = result['metadata']
        
        if 'timings' in metadata:
            timings = metadata['timings']
            print(f"  Total time: {timings.get('total_time_ms', 0):.0f}ms")
            
            if 'components' in timings:
                print(f"  Component breakdown:")
                for comp, stats in timings['components'].items():
                    print(f"    - {comp}: {stats['total_ms']:.0f}ms")
        
        if 'features_used' in metadata:
            features = metadata['features_used']
            print(f"  Features used:")
            for feature, enabled in features.items():
                print(f"    - {feature}: {'✅' if enabled else '❌'}")
        
        if 'context_stats' in metadata:
            stats = metadata['context_stats']
            print(f"  Context stats:")
            print(f"    - Original chunks: {stats['original_count']}")
            print(f"    - Final chunks: {stats['final_count']}")
            print(f"    - Tokens used: {stats['tokens_used']}/{stats['token_limit']}")




def cmd_status(args):
    """Handle the 'status' command — show info about the vector store."""
    from src.indexing.ingest import get_vector_store

    vs = get_vector_store()
    collection = vs._collection
    count = collection.count()
    log.info("ChromaDB Status", collection=collection.name, documents_count=count)


def cmd_cache(args):
    """Handle cache management commands."""
    from src.caching import get_cache
    
    cache = get_cache()
    
    if args.cache_command == "clear":
        success = cache.clear_all()
        if success:
            print("✅ Cache cleared successfully")
        else:
            print("❌ Failed to clear cache (is Redis running?)")
            sys.exit(1)
    
    elif args.cache_command == "stats":
        stats = cache.get_stats()
        
        if not stats.get("enabled"):
            print("❌ Cache is not enabled")
            print("   Set CACHE_ENABLED=true in .env and ensure Redis is running")
            sys.exit(1)
        
        if not stats.get("connected"):
            print("❌ Cache is enabled but not connected to Redis")
            print(f"   Error: {stats.get('error', 'Unknown')}")
            sys.exit(1)
        
        print("📊 Cache Statistics:")
        print(f"  Status: ✅ Connected")
        print(f"  Total RAG keys: {stats.get('total_rag_keys', 0)}")
        print(f"  Keyspace hits: {stats.get('keyspace_hits', 0)}")
        print(f"  Keyspace misses: {stats.get('keyspace_misses', 0)}")
        print(f"  Hit rate: {stats.get('hit_rate', 0):.2%}")


def cmd_eval(args):
    """Run evaluation pipeline."""
    if args.ragas:
        from eval.ragas_evaluate import run_ragas_evaluation
        
        result = run_ragas_evaluation(
            dataset_path=args.dataset,
            threshold=args.threshold,
            use_hybrid=not args.no_hybrid,
            use_reranker=not args.no_reranker,
        )
        
        if "error" in result or not result["summary"]["passed"]:
            sys.exit(1)
    else:
        from eval.evaluate import run_evaluation
        
        result = run_evaluation(
            dataset_path=args.dataset,
            threshold=args.threshold,
            use_hybrid=not args.no_hybrid,
            use_reranker=not args.no_reranker,
        )
        
        if not result["summary"]["passed"]:
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Ask My Doc — Production RAG Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- ingest ---
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents into the vector store")
    ingest_parser.add_argument(
        "--source", "-s",
        nargs="+",
        required=True,
        help="File path(s), directory, or URL(s) to ingest",
    )
    ingest_parser.add_argument("--chunk-size", type=int, default=None, help="Override chunk size")
    ingest_parser.add_argument("--chunk-overlap", type=int, default=None, help="Override chunk overlap")

    # --- query ---
    query_parser = subparsers.add_parser("query", help="Ask a question")
    query_parser.add_argument("question", help="The question to ask")
    query_parser.add_argument("--top-k", type=int, default=None, help="Number of chunks to retrieve")
    query_parser.add_argument("--json", action="store_true", help="Also output JSON format")
    query_parser.add_argument("--no-hybrid", action="store_true", help="Disable hybrid retrieval (vector only)")
    query_parser.add_argument("--no-reranker", action="store_true", help="Disable cross-encoder reranking")
    query_parser.add_argument("--query-rewriting", action="store_true", help="Enable query rewriting")
    query_parser.add_argument("--multi-hop", action="store_true", help="Enable multi-hop retrieval")
    query_parser.add_argument("--cache", action="store_true", help="Enable caching")
    query_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed metadata")
    # --- status ---
    subparsers.add_parser("status", help="Show vector store status")
    
    # --- cache ---
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_parser.add_argument("cache_command", choices=["clear", "stats"], help="Cache operation")
    
    # --- eval ---
    eval_parser = subparsers.add_parser("eval", help="Run evaluation")
    eval_parser.add_argument("--dataset", type=str, default=None, help="Path to dataset")
    eval_parser.add_argument("--threshold", type=float, default=None, help="Quality threshold")
    eval_parser.add_argument("--no-hybrid", action="store_true", help="Disable hybrid retrieval")
    eval_parser.add_argument("--no-reranker", action="store_true", help="Disable reranker")
    eval_parser.add_argument("--ragas", action="store_true", help="Use RAGAS evaluation")

    # --- serve ---
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    serve_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload on file changes")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Validate config
    validate_config()

    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "cache":
        cmd_cache(args)
    elif args.command == "eval":
        cmd_eval(args)
    elif args.command == "serve":
        log.info("Starting FastAPI server", host=args.host, port=args.port)
        reload = not args.no_reload
        uvicorn.run("src.api.router:app", host=args.host, port=args.port, reload=reload)


if __name__ == "__main__":
    main()
