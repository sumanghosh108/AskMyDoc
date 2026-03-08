# API Guide - Step-by-Step
## Running the RAG System Through REST API

This guide shows you how to run and interact with the RAG system using the FastAPI REST API.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Starting the API Server](#starting-the-api-server)
3. [API Endpoints](#api-endpoints)
4. [Testing with Different Tools](#testing-with-different-tools)
5. [Advanced Usage](#advanced-usage)
6. [Error Handling](#error-handling)
7. [Production Deployment](#production-deployment)

---

## Quick Start

### Step 1: Setup (One-Time)

```bash
# Activate virtual environment
.venv\Scripts\activate

# Ensure dependencies are installed
pip install -r requirements.txt

# Configure API key in .env
OPENROUTER_API_KEY=your_key_here
```

### Step 2: Ingest Documents

```bash
# Ingest sample documents
python main.py ingest --source ./sample_docs/
```

### Step 3: Start API Server

```bash
# Start on default port 8000
python main.py serve

# Or specify custom host/port
python main.py serve --host 0.0.0.0 --port 8080
```

### Step 4: Test the API

Open your browser: http://localhost:8000/docs

---

## Starting the API Server

### Basic Server Start

```bash
python main.py serve
```

**Expected Output:**
```
INFO: Starting FastAPI server, host=0.0.0.0, port=8000
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO: Started reloader process
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
```

### Custom Configuration

```bash
# Custom port
python main.py serve --port 8080

# Custom host (localhost only)
python main.py serve --host 127.0.0.1 --port 8000

# Production settings
python main.py serve --host 0.0.0.0 --port 80
```

### Verify Server is Running

Open browser to: http://localhost:8000/health

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Check if the API is running

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 2. Query Endpoint (Basic)

**Endpoint:** `POST /query`

**Purpose:** Ask questions and get answers with sources

**Request Body:**
```json
{
  "question": "What is machine learning?",
  "top_k": 5,
  "use_hybrid": true,
  "use_reranker": true
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is machine learning?\", \"top_k\": 5}"
```

**Example (PowerShell):**
```powershell
$body = @{
    question = "What is machine learning?"
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed...",
  "sources": [
    {
      "source": "./sample_docs/machine_learning_intro.md",
      "page": 1,
      "content": "Machine learning is...",
      "reranker_score": 0.856
    }
  ],
  "metadata": {
    "retrieval_method": "hybrid",
    "reranker_used": true,
    "chunks_retrieved": 5,
    "chunks_after_rerank": 3
  }
}
```

---

### 3. Query Endpoint (Advanced)

**Endpoint:** `POST /query/advanced`

**Purpose:** Query with advanced features (query rewriting, multi-hop, caching)

**Request Body:**
```json
{
  "question": "What are the differences between supervised and unsupervised learning?",
  "top_k": 10,
  "use_hybrid": true,
  "use_reranker": true,
  "use_query_rewriting": true,
  "use_multi_hop": true,
  "use_cache": true
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/query/advanced" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What are the differences between supervised and unsupervised learning?\", \"use_query_rewriting\": true, \"use_multi_hop\": true}"
```

**Example (PowerShell):**
```powershell
$body = @{
    question = "What are the differences between supervised and unsupervised learning?"
    top_k = 10
    use_query_rewriting = $true
    use_multi_hop = $true
    use_cache = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query/advanced" -Method Post -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "question": "What are the differences between supervised and unsupervised learning?",
  "answer": "The key differences are: 1) Supervised learning uses labeled data...",
  "sources": [...],
  "metadata": {
    "timings": {
      "total_time_ms": 45230,
      "components": {
        "query_rewriting": {"total_ms": 6500},
        "retrieval": {"total_ms": 15200},
        "multi_hop_analysis": {"total_ms": 18000},
        "reranking": {"total_ms": 5100},
        "context_building": {"total_ms": 220},
        "llm_generation": {"total_ms": 13800}
      }
    },
    "features_used": {
      "query_rewriting": true,
      "multi_hop": true,
      "reranking": true,
      "cache": true
    },
    "context_stats": {
      "original_count": 20,
      "final_count": 5,
      "tokens_used": 850,
      "token_limit": 4000
    }
  }
}
```

---

### 4. Cache Statistics

**Endpoint:** `GET /cache/stats`

**Purpose:** Get cache performance metrics

**Example:**
```bash
curl http://localhost:8000/cache/stats
```

**Response:**
```json
{
  "enabled": true,
  "connected": true,
  "total_rag_keys": 15,
  "keyspace_hits": 42,
  "keyspace_misses": 8,
  "hit_rate": 0.84
}
```

---

### 5. Clear Cache

**Endpoint:** `POST /cache/clear`

**Purpose:** Clear all cached data

**Example:**
```bash
curl -X POST http://localhost:8000/cache/clear
```

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

---

### 6. System Metrics

**Endpoint:** `GET /metrics`

**Purpose:** Get system performance metrics

**Example:**
```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "total_queries": 127,
  "avg_latency_ms": 3450,
  "cache_hit_rate": 0.68,
  "vector_store_docs": 42
}
```

---

## Testing with Different Tools

### 1. Using cURL (Command Line)

**Windows (PowerShell):**
```powershell
# Basic query
curl.exe -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{\"question\": \"What is machine learning?\"}'

# Advanced query
curl.exe -X POST "http://localhost:8000/query/advanced" -H "Content-Type: application/json" -d '{\"question\": \"Explain NLP\", \"use_query_rewriting\": true, \"use_multi_hop\": true}'
```

**Linux/Mac:**
```bash
# Basic query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'

# Advanced query
curl -X POST "http://localhost:8000/query/advanced" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain NLP", "use_query_rewriting": true, "use_multi_hop": true}'
```

---

### 2. Using PowerShell (Invoke-RestMethod)

```powershell
# Basic query
$response = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body (@{
    question = "What is machine learning?"
    top_k = 5
} | ConvertTo-Json) -ContentType "application/json"

# Display answer
Write-Host $response.answer

# Display sources
$response.sources | ForEach-Object {
    Write-Host "Source: $($_.source) - Score: $($_.reranker_score)"
}

# Advanced query with all features
$response = Invoke-RestMethod -Uri "http://localhost:8000/query/advanced" -Method Post -Body (@{
    question = "What are the differences between supervised and unsupervised learning?"
    use_query_rewriting = $true
    use_multi_hop = $true
    use_cache = $true
    top_k = 10
} | ConvertTo-Json) -ContentType "application/json"

# Display metadata
Write-Host "Total time: $($response.metadata.timings.total_time_ms)ms"
Write-Host "Features used:"
$response.metadata.features_used | Format-List
```

---

### 3. Using Python (requests)

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{BASE_URL}/health")
print(f"Health: {response.json()}")

# 2. Basic query
query_data = {
    "question": "What is machine learning?",
    "top_k": 5,
    "use_hybrid": True,
    "use_reranker": True
}

response = requests.post(f"{BASE_URL}/query", json=query_data)
result = response.json()

print(f"\nQuestion: {result['question']}")
print(f"\nAnswer: {result['answer']}")
print(f"\nSources:")
for i, source in enumerate(result['sources'], 1):
    print(f"  {i}. {source['source']} (score: {source.get('reranker_score', 'N/A')})")

# 3. Advanced query with all features
advanced_query = {
    "question": "What are the differences between supervised and unsupervised learning?",
    "top_k": 10,
    "use_query_rewriting": True,
    "use_multi_hop": True,
    "use_cache": True
}

response = requests.post(f"{BASE_URL}/query/advanced", json=advanced_query)
result = response.json()

print(f"\n\nAdvanced Query Results:")
print(f"Answer: {result['answer']}")
print(f"\nMetadata:")
print(f"  Total time: {result['metadata']['timings']['total_time_ms']}ms")
print(f"  Features used: {result['metadata']['features_used']}")
print(f"  Context stats: {result['metadata']['context_stats']}")

# 4. Cache statistics
response = requests.get(f"{BASE_URL}/cache/stats")
cache_stats = response.json()
print(f"\n\nCache Statistics:")
print(f"  Enabled: {cache_stats['enabled']}")
print(f"  Hit rate: {cache_stats.get('hit_rate', 0):.2%}")

# 5. Clear cache
response = requests.post(f"{BASE_URL}/cache/clear")
print(f"\n\nCache cleared: {response.json()}")
```

**Save as `test_api.py` and run:**
```bash
python test_api.py
```

---

### 4. Using JavaScript (fetch)

```javascript
// Base URL
const BASE_URL = "http://localhost:8000";

// 1. Health check
async function checkHealth() {
    const response = await fetch(`${BASE_URL}/health`);
    const data = await response.json();
    console.log("Health:", data);
}

// 2. Basic query
async function basicQuery() {
    const response = await fetch(`${BASE_URL}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: "What is machine learning?",
            top_k: 5,
            use_hybrid: true,
            use_reranker: true
        })
    });
    
    const result = await response.json();
    console.log("\nQuestion:", result.question);
    console.log("\nAnswer:", result.answer);
    console.log("\nSources:", result.sources);
}

// 3. Advanced query
async function advancedQuery() {
    const response = await fetch(`${BASE_URL}/query/advanced`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: "What are the differences between supervised and unsupervised learning?",
            top_k: 10,
            use_query_rewriting: true,
            use_multi_hop: true,
            use_cache: true
        })
    });
    
    const result = await response.json();
    console.log("\nAdvanced Query Results:");
    console.log("Answer:", result.answer);
    console.log("Metadata:", result.metadata);
}

// 4. Cache stats
async function getCacheStats() {
    const response = await fetch(`${BASE_URL}/cache/stats`);
    const data = await response.json();
    console.log("\nCache Statistics:", data);
}

// Run all tests
async function runTests() {
    await checkHealth();
    await basicQuery();
    await advancedQuery();
    await getCacheStats();
}

runTests();
```

**Save as `test_api.js` and run with Node.js:**
```bash
node test_api.js
```

---

### 5. Using Postman

**Step 1:** Import Collection

Create a new collection in Postman with these requests:

**Request 1: Health Check**
- Method: `GET`
- URL: `http://localhost:8000/health`

**Request 2: Basic Query**
- Method: `POST`
- URL: `http://localhost:8000/query`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "question": "What is machine learning?",
  "top_k": 5
}
```

**Request 3: Advanced Query**
- Method: `POST`
- URL: `http://localhost:8000/query/advanced`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "question": "What are the differences between supervised and unsupervised learning?",
  "use_query_rewriting": true,
  "use_multi_hop": true,
  "use_cache": true
}
```

**Request 4: Cache Stats**
- Method: `GET`
- URL: `http://localhost:8000/cache/stats`

**Request 5: Clear Cache**
- Method: `POST`
- URL: `http://localhost:8000/cache/clear`

---

### 6. Using Swagger UI (Interactive)

**Step 1:** Start the server
```bash
python main.py serve
```

**Step 2:** Open browser to http://localhost:8000/docs

**Step 3:** Try the endpoints interactively:
1. Click on any endpoint (e.g., `POST /query`)
2. Click "Try it out"
3. Fill in the request body
4. Click "Execute"
5. View the response

---

## Advanced Usage

### Batch Queries

```python
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000"

questions = [
    "What is machine learning?",
    "Explain supervised learning",
    "What is NLP?",
    "Describe neural networks"
]

def query_api(question):
    response = requests.post(
        f"{BASE_URL}/query",
        json={"question": question, "top_k": 5}
    )
    return response.json()

# Execute queries in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(query_api, questions))

for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['question']}")
    print(f"   Answer: {result['answer'][:100]}...")
```

---

### Streaming Responses (Future Enhancement)

```python
# Note: Streaming not yet implemented, but here's the pattern
import requests

response = requests.post(
    f"{BASE_URL}/query/stream",
    json={"question": "What is machine learning?"},
    stream=True
)

for chunk in response.iter_content(chunk_size=None):
    if chunk:
        print(chunk.decode('utf-8'), end='', flush=True)
```

---

### Custom Headers and Authentication (Future Enhancement)

```python
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here",
    "X-User-ID": "user123"
}

response = requests.post(
    f"{BASE_URL}/query",
    json={"question": "What is machine learning?"},
    headers=headers
)
```

---

## Error Handling

### Common Errors and Solutions

**1. Connection Refused**
```json
{
  "error": "Connection refused"
}
```
**Solution:** Make sure the server is running (`python main.py serve`)

---

**2. Invalid Request Body**
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution:** Ensure all required fields are present in the request body

---

**3. API Key Not Configured**
```json
{
  "error": "OpenRouter API key not configured"
}
```
**Solution:** Set `OPENROUTER_API_KEY` in your `.env` file

---

**4. No Documents Ingested**
```json
{
  "error": "No documents found in vector store"
}
```
**Solution:** Ingest documents first: `python main.py ingest --source ./sample_docs/`

---

**5. Timeout Error**
```json
{
  "error": "Request timeout"
}
```
**Solution:** 
- Reduce `top_k` value
- Disable `use_query_rewriting` or `use_multi_hop`
- Check your internet connection (for LLM API calls)

---

### Error Handling in Code

```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/query",
        json={"question": "What is machine learning?"},
        timeout=60  # 60 second timeout
    )
    response.raise_for_status()  # Raise exception for 4xx/5xx status codes
    
    result = response.json()
    print(result['answer'])
    
except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to API server. Is it running?")
except requests.exceptions.Timeout:
    print("Error: Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Production Deployment

### 1. Using Gunicorn (Linux/Mac)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn src.api.router:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

---

### 2. Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
# Build image
docker build -t rag-api .

# Run container
docker run -p 8000:8000 --env-file .env rag-api
```

---

### 3. Environment Variables for Production

```env
# API Configuration
OPENROUTER_API_KEY=your_production_key
OPENAI_API_KEY=your_openai_key
COHERE_API_KEY=your_cohere_key

# Cache Configuration
CACHE_ENABLED=true
REDIS_HOST=redis.production.com
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Performance Tuning
MAX_WORKERS=4
TIMEOUT=120
LOG_LEVEL=INFO
```

---

### 4. Monitoring and Logging

```python
# Add to your API client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_with_logging(question):
    logger.info(f"Querying: {question}")
    
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json={"question": question}
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response time: {response.elapsed.total_seconds()}s")
        
        return response.json()
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
```

---

## Complete Example: Building a Chat Interface

```python
import requests
import sys

BASE_URL = "http://localhost:8000"

def chat():
    print("RAG System Chat Interface")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        try:
            print("Thinking...", end='', flush=True)
            
            response = requests.post(
                f"{BASE_URL}/query/advanced",
                json={
                    "question": question,
                    "use_query_rewriting": True,
                    "use_multi_hop": True,
                    "use_cache": True
                },
                timeout=120
            )
            
            result = response.json()
            
            print("\r" + " " * 20 + "\r", end='')  # Clear "Thinking..."
            print(f"Assistant: {result['answer']}\n")
            
            if result.get('sources'):
                print("Sources:")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"  {i}. {source['source']}")
                print()
            
        except requests.exceptions.Timeout:
            print("\nError: Request timed out. Try a simpler question.")
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            chat()
        else:
            print("Error: API server is not healthy")
    except:
        print("Error: Cannot connect to API server.")
        print("Please start the server with: python main.py serve")
```

**Save as `chat.py` and run:**
```bash
python chat.py
```

---

## Summary

You now have everything you need to interact with the RAG system through the API:

1. ✅ Start the server: `python main.py serve`
2. ✅ Test with browser: http://localhost:8000/docs
3. ✅ Query with curl, Python, JavaScript, or Postman
4. ✅ Use advanced features: query rewriting, multi-hop, caching
5. ✅ Monitor performance with metrics endpoints
6. ✅ Handle errors gracefully
7. ✅ Deploy to production

**Next Steps:**
- Build a web frontend (React, Vue, etc.)
- Add authentication and rate limiting
- Implement streaming responses
- Add monitoring and alerting
- Scale with load balancers

Happy coding! 🚀
