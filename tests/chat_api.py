"""
Simple Chat Interface Using the RAG API
Run this after starting the server with: python main.py serve
"""

import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def query_api(question, use_advanced=True):
    """Send a query to the API"""
    
    if use_advanced:
        endpoint = f"{BASE_URL}/query/advanced"
        data = {
            "question": question,
            "top_k": 10,
            "use_query_rewriting": True,
            "use_multi_hop": True,
            "use_cache": True
        }
    else:
        endpoint = f"{BASE_URL}/query"
        data = {
            "question": question,
            "top_k": 5
        }
    
    try:
        response = requests.post(endpoint, json=data, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try a simpler question or use basic mode."}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def print_header():
    """Print chat header"""
    print("\n" + "=" * 70)
    print("  RAG SYSTEM - CHAT INTERFACE")
    print("=" * 70)
    print("\nCommands:")
    print("  /help     - Show this help message")
    print("  /mode     - Toggle between basic and advanced mode")
    print("  /stats    - Show cache statistics")
    print("  /clear    - Clear the screen")
    print("  /quit     - Exit the chat")
    print("\nType your question and press Enter to get an answer.")
    print("=" * 70 + "\n")

def print_help():
    """Print help message"""
    print("\n" + "-" * 70)
    print("HELP")
    print("-" * 70)
    print("\nAvailable Commands:")
    print("  /help     - Show this help message")
    print("  /mode     - Toggle between basic and advanced mode")
    print("  /stats    - Show cache statistics")
    print("  /clear    - Clear the screen")
    print("  /quit     - Exit the chat")
    print("\nModes:")
    print("  Basic Mode    - Fast queries with standard retrieval")
    print("  Advanced Mode - Slower but more comprehensive (query rewriting, multi-hop)")
    print("\nTips:")
    print("  - Use basic mode for simple factual questions")
    print("  - Use advanced mode for complex questions requiring reasoning")
    print("  - First query is slower (model loading), subsequent queries are faster")
    print("-" * 70 + "\n")

def show_cache_stats():
    """Show cache statistics"""
    try:
        response = requests.get(f"{BASE_URL}/cache/stats", timeout=5)
        result = response.json()
        
        print("\n" + "-" * 70)
        print("CACHE STATISTICS")
        print("-" * 70)
        print(f"Enabled: {result.get('enabled', False)}")
        print(f"Connected: {result.get('connected', False)}")
        
        if result.get('connected'):
            print(f"Total keys: {result.get('total_rag_keys', 0)}")
            print(f"Hits: {result.get('keyspace_hits', 0)}")
            print(f"Misses: {result.get('keyspace_misses', 0)}")
            print(f"Hit rate: {result.get('hit_rate', 0):.2%}")
        else:
            print("Cache is not connected (Redis not available)")
        
        print("-" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Failed to get cache stats: {e}\n")

def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def format_answer(result, show_metadata=False):
    """Format and print the answer"""
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}\n")
        return
    
    # Print answer
    print(f"\n{'─' * 70}")
    print("ANSWER")
    print('─' * 70)
    print(result.get('answer', 'No answer generated'))
    
    # Print sources
    sources = result.get('sources', [])
    if sources:
        print(f"\n{'─' * 70}")
        print(f"SOURCES ({len(sources)} found)")
        print('─' * 70)
        for i, source in enumerate(sources[:5], 1):
            score = source.get('reranker_score')
            score_str = f" [score: {score:.3f}]" if score is not None else ""
            page = source.get('page')
            page_str = f" (Page {page})" if page else ""
            print(f"{i}. {source.get('source', 'Unknown')}{page_str}{score_str}")
    
    # Print metadata if requested
    if show_metadata and 'metadata' in result:
        metadata = result['metadata']
        
        print(f"\n{'─' * 70}")
        print("METADATA")
        print('─' * 70)
        
        # Timings
        if 'timings' in metadata:
            timings = metadata['timings']
            total_time = timings.get('total_time_ms', 0)
            print(f"Total time: {total_time:.0f}ms ({total_time/1000:.1f}s)")
            
            if 'components' in timings:
                print("\nComponent breakdown:")
                for comp, stats in timings['components'].items():
                    print(f"  - {comp}: {stats.get('total_ms', 0):.0f}ms")
        
        # Features used
        if 'features_used' in metadata:
            features = metadata['features_used']
            print("\nFeatures used:")
            for feature, enabled in features.items():
                status = "✅" if enabled else "❌"
                print(f"  {status} {feature}")
        
        # Context stats
        if 'context_stats' in metadata:
            stats = metadata['context_stats']
            print("\nContext statistics:")
            print(f"  Original chunks: {stats.get('original_count', 0)}")
            print(f"  Final chunks: {stats.get('final_count', 0)}")
            print(f"  Tokens: {stats.get('tokens_used', 0)}/{stats.get('token_limit', 0)}")
    
    print('─' * 70 + "\n")

def chat():
    """Main chat loop"""
    
    # Check if server is running
    if not check_server():
        print("\n❌ Error: Cannot connect to API server")
        print("Please start the server with: python main.py serve")
        print("Then run this script again.\n")
        return
    
    # Initialize
    clear_screen()
    print_header()
    
    use_advanced = True
    show_metadata = False
    
    print(f"Mode: {'Advanced' if use_advanced else 'Basic'}")
    print(f"Metadata: {'Shown' if show_metadata else 'Hidden'}")
    print()
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command in ['/quit', '/exit', '/q']:
                    print("\nGoodbye! 👋\n")
                    break
                
                elif command == '/help':
                    print_help()
                    continue
                
                elif command == '/mode':
                    use_advanced = not use_advanced
                    mode_name = "Advanced" if use_advanced else "Basic"
                    print(f"\n✅ Switched to {mode_name} mode\n")
                    continue
                
                elif command == '/stats':
                    show_cache_stats()
                    continue
                
                elif command == '/clear':
                    clear_screen()
                    print_header()
                    print(f"Mode: {'Advanced' if use_advanced else 'Basic'}")
                    print(f"Metadata: {'Shown' if show_metadata else 'Hidden'}")
                    print()
                    continue
                
                elif command == '/metadata':
                    show_metadata = not show_metadata
                    status = "shown" if show_metadata else "hidden"
                    print(f"\n✅ Metadata will be {status}\n")
                    continue
                
                else:
                    print(f"\n❌ Unknown command: {user_input}")
                    print("Type /help for available commands\n")
                    continue
            
            # Process question
            print("\nThinking...", end='', flush=True)
            start_time = time.time()
            
            result = query_api(user_input, use_advanced=use_advanced)
            
            elapsed = time.time() - start_time
            
            # Clear "Thinking..." message
            print("\r" + " " * 20 + "\r", end='')
            
            # Show result
            format_answer(result, show_metadata=show_metadata)
            
            # Show timing
            if not show_metadata:
                print(f"(Query took {elapsed:.1f}s)\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")

def main():
    """Entry point"""
    try:
        chat()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
