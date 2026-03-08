import requests
import os

# Find a PDF file to test with
pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

if not pdf_files:
    print("No PDF files found in current directory")
    print("Creating a test PDF...")
    # Create a minimal PDF for testing
    from reportlab.pdfgen import canvas
    test_pdf = "test_document.pdf"
    c = canvas.Canvas(test_pdf)
    c.drawString(100, 750, "Test Document for Upload")
    c.drawString(100, 730, "This is a test PDF file.")
    c.save()
    pdf_file = test_pdf
else:
    pdf_file = pdf_files[0]

print(f"Testing upload with: {pdf_file}")

try:
    with open(pdf_file, 'rb') as f:
        files = {'file': (pdf_file, f, 'application/pdf')}
        response = requests.post('http://localhost:8000/api/v1/ingest/upload', files=files, timeout=120)
        
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except requests.exceptions.Timeout:
    print("Request timed out - backend might be processing")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
