import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

/**
 * Configured Axios instance for API communication with the FastAPI backend
 * 
 * Features:
 * - Base URL from environment variable (VITE_API_BASE_URL)
 * - Configurable timeout from environment variable (VITE_API_TIMEOUT)
 * - Request interceptor for logging and header configuration
 * - Response interceptor for error handling and transformation
 * - Proper CORS and JSON serialization
 * 
 * @example
 * import apiClient from '@/services/apiClient';
 * const response = await apiClient.post('/api/v1/query', { question: 'What is ML?' });
 */

// Get configuration from environment variables with defaults
// In production, use relative URL (empty string) so requests go through Vercel's rewrites/proxy
const BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');
const TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '60000', 10);

// Create Axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  // Enable CORS credentials if needed
  withCredentials: false,
});

/**
 * Request interceptor
 * - Logs outgoing requests in development
 * - Adds timestamp to track request duration
 * - Can be extended for authentication tokens
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add request timestamp for latency tracking
    config.metadata = { startTime: Date.now() };
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }
    
    return config;
  },
  (error: AxiosError) => {
    // Log request errors
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * - Logs responses and errors in development
 * - Transforms error responses into user-friendly messages
 * - Tracks request latency
 * - Handles common error scenarios (network, timeout, server errors)
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Calculate request latency
    const latency = Date.now() - (response.config.metadata?.startTime || Date.now());
    
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        latency: `${latency}ms`,
        data: response.data,
      });
    }
    
    return response;
  },
  (error: AxiosError) => {
    // Enhanced error handling with detailed information
    const errorDetails = {
      message: 'An error occurred',
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method,
    };
    
    // Handle different error scenarios
    if (error.code === 'ECONNABORTED') {
      // Timeout error
      errorDetails.message = `Request timeout after ${TIMEOUT}ms. The server took too long to respond.`;
      console.error('[API Timeout]', errorDetails);
    } else if (error.code === 'ERR_NETWORK' || !error.response) {
      // Network error - backend unreachable
      errorDetails.message = 'Network error: Unable to reach the backend server. Please check your connection and ensure the backend is running.';
      console.error('[API Network Error]', errorDetails);
    } else if (error.response?.status === 500) {
      // Server error
      errorDetails.message = 'Server error: The backend encountered an internal error. Please try again later.';
      console.error('[API Server Error]', errorDetails);
    } else if (error.response?.status === 404) {
      // Not found
      errorDetails.message = 'Resource not found: The requested endpoint does not exist.';
      console.error('[API Not Found]', errorDetails);
    } else if (error.response?.status === 400) {
      // Bad request - use server message if available
      const serverMessage = (error.response.data as any)?.detail || (error.response.data as any)?.message;
      errorDetails.message = serverMessage || 'Bad request: Invalid data sent to the server.';
      console.error('[API Bad Request]', errorDetails);
    } else if (error.response?.status === 422) {
      // Validation error
      const serverMessage = (error.response.data as any)?.detail || (error.response.data as any)?.message;
      errorDetails.message = serverMessage || 'Validation error: The data sent to the server is invalid.';
      console.error('[API Validation Error]', errorDetails);
    } else {
      // Generic error
      errorDetails.message = `Request failed: ${error.message}`;
      console.error('[API Error]', errorDetails);
    }
    
    // Attach enhanced error details to the error object
    error.message = errorDetails.message;
    (error as any).details = errorDetails;
    
    return Promise.reject(error);
  }
);

// Extend Axios types to include metadata
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

export default apiClient;
export { apiClient };
