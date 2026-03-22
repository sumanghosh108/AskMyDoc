"""
Central configuration for the Ask My Doc RAG application.
Loads environment variables and exposes settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
# config.py is now in src/core/, so root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# --- Retrieval ---
TOP_K = int(os.getenv("TOP_K", "5"))
TOP_K_INITIAL = int(os.getenv("TOP_K_INITIAL", "20"))  # Before reranking

# --- ChromaDB ---
# Local dev: "chroma_db" | Render with mounted disk: "/data/chroma_db"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "chroma_db"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "ask_my_doc")

# --- Models ---
# Using local sentence-transformers for embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
# Using Groq for the LLM (free tier)
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# --- Prompts ---
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
PROMPTS_DIR = PROJECT_ROOT / "config"

# --- Reranker ---
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# --- Evaluation ---
EVAL_THRESHOLD = float(os.getenv("EVAL_THRESHOLD", "0.7"))
GOLDEN_DATASET_PATH = os.getenv("GOLDEN_DATASET_PATH", str(PROJECT_ROOT / "eval" / "golden_dataset.json"))

# --- Caching ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_TTL = int(os.getenv("REDIS_TTL", "3600"))  # 1 hour
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"

# --- Context Building ---
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "4000"))

# --- Multi-hop ---
MAX_HOPS = int(os.getenv("MAX_HOPS", "3"))

# --- Query Rewriting ---
QUERY_REWRITING_ENABLED = os.getenv("QUERY_REWRITING_ENABLED", "false").lower() == "true"
MULTI_HOP_ENABLED = os.getenv("MULTI_HOP_ENABLED", "false").lower() == "true"


def get_prompt_config_path() -> Path:
    """Return the path to the active prompt config file."""
    return PROMPTS_DIR / f"prompts_{PROMPT_VERSION}.yaml"


def validate_config():
    """Validate that required configuration is set."""
    errors = []
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is not set. Add it to your .env file.")
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL is not set. Add it to your .env file.")
    if not SUPABASE_SERVICE_ROLE_KEY:
        errors.append("SUPABASE_SERVICE_ROLE_KEY is not set. Add it to your .env file.")
    if errors:
        raise EnvironmentError("\n".join(errors))
