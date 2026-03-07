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

from src.config import validate_config
from src.logger import get_logger

log = get_logger(__name__)


def cmd_ingest(args):
    """Handle the 'ingest' command."""
    from src.ingest import ingest_documents

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
    from src.generator import generate_answer

    question = args.question
    use_hybrid = not args.no_hybrid
    use_reranker = not args.no_reranker
    log.info("Starting query", question=question, hybrid=use_hybrid, reranker=use_reranker)

    result = generate_answer(
        question,
        top_k=args.top_k,
        use_hybrid=use_hybrid,
        use_reranker=use_reranker,
    )

    # JSON output if requested
    if args.json:
        output = {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
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
            if src.get("relevance_score") is not None:
                source_str += f" [score: {src['relevance_score']}]"
            print(source_str)




def cmd_status(args):
    """Handle the 'status' command — show info about the vector store."""
    from src.ingest import get_vector_store

    vs = get_vector_store()
    collection = vs._collection
    count = collection.count()
    log.info("ChromaDB Status", collection=collection.name, documents_count=count)


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
    # --- status ---
    subparsers.add_parser("status", help="Show vector store status")

    # --- serve ---
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

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
    elif args.command == "serve":
        log.info("Starting FastAPI server", host=args.host, port=args.port)
        uvicorn.run("src.api:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
