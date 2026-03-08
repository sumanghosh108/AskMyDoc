"""
Test database connection and initialization
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("PostgreSQL Database Connection Test")
print("=" * 60)

# Display configuration (without password)
print("\n📋 Configuration:")
print(f"   Host: {os.getenv('POSTGRES_HOST', 'localhost')}")
print(f"   Port: {os.getenv('POSTGRES_PORT', '5432')}")
print(f"   User: {os.getenv('POSTGRES_USER', 'postgres')}")
print(f"   Database: {os.getenv('POSTGRES_DB', 'AskMyDocLOG')}")
print(f"   Password: {'***' if os.getenv('POSTGRES_PASSWORD') else '(not set)'}")

# Test 1: Import modules
print("\n🔧 Test 1: Importing modules...")
try:
    from database.db_initializer import initialize_database, verify_database_setup, get_database_stats
    print("   ✅ Modules imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import modules: {e}")
    sys.exit(1)

# Test 2: Initialize database
print("\n🔧 Test 2: Initializing database...")
try:
    result = initialize_database()
    
    if result['success']:
        print("   ✅ Database initialized successfully")
        print(f"      Database created: {result.get('database_created', False)}")
        print(f"      Tables created: {result.get('tables_created', False)}")
        
        verification = result.get('verification', {})
        print(f"      Tables: {len(verification.get('tables', []))}")
        print(f"      Views: {len(verification.get('views', []))}")
        print(f"      Functions: {len(verification.get('functions', []))}")
    else:
        print(f"   ❌ Database initialization failed: {result.get('error')}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error during initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verify database setup
print("\n🔧 Test 3: Verifying database setup...")
try:
    verification = verify_database_setup(os.getenv('POSTGRES_DB', 'AskMyDocLOG'))
    
    if verification.get('status') == 'healthy':
        print("   ✅ Database is healthy")
        print(f"      Tables found: {len(verification.get('tables', []))}")
        
        # List tables
        tables = verification.get('tables', [])
        if tables:
            print("\n   📊 Tables:")
            for table in sorted(tables):
                print(f"      - {table}")
    else:
        print(f"   ⚠️  Database status: {verification.get('status')}")
        print(f"      Error: {verification.get('error')}")
        
except Exception as e:
    print(f"   ❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Get database statistics
print("\n🔧 Test 4: Getting database statistics...")
try:
    stats = get_database_stats()
    
    if 'error' not in stats:
        print("   ✅ Statistics retrieved successfully")
        print(f"      Query logs: {stats.get('query_logs_count', 0)}")
        print(f"      Error logs: {stats.get('error_logs_count', 0)}")
        print(f"      Evaluation metrics: {stats.get('evaluation_metrics_count', 0)}")
        print(f"      Queries (24h): {stats.get('queries_last_24h', 0)}")
        print(f"      Avg latency (24h): {stats.get('avg_latency_24h', 0):.2f}ms")
        print(f"      Database size: {stats.get('database_size', 'N/A')}")
    else:
        print(f"   ⚠️  Error getting stats: {stats.get('error')}")
        
except Exception as e:
    print(f"   ❌ Error getting statistics: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test query logger
print("\n🔧 Test 5: Testing query logger...")
try:
    from database.query_logger import get_query_logger
    
    query_logger = get_query_logger()
    
    # Log a test query
    query_id = query_logger.log_query(
        query_text="Test query: What is machine learning?",
        total_latency=1500.0,
        retrieval_latency=400.0,
        rerank_latency=200.0,
        llm_latency=900.0,
        retrieved_chunks=10,
        reranked_chunks=5,
        model_used="test-model",
        query_rewriting_enabled=True,
        multi_hop_enabled=False,
        cache_hit=False,
        answer_length=250,
        source_count=3
    )
    
    if query_id:
        print(f"   ✅ Query logged successfully (ID: {query_id})")
    else:
        print("   ⚠️  Query logging returned None")
        
except Exception as e:
    print(f"   ❌ Error testing query logger: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test error logger
print("\n🔧 Test 6: Testing error logger...")
try:
    from database.error_logger import get_error_logger
    
    error_logger = get_error_logger()
    
    # Log a test error
    error_id = error_logger.log_error(
        pipeline_stage="test",
        error_message="Test error message",
        query_text="Test query",
        error_type="TestError",
        severity="INFO"
    )
    
    if error_id:
        print(f"   ✅ Error logged successfully (ID: {error_id})")
    else:
        print("   ⚠️  Error logging returned None")
        
except Exception as e:
    print(f"   ❌ Error testing error logger: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Database test completed successfully!")
print("=" * 60)
