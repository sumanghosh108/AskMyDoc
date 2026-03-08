# API Services

This directory contains all API service modules for communicating with the FastAPI backend.

## API Client

The `apiClient.ts` module provides a configured Axios instance with:

- **Base URL**: Configured from `VITE_API_BASE_URL` environment variable (default: `http://localhost:8000`)
- **Timeout**: Configured from `VITE_API_TIMEOUT` environment variable (default: `60000ms`)
- **Request Interceptor**: Adds metadata and logging for all outgoing requests
- **Response Interceptor**: Handles errors and provides user-friendly error messages

### Usage Example

```typescript
import { apiClient } from '@/services';

// Simple GET request
const response = await apiClient.get('/health');
console.log(response.data);

// POST request with data
const queryResponse = await apiClient.post('/api/v1/query', {
  question: 'What is machine learning?',
  topK: 5,
  useHybrid: true,
  useReranker: true
});

// File upload with progress tracking
const formData = new FormData();
formData.append('file', file);

const uploadResponse = await apiClient.post('/api/v1/ingest', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  onUploadProgress: (progressEvent) => {
    const percentCompleted = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    console.log(`Upload progress: ${percentCompleted}%`);
  }
});
```

### Error Handling

The API client automatically handles common error scenarios:

- **Network Errors**: When the backend is unreachable
- **Timeout Errors**: When requests exceed the configured timeout
- **Server Errors (500)**: Internal server errors
- **Not Found (404)**: Resource not found
- **Bad Request (400)**: Invalid request data
- **Validation Errors (422)**: Request validation failures

All errors include detailed information and user-friendly messages.

### Configuration

Set environment variables in `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=60000
```

## Service Modules

Additional service modules will be implemented:

- `queryService.ts` - Query submission and management
- `ingestService.ts` - Document upload and ingestion
- `metricsService.ts` - System metrics fetching
- `healthService.ts` - Health check monitoring
