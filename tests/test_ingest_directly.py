import sys
sys.path.insert(0, '.')

from src.indexing.ingest import ingest_documents

try:
    result = ingest_documents('test_upload.txt')
    print(f"Success! Ingested {result} chunks")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
