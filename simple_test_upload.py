import requests

# Create a simple test file
test_file = "simple_test.txt"
with open(test_file, 'w') as f:
    f.write("This is a simple test document.\n")
    f.write("It contains some text for testing the upload functionality.\n")
    f.write("The system should be able to process this file.\n")

print(f"Testing upload with: {test_file}")

try:
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'text/plain')}
        print("Sending request...")
        response = requests.post('http://localhost:8000/api/v1/ingest/upload', files=files, timeout=120)
        
    print(f"\nStatus Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response Text: {response.text}")
    
except requests.exceptions.Timeout:
    print("Request timed out - backend might still be processing")
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
    print("Is the backend running?")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
