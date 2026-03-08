"""
Debug script to test PDF ingestion directly
"""
import sys
import traceback

# Test if we can import and use the ingest function
try:
    from src.indexing.ingest import ingest_documents
    
    # Try to ingest a PDF
    pdf_file = "report.pdf"  # Replace with your actual PDF filename
    
    print(f"Attempting to ingest: {pdf_file}")
    print("This will show the full error if it fails...")
    
    result = ingest_documents(pdf_file)
    print(f"\nSuccess! Ingested {result} chunks")
    
except Exception as e:
    print(f"\nError occurred: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
