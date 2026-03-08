"""
Quick API Test Script
Run this after starting the server with: python main.py serve
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        result = response.json()
        print(f"✅ Server is healthy")
        print(f"   Status: {result['status']}")
        print(f"   Version: {result.get('version', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Server is not running or not responding")
        print(f"   Error: {e}")
        print(f"\n   Please start the server with: python main.py serve")
        return False

def test_basic_query():
    """Test 2: Basic Query"""
    print_section("TEST 2: Basic Query")
    
    query_data = {
        "question": "What is machine learning?",
        "top_k": 5,
        "use_hybrid": True,
        "use_reranker": True
    }
    
    print(f"Question: {query_data['question']}")
    print(f"Sending request...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json=query_data,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        result = response.json()
        
        print(f"\n✅ Query successful (took {elapsed:.2f}s)")
        print(f"\nAnswer:")
        print(f"   {result['answer'][:200]}...")
        
        if result.get('sources'):
            print(f"\nSources ({len(result['sources'])} found):")
            for i, source in enumerate(result['sources'][:3], 1):
                score = source.get('reranker_score', 'N/A')
                print(f"   {i}. {source['source']} (score: {score})")
        
        if result.get('metadata'):
            print(f"\nMetadata:")
            print(f"   Retrieval method: {result['metadata'].get('retrieval_method', 'N/A')}")
            print(f"   Reranker used: {result['metadata'].get('reranker_used', 'N/A')}")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def test_advanced_query():
    """Test 3: Advanced Query with All Features"""
    print_section("TEST 3: Advanced Query (All Features)")
    
    query_data = {
        "question": "What are the differences between supervised and unsupervised learning?",
        "top_k": 10,
        "use_hybrid": True,
        "use_reranker": True,
        "use_query_rewriting": True,
        "use_multi_hop": True,
        "use_cache": True
    }
    
    print(f"Question: {query_data['question']}")
    print(f"Features enabled:")
    print(f"   - Query Rewriting: ✅")
    print(f"   - Multi-Hop: ✅")
    print(f"   - Caching: ✅")
    print(f"   - Reranking: ✅")
    print(f"\nSending request (this may take 30-60 seconds)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/query/advanced",
            json=query_data,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        result = response.json()
        
        print(f"\n✅ Advanced query successful (took {elapsed:.2f}s)")
        print(f"\nAnswer:")
        print(f"   {result['answer'][:300]}...")
        
        if result.get('metadata'):
            metadata = result['metadata']
            
            # Timings
            if 'timings' in metadata:
                timings = metadata['timings']
                print(f"\nTiming Breakdown:")
                print(f"   Total time: {timings.get('total_time_ms', 0):.0f}ms")
                
                if 'components' in timings:
                    print(f"   Components:")
                    for comp, stats in timings['components'].items():
                        print(f"      - {comp}: {stats.get('total_ms', 0):.0f}ms")
            
            # Features used
            if 'features_used' in metadata:
                features = metadata['features_used']
                print(f"\nFeatures Used:")
                for feature, enabled in features.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {feature}")
            
            # Context stats
            if 'context_stats' in metadata:
                stats = metadata['context_stats']
                print(f"\nContext Statistics:")
                print(f"   Original chunks: {stats.get('original_count', 0)}")
                print(f"   Final chunks: {stats.get('final_count', 0)}")
                print(f"   Tokens used: {stats.get('tokens_used', 0)}/{stats.get('token_limit', 0)}")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ Advanced query failed: {e}")
        return False

def test_cache_stats():
    """Test 4: Cache Statistics"""
    print_section("TEST 4: Cache Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/cache/stats", timeout=5)
        result = response.json()
        
        print(f"✅ Cache stats retrieved")
        print(f"\nCache Status:")
        print(f"   Enabled: {result.get('enabled', False)}")
        print(f"   Connected: {result.get('connected', False)}")
        
        if result.get('connected'):
            print(f"\nCache Metrics:")
            print(f"   Total keys: {result.get('total_rag_keys', 0)}")
            print(f"   Hits: {result.get('keyspace_hits', 0)}")
            print(f"   Misses: {result.get('keyspace_misses', 0)}")
            print(f"   Hit rate: {result.get('hit_rate', 0):.2%}")
        else:
            print(f"\n⚠️  Cache is not connected (Redis not available)")
            print(f"   System will work without caching")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get cache stats: {e}")
        return False

def test_metrics():
    """Test 5: System Metrics"""
    print_section("TEST 5: System Metrics")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        result = response.json()
        
        print(f"✅ System metrics retrieved")
        print(f"\nMetrics:")
        for key, value in result.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Metrics endpoint not available: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  RAG System API Test Suite")
    print("=" * 60)
    print("\nThis script will test all API endpoints")
    print("Make sure the server is running: python main.py serve\n")
    
    input("Press Enter to start tests...")
    
    # Run tests
    results = []
    
    # Test 1: Health check (required)
    if not test_health():
        print("\n❌ Server is not running. Exiting.")
        return
    
    results.append(("Health Check", True))
    
    # Test 2: Basic query
    results.append(("Basic Query", test_basic_query()))
    
    # Test 3: Advanced query
    results.append(("Advanced Query", test_advanced_query()))
    
    # Test 4: Cache stats
    results.append(("Cache Stats", test_cache_stats()))
    
    # Test 5: Metrics
    results.append(("System Metrics", test_metrics()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed\n")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
