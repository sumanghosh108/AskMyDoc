# Getting Started Guide
## Production-Grade RAG System - Step-by-Step Setup

This guide will walk you through setting up and running the RAG system from scratch.

---

## Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)
- 2GB+ free disk space
- Internet connection (for downloading models)

---

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Windows (CMD):
.venv\Scripts\activate.bat

# On Linux/Mac:
source .venv/bin/activate
```

### 1.2 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CPU version for Windows)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install all other dependencies
pip install -r requirements.txt
```

**Note**: The installation may take 5-10 minutes depending on your internet speed.

---

## Step 2: Configuration

### 2.1 Create Environment File

Copy the example environment file:

```bash
# On Windows:
copy .env.example .env

# On Linux/Mac:
cp .env.example .env
```

### 2.2 Configure API Keys

Edit the `.env` file and add your API keys:

```env
# Required: OpenRouter API key for LLM
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: For embeddings (defaults to sentence-transformers if not set)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For reranking (defaults to cross-encoder if not set)
COHERE_API_KEY=your_cohere_api_key_here

# Cache settings (optional)
CACHE_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Getting API Keys:**
- OpenRouter: https://openrouter.ai/ (required for answer generation)
- OpenAI: https://platform.openai.com/ (optional, for embeddings)
- Cohere: https://cohere.com/ (optional, for reranking)

---

## Step 3: Ingest Documents

### 3.1 Prepare Your Documents

Place your documents in a folder. Supported formats:
- PDF files (`.pdf`)
- Markdown files (`.md`)
- Web pages (URLs)

The system comes with sample documents in `./sample_docs/`.

### 3.2 Ingest Documents

```bash
# Ingest from a directory
python main.py ingest --source ./sample_docs/

# Ingest a single file
python main.py ingest --source ./path/to/document.pdf

# Ingest from a URL
python main.py ingest --source https://example.com/page

# Ingest multiple sources
python main.py ingest --source ./docs/ ./file.pdf https://example.com
```

**Expected Output:**
```
INFO: Ingestion complete, chunks=4, source=./sample_docs/
```

### 3.3 Verify Ingestion

```bash
python main.py status
```

**Expected Output:**
```
INFO: ChromaDB Status, collection=rag_documents, documents_count=4
```

---

## Step 4: Query the System

### 4.1 Basic Query

```bash
python main.py query "What is machine learning?"
```

**Expected Output:**
```
============================================================
ANSWER
============================================================
Machine learning is a subset of artificial intelligence...

------------------------------------------------------------
SOURCES
------------------------------------------------------------
  1. ./sample_docs/machine_learning_intro.md (Page 1) [score: 0.856]
```

### 4.2 Advanced Query with All Features

```bash
python main.py query "What are the differences between supervised and unsupervised learning?" --query-rewriting --multi-hop --cache --verbose
```

**Features:**
- `--query-rewriting`: Generates multiple query variations for better recall
- `--multi-hop`: Enables multi-step reasoning for complex questions
- `--cache`: Enables caching (requires Redis)
- `--verbose`: Shows detailed timing and metadata

### 4.3 Query Options

```bash
# Customize retrieval
python main.py query "Your question" --top-k 10

# Disable hybrid retrieval (vector only)
python main.py query "Your question" --no-hybrid

# Disable reranking
python main.py query "Your question" --no-reranker

# JSON output
python main.py query "Your question" --json
```

---

## Step 5: Run the API Server (Optional)

### 5.1 Start the Server

```bash
python main.py serve
```

**Expected Output:**
```
INFO: Starting FastAPI server, host=0.0.0.0, port=8000
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 5.2 Test the API

Open your browser and navigate to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 5.3 Query via API

```bash
# Using curl (Windows PowerShell)
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"What is machine learning?\", \"top_k\": 5}'

# Using Python
import requests
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is machine learning?", "top_k": 5}
)
print(response.json())
```

---

## Step 6: Enable Caching (Optional)

### 6.1 Install Redis

**Windows:**
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Install and start Redis server

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

### 6.2 Install Redis Python Client

```bash
pip install redis
```

### 6.3 Enable Cache in .env

```env
CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 6.4 Test Cache

```bash
# Check cache stats
python main.py cache stats

# Clear cache
python main.py cache clear
```

---

## Step 7: Run Evaluation (Optional)

### 7.1 Prepare Golden Dataset

Create a file `eval/golden_dataset.json`:

```json
{
  "questions": [
    {
      "question": "What is machine learning?",
      "expected_answer": "Machine learning is a subset of AI...",
      "ground_truth_context": ["Machine learning enables computers to learn..."]
    }
  ]
}
```

### 7.2 Run Evaluation

```bash
# Basic evaluation
python main.py eval --dataset eval/golden_dataset.json

# RAGAS evaluation (more comprehensive)
python main.py eval --ragas --dataset eval/golden_dataset.json
```

---

## Common Commands Reference

### Document Management
```bash
# Ingest documents
python main.py ingest --source ./docs/

# Check vector store status
python main.py status
```

### Querying
```bash
# Basic query
python main.py query "Your question"

# Advanced query with all features
python main.py query "Your question" --query-rewriting --multi-hop --cache --verbose

# Custom retrieval settings
python main.py query "Your question" --top-k 10 --no-hybrid --no-reranker
```

### API Server
```bash
# Start server
python main.py serve

# Start on custom port
python main.py serve --port 8080
```

### Cache Management
```bash
# View cache statistics
python main.py cache stats

# Clear all cache
python main.py cache clear
```

### Evaluation
```bash
# Run evaluation
python main.py eval --dataset eval/golden_dataset.json

# Run RAGAS evaluation
python main.py eval --ragas --threshold 0.85
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "PyTorch DLL load failed"
**Solution:** Reinstall PyTorch CPU version:
```bash
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "OpenRouter API key not found"
**Solution:** Set your API key in `.env`:
```env
OPENROUTER_API_KEY=your_key_here
```

### Issue: "Redis connection failed"
**Solution:** Either install Redis or disable caching:
```env
CACHE_ENABLED=false
```

### Issue: Slow query performance
**Solution:** 
- First query is always slower (model loading)
- Use `--no-reranker` to skip reranking
- Use `--no-hybrid` for faster vector-only search
- Reduce `--top-k` value

---

## Performance Tips

1. **First Query is Slow**: Models are loaded on first use (~10-20s). Subsequent queries are faster.

2. **Enable Caching**: Install Redis and enable caching to avoid redundant API calls.

3. **Optimize Retrieval**: 
   - Use `--top-k 5` instead of default 10 for faster retrieval
   - Disable reranking with `--no-reranker` if speed is critical

4. **Query Rewriting**: Only use `--query-rewriting` for complex queries (adds ~5-10s).

5. **Multi-Hop**: Only use `--multi-hop` for questions requiring multiple reasoning steps (adds ~15-20s).

---

## Next Steps

1. **Ingest Your Documents**: Replace sample docs with your own documents
2. **Customize Prompts**: Edit `config/prompts_v1.yaml` to customize system behavior
3. **Tune Parameters**: Adjust chunk size, top-k, and other settings in `src/core/config.py`
4. **Create Golden Dataset**: Build evaluation dataset for your domain
5. **Deploy API**: Use the FastAPI server for production deployment

---

## Additional Resources

- **Full Documentation**: See `README.md`
- **Usage Guide**: See `USAGE_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`
- **Verification Checklist**: See `VERIFICATION_CHECKLIST.md`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the documentation files
3. Check the logs in `./logs/` directory
4. Verify your `.env` configuration

---

**You're all set! Start by ingesting documents and asking questions.**
