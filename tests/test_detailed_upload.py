import requests
import traceback

# Test file upload with detailed error handling
try:
    with open('test_upload.txt', 'rb') as f:
        files = {'file': ('test_upload.txt', f, 'text/plain')}
        response = requests.post('http://localhost:8000/api/v1/ingest/upload', files=files)
        
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("\nTrying to get more details from backend logs...")
        
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
