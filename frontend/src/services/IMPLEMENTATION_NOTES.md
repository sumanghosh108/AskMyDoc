# API Client Implementation Notes

## Task 3.1: Create Axios API Client

### Implementation Summary

Created a fully configured Axios API client (`apiClient.ts`) with the following features:

#### ✅ Configuration
- **Base URL**: Reads from `VITE_API_BASE_URL` environment variable (default: `http://localhost:8000`)
- **Timeout**: Reads from `VITE_API_TIMEOUT` environment variable (default: `60000ms` / 60 seconds)
- **Headers**: Sets `Content-Type: application/json` by default
- **CORS**: Configured with `withCredentials: false`

#### ✅ Request Interceptor
- Adds metadata with `startTime` timestamp to track request latency
- Logs outgoing requests in development mode (method, URL, data, params)
- Extensible for future authentication token injection

#### ✅ Response Interceptor
- Calculates and logs request latency for performance monitoring
- Logs successful responses in development mode
- Comprehensive error handling for common scenarios:
  - **Timeout errors** (`ECONNABORTED`): User-friendly message with timeout duration
  - **Network errors** (`ERR_NETWORK`): Indicates backend is unreachable
  - **500 Server errors**: Generic internal server error message
  - **404 Not Found**: Resource not found message
  - **400 Bad Request**: Uses server message if available, otherwise generic message
  - **422 Validation errors**: Uses server validation message
  - **Generic errors**: Fallback error handling
- Attaches enhanced error details to error object for debugging

#### ✅ TypeScript Support
- Full type safety with Axios types
- Extended `InternalAxiosRequestConfig` interface to include metadata
- Proper type-only imports for `verbatimModuleSyntax` compatibility

#### ✅ Requirements Satisfied
- **12.1**: Base URL configured from environment variable ✓
- **12.2**: Proper headers included (Content-Type: application/json) ✓
- **12.3**: Timeout configured from environment variable (60 seconds) ✓
- **12.4**: Detailed error information provided via interceptors ✓
- **12.7**: JSON serialization handled by Axios defaults ✓

### File Structure

```
frontend/src/services/
├── apiClient.ts              # Main API client implementation
├── apiClient.example.ts      # Usage examples
├── index.ts                  # Service exports
└── README.md                 # Documentation
```

### Usage

```typescript
import { apiClient } from '@/services';

// Simple GET request
const response = await apiClient.get('/health');

// POST request with data
const result = await apiClient.post('/api/v1/query', {
  question: 'What is machine learning?',
  topK: 5,
  useHybrid: true,
  useReranker: true
});

// File upload with progress tracking
const formData = new FormData();
formData.append('file', file);

const uploadResult = await apiClient.post('/api/v1/ingest', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  onUploadProgress: (progressEvent) => {
    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    console.log(`Upload: ${percent}%`);
  }
});
```

### Error Handling

All errors are enhanced with user-friendly messages and detailed information:

```typescript
try {
  await apiClient.post('/api/v1/query', data);
} catch (error: any) {
  console.error(error.message); // User-friendly message
  console.error(error.details);  // Detailed error information
}
```

### Testing

Unit tests will be added once Vitest is configured in the project (Task 20.x).

### Next Steps

The following service modules will build on this API client:
- `queryService.ts` (Task 3.2) - Query submission
- `ingestService.ts` (Task 3.3) - Document upload
- `metricsService.ts` (Task 3.4) - Metrics fetching
- `healthService.ts` (Task 3.5) - Health monitoring

### Notes

- The `.js` extension is required in imports due to `verbatimModuleSyntax` TypeScript setting
- Both default and named exports are provided for flexibility
- Development logging can be disabled by checking `import.meta.env.DEV`
- The client is ready for immediate use by other services and components
