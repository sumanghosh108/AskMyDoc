"""
RAGAS-based evaluation pipeline for Ask My Doc RAG system.
Uses the RAGAS library for comprehensive evaluation metrics.

Metrics:
- Faithfulness: How grounded the answer is in the context
- Answer Relevancy: How relevant the answer is to the question
- Context Precision: How precise the retrieved context is
- Context Recall: How much of the ground truth is captured

Usage:
    python eval/ragas_evaluate.py
    python eval/ragas_evaluate.py --threshold 0.8
    python eval/ragas_evaluate.py --dataset eval/golden_dataset.json
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

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from src.core.config import EVAL_THRESHOLD, GOLDEN_DATASET_PATH, validate_config
from src.generation.enhanced_generator import generate_answer_enhanced
from src.utils.logger import get_logger

log = get_logger(__name__)


def load_golden_dataset(path: Optional[str] = None) -> list[dict]:
    """Load the golden evaluation dataset."""
    dataset_path = path or GOLDEN_DATASET_PATH
    with open(dataset_path, "r") as f:
        data = json.load(f)
    return data["dataset"]


def prepare_ragas_dataset(
    golden_data: list[dict],
    use_hybrid: bool = True,
    use_reranker: bool = True,
) -> Dataset:
    """
    Prepare dataset in RAGAS format.

    RAGAS expects:
    - question: The question
    - answer: Generated answer
    - contexts: List of context strings used
    - ground_truth: Ground truth answer

    Args:
        golden_data: List of golden dataset items.
        use_hybrid: Whether to use hybrid retrieval.
        use_reranker: Whether to use reranker.

    Returns:
        HuggingFace Dataset object.
    """
    ragas_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    print(f"\n{'='*70}")
    print(f"📊 PREPARING RAGAS EVALUATION DATASET")
    print(f"{'='*70}\n")

    for i, item in enumerate(golden_data, 1):
        question = item["question"]
        ground_truth = item["ground_truth_answer"]

        print(f"[{i}/{len(golden_data)}] Processing: {question[:60]}...")

        try:
            # Generate answer using the RAG system
            result = generate_answer_enhanced(
                question,
                use_hybrid=use_hybrid,
                use_reranker=use_reranker,
                use_cache=False,  # Disable cache for evaluation
            )

            answer = result["answer"]
            context = result["context"]

            # RAGAS expects contexts as a list of strings
            # Split by source markers
            context_chunks = []
            for line in context.split("\n\n"):
                if line.strip() and not line.startswith("[Source"):
                    context_chunks.append(line.strip())

            if not context_chunks:
                context_chunks = [context]

            ragas_data["question"].append(question)
            ragas_data["answer"].append(answer)
            ragas_data["contexts"].append(context_chunks)
            ragas_data["ground_truth"].append(ground_truth)

            print(f"  ✅ Generated answer ({len(answer)} chars, {len(context_chunks)} contexts)")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            # Add placeholder to maintain dataset alignment
            ragas_data["question"].append(question)
            ragas_data["answer"].append("Error generating answer")
            ragas_data["contexts"].append([""])
            ragas_data["ground_truth"].append(ground_truth)

    # Convert to HuggingFace Dataset
    dataset = Dataset.from_dict(ragas_data)
    
    print(f"\n✅ Dataset prepared: {len(dataset)} samples\n")
    
    return dataset


def run_ragas_evaluation(
    dataset_path: Optional[str] = None,
    threshold: Optional[float] = None,
    use_hybrid: bool = True,
    use_reranker: bool = True,
) -> dict:
    """
    Run RAGAS evaluation pipeline.

    Args:
        dataset_path: Path to golden dataset JSON.
        threshold: Minimum threshold for passing.
        use_hybrid: Whether to use hybrid retrieval.
        use_reranker: Whether to use reranker.

    Returns:
        Dictionary with evaluation results.
    """
    threshold_val = threshold or EVAL_THRESHOLD
    golden_data = load_golden_dataset(dataset_path)

    print(f"\n{'='*70}")
    print(f"📊 ASK MY DOC — RAGAS EVALUATION PIPELINE")
    print(f"{'='*70}")
    print(f"  Dataset:    {dataset_path or GOLDEN_DATASET_PATH}")
    print(f"  Questions:  {len(golden_data)}")
    print(f"  Threshold:  {threshold_val}")
    print(f"  Hybrid:     {use_hybrid}")
    print(f"  Reranker:   {use_reranker}")
    print(f"{'='*70}\n")

    start_time = time.time()

    # Prepare dataset
    dataset = prepare_ragas_dataset(golden_data, use_hybrid, use_reranker)

    # Run RAGAS evaluation
    print(f"\n{'='*70}")
    print(f"🔍 RUNNING RAGAS METRICS")
    print(f"{'='*70}\n")

    try:
        # Evaluate with RAGAS metrics
        results = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )

        # Extract scores
        scores = {
            "faithfulness": results["faithfulness"],
            "answer_relevancy": results["answer_relevancy"],
            "context_precision": results["context_precision"],
            "context_recall": results["context_recall"],
        }

        # Calculate average
        avg_score = sum(scores.values()) / len(scores)

    except Exception as e:
        print(f"❌ RAGAS evaluation failed: {e}")
        log.error("RAGAS evaluation failed", error=str(e))
        return {
            "error": str(e),
            "passed": False
        }

    elapsed = time.time() - start_time

    # Print results
    print(f"\n{'='*70}")
    print(f"📊 RAGAS EVALUATION RESULTS")
    print(f"{'='*70}")
    print(f"  Total Questions:     {len(golden_data)}")
    print(f"  Faithfulness:        {scores['faithfulness']:.4f}")
    print(f"  Answer Relevancy:    {scores['answer_relevancy']:.4f}")
    print(f"  Context Precision:   {scores['context_precision']:.4f}")
    print(f"  Context Recall:      {scores['context_recall']:.4f}")
    print(f"  Average Score:       {avg_score:.4f}")
    print(f"  Time Elapsed:        {elapsed:.1f}s")
    print(f"  Threshold:           {threshold_val}")

    passed = scores["faithfulness"] >= threshold_val
    print(f"\n  {'✅ PASSED' if passed else '❌ FAILED'}: "
          f"Faithfulness {scores['faithfulness']:.4f} {'≥' if passed else '<'} {threshold_val}")
    print(f"{'='*70}\n")

    # Save results
    output = {
        "summary": {
            "total_questions": len(golden_data),
            "faithfulness": round(scores["faithfulness"], 4),
            "answer_relevancy": round(scores["answer_relevancy"], 4),
            "context_precision": round(scores["context_precision"], 4),
            "context_recall": round(scores["context_recall"], 4),
            "average_score": round(avg_score, 4),
            "threshold": threshold_val,
            "passed": passed,
            "elapsed_seconds": round(elapsed, 1),
        },
        "ragas_results": results.to_pandas().to_dict(orient="records"),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / f"ragas_eval_{int(time.time())}.json"
    
    with open(results_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"  📁 Results saved to: {results_file}")

    return output


def main():
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation pipeline")
    parser.add_argument("--dataset", type=str, default=None, help="Path to golden dataset JSON")
    parser.add_argument("--threshold", type=float, default=None, help="Faithfulness threshold")
    parser.add_argument("--no-hybrid", action="store_true", help="Disable hybrid retrieval")
    parser.add_argument("--no-reranker", action="store_true", help="Disable reranker")
    args = parser.parse_args()

    validate_config()

    output = run_ragas_evaluation(
        dataset_path=args.dataset,
        threshold=args.threshold,
        use_hybrid=not args.no_hybrid,
        use_reranker=not args.no_reranker,
    )

    if "error" in output:
        print(f"❌ Evaluation failed: {output['error']}")
        sys.exit(1)

    if not output["summary"]["passed"]:
        print("❌ Build failed: quality below threshold!")
        sys.exit(1)

    print("✅ All quality checks passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
