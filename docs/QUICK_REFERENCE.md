# Quick Reference Card

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY
```

## Common Commands

### Ingest Documents

```bash
python main.py ingest --source ./docs/
```

### Query (Basic)

```bash
python main.py query "What is machine learning?"
```

### Query (All Features)

```bash
python main.py query "What is ML?" \
  --query-rewriting \
  --multi-hop \
  --cache \
  --verbose
```

### Start API Server

```bash
python main.py serve
```

### Run Evaluation

```bash
python main.py eval --ragas
```

### Cache Management

```bash
python main.py cache stats
python main.py cache clear
```

## API Endpoints

```bash
# Query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ML?", "use_hybrid": true}'

# Cache stats
curl "http://localhost:8000/api/v1/cache/stats"

# Metrics
curl "http://localhost:8000/api/v1/metrics"
```

## Configuration (.env)

```bash
# Required
OPENROUTER_API_KEY=your_key

# Optional - Advanced Features
CACHE_ENABLED=true
QUERY_REWRITING_ENABLED=true
MULTI_HOP_ENABLED=true
MAX_CONTEXT_TOKENS=4000
```

## Feature Flags

| Feature | CLI Flag | Config Variable | Default |
|---------|----------|----------------|---------|
| Hybrid Retrieval | `--no-hybrid` (disable) | - | Enabled |
| Reranking | `--no-reranker` (disable) | - | Enabled |
| Query Rewriting | `--query-rewriting` | `QUERY_REWRITING_ENABLED` | Disabled |
| Multi-Hop | `--multi-hop` | `MULTI_HOP_ENABLED` | Disabled |
| Caching | `--cache` | `CACHE_ENABLED` | Disabled |

## Performance Tips

1. **Enable caching** for production: `CACHE_ENABLED=true`
2. **Reduce TOP_K** for faster responses: `TOP_K=3`
3. **Disable query rewriting** for simple queries
4. **Enable multi-hop** only for complex questions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Redis connection failed | Start Redis: `docker run -d -p 6379:6379 redis` |
| Out of memory | Reduce `TOP_K` and `MAX_CONTEXT_TOKENS` |
| Slow performance | Enable caching, reduce `TOP_K_INITIAL` |
| API key error | Set `OPENROUTER_API_KEY` in `.env` |

## File Locations

- **Config**: `.env`, `config/prompts_v1.yaml`
- **Logs**: `logs/`
- **Vector DB**: `chroma_db/`
- **Evaluation**: `eval/golden_dataset.json`
- **Results**: `eval/results/`

## Documentation

- **README.md** - Complete system documentation
- **USAGE_GUIDE.md** - Detailed usage guide
- **IMPLEMENTATION_SUMMARY.md** - What was implemented
- **QUICK_REFERENCE.md** - This file

## Support

1. Check logs in `logs/`
2. Review documentation
3. Check API docs at `http://localhost:8000/docs`
