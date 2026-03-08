import requests

# Test file upload
with open('test_upload.txt', 'rb') as f:
    files = {'file': ('test_upload.txt', f, 'text/plain')}
    response = requests.post('http://localhost:8000/api/v1/ingest/upload', files=files)
    
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
