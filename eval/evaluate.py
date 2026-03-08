"""
Offline evaluation script for Ask My Doc RAG system.
Measures faithfulness and answer relevancy using the golden dataset.
Exits with non-zero code if quality drops below threshold.

Usage:
    python eval/evaluate.py
    python eval/evaluate.py --threshold 0.8
    python eval/evaluate.py --dataset eval/golden_dataset.json
"""

import json
import sys
import os
import time
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import EVAL_THRESHOLD, GOLDEN_DATASET_PATH, validate_config
from src.generation.generator import generate_answer


def load_golden_dataset(path: Optional[str] = None) -> list[dict]:
    """Load the golden evaluation dataset."""
    dataset_path = path or GOLDEN_DATASET_PATH
    with open(dataset_path, "r") as f:
        data = json.load(f)
    return data["dataset"]


def evaluate_single(item: dict, use_hybrid: bool = True, use_reranker: bool = True) -> dict:
    """
    Evaluate a single question from the golden dataset.

    Returns:
        Dictionary with evaluation results.
    """
    question = item["question"]
    ground_truth = item["ground_truth_answer"]

    # Generate answer
    result = generate_answer(
        question,
        use_hybrid=use_hybrid,
        use_reranker=use_reranker,
    )

    generated_answer = result["answer"]
    sources = result["sources"]
    context = result["context"]

    # --- Faithfulness Check ---
    # Check if the generated answer references context content
    # (Simple heuristic: token overlap between answer and context)
    answer_tokens = set(generated_answer.lower().split())
    context_tokens = set(context.lower().split())
    if context_tokens:
        overlap = len(answer_tokens & context_tokens)
        faithfulness_score = min(overlap / max(len(answer_tokens), 1), 1.0)
    else:
        faithfulness_score = 0.0

    # --- Answer Relevancy Check ---
    # Check overlap between generated answer and ground truth
    ground_truth_tokens = set(ground_truth.lower().split())
    if ground_truth_tokens:
        relevancy_overlap = len(answer_tokens & ground_truth_tokens)
        relevancy_score = min(relevancy_overlap / max(len(ground_truth_tokens), 1), 1.0)
    else:
        relevancy_score = 0.0

    # --- Source Check ---
    expected_sources = item.get("expected_sources", [])
    source_files = [os.path.basename(s["source"]) for s in sources]
    source_match = any(
        exp in source_files
        for exp in expected_sources
    ) if expected_sources else True

    return {
        "id": item["id"],
        "question": question,
        "ground_truth": ground_truth,
        "generated_answer": generated_answer[:200] + "..." if len(generated_answer) > 200 else generated_answer,
        "faithfulness_score": round(faithfulness_score, 4),
        "relevancy_score": round(relevancy_score, 4),
        "source_match": source_match,
        "sources_found": source_files,
        "expected_sources": expected_sources,
        "difficulty": item.get("difficulty", "unknown"),
    }


def run_evaluation(
    dataset_path: Optional[str] = None,
    threshold: Optional[float] = None,
    use_hybrid: bool = True,
    use_reranker: bool = True,
) -> dict:
    """
    Run full evaluation pipeline.

    Returns:
        Dictionary with overall results and per-question details.
    """
    threshold_val = threshold or EVAL_THRESHOLD
    dataset = load_golden_dataset(dataset_path)

    print(f"\n{'='*70}")
    print(f"📊 ASK MY DOC — EVALUATION PIPELINE")
    print(f"{'='*70}")
    print(f"  Dataset:    {dataset_path or GOLDEN_DATASET_PATH}")
    print(f"  Questions:  {len(dataset)}")
    print(f"  Threshold:  {threshold_val}")
    print(f"  Hybrid:     {use_hybrid}")
    print(f"  Reranker:   {use_reranker}")
    print(f"{'='*70}\n")

    results = []
    start_time = time.time()

    for i, item in enumerate(dataset, 1):
        print(f"\n[{i}/{len(dataset)}] Evaluating: {item['question'][:60]}...")
        try:
            result = evaluate_single(item, use_hybrid=use_hybrid, use_reranker=use_reranker)
            results.append(result)
            print(f"  ✅ Faithfulness: {result['faithfulness_score']:.2f} | "
                  f"Relevancy: {result['relevancy_score']:.2f} | "
                  f"Source Match: {'✅' if result['source_match'] else '❌'}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                "id": item["id"],
                "question": item["question"],
                "error": str(e),
                "faithfulness_score": 0.0,
                "relevancy_score": 0.0,
                "source_match": False,
            })

    elapsed = time.time() - start_time

    # Aggregate scores
    valid_results = [r for r in results if "error" not in r]
    avg_faithfulness = sum(r["faithfulness_score"] for r in valid_results) / max(len(valid_results), 1)
    avg_relevancy = sum(r["relevancy_score"] for r in valid_results) / max(len(valid_results), 1)
    source_accuracy = sum(1 for r in valid_results if r["source_match"]) / max(len(valid_results), 1)
    error_count = len(results) - len(valid_results)

    # Print summary
    print(f"\n{'='*70}")
    print(f"📊 EVALUATION RESULTS")
    print(f"{'='*70}")
    print(f"  Total Questions:     {len(dataset)}")
    print(f"  Successful:          {len(valid_results)}")
    print(f"  Errors:              {error_count}")
    print(f"  Avg Faithfulness:    {avg_faithfulness:.4f}")
    print(f"  Avg Relevancy:       {avg_relevancy:.4f}")
    print(f"  Source Accuracy:     {source_accuracy:.2%}")
    print(f"  Time Elapsed:        {elapsed:.1f}s")
    print(f"  Threshold:           {threshold_val}")

    passed = avg_faithfulness >= threshold_val
    print(f"\n  {'✅ PASSED' if passed else '❌ FAILED'}: "
          f"Faithfulness {avg_faithfulness:.4f} {'≥' if passed else '<'} {threshold_val}")
    print(f"{'='*70}\n")

    # Save results
    output = {
        "summary": {
            "total_questions": len(dataset),
            "successful": len(valid_results),
            "errors": error_count,
            "avg_faithfulness": round(avg_faithfulness, 4),
            "avg_relevancy": round(avg_relevancy, 4),
            "source_accuracy": round(source_accuracy, 4),
            "threshold": threshold_val,
            "passed": passed,
            "elapsed_seconds": round(elapsed, 1),
        },
        "details": results,
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / f"eval_results_{int(time.time())}.json"
    with open(results_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  📁 Results saved to: {results_file}")

    return output


def main():
    parser = argparse.ArgumentParser(description="Run RAG evaluation pipeline")
    parser.add_argument("--dataset", type=str, default=None, help="Path to golden dataset JSON")
    parser.add_argument("--threshold", type=float, default=None, help="Faithfulness threshold")
    parser.add_argument("--no-hybrid", action="store_true", help="Disable hybrid retrieval")
    parser.add_argument("--no-reranker", action="store_true", help="Disable reranker")
    args = parser.parse_args()

    validate_config()

    output = run_evaluation(
        dataset_path=args.dataset,
        threshold=args.threshold,
        use_hybrid=not args.no_hybrid,
        use_reranker=not args.no_reranker,
    )

    if not output["summary"]["passed"]:
        print("❌ Build failed: quality below threshold!")
        sys.exit(1)

    print("✅ All quality checks passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
