"""
Central configuration for the Ask My Doc RAG application.
Loads environment variables and exposes settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# --- Retrieval ---
TOP_K = int(os.getenv("TOP_K", "5"))
TOP_K_INITIAL = int(os.getenv("TOP_K_INITIAL", "20"))  # Before reranking

# --- ChromaDB ---
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "chroma_db"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "ask_my_doc")

# --- Models ---
# Using local sentence-transformers for embeddings to avoid API limitations/errors
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
# Using OpenRouter for the LLM
LLM_MODEL = os.getenv("LLM_MODEL", "stepfun/step-3.5-flash")

# --- Prompts ---
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
PROMPTS_DIR = PROJECT_ROOT / "config"

# --- Reranker ---
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# --- Evaluation ---
EVAL_THRESHOLD = float(os.getenv("EVAL_THRESHOLD", "0.7"))
GOLDEN_DATASET_PATH = os.getenv("GOLDEN_DATASET_PATH", str(PROJECT_ROOT / "eval" / "golden_dataset.json"))


def get_prompt_config_path() -> Path:
    """Return the path to the active prompt config file."""
    return PROMPTS_DIR / f"prompts_{PROMPT_VERSION}.yaml"


def validate_config():
    """Validate that required configuration is set."""
    errors = []
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is not set. Add it to your .env file.")
    if errors:
        raise EnvironmentError("\n".join(errors))
