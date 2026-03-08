import apiClient from './apiClient';
import type { QueryRequest, QueryResponse } from '../types';

/**
 * Query Service
 * 
 * Handles RAG query submission to the backend API.
 * 
 * Features:
 * - Posts queries to /api/v1/query endpoint
 * - Transforms request/response data
 * - Provides detailed error handling
 * - Validates query parameters
 * 
 * Requirements: 1.1, 1.3, 10.1, 10.2, 10.3
 */

/**
 * Submit a query to the RAG system
 * 
 * @param request - Query request with question and options
 * @returns Promise resolving to query response with answer and sources
 * @throws Error with detailed message on failure
 * 
 * @example
 * const response = await submitQuery({
 *   question: 'What is machine learning?',
 *   topK: 5,
 *   useHybrid: true,
 *   useReranker: true
 * });
 */
export async function submitQuery(request: QueryRequest): Promise<QueryResponse> {
  try {
    // Validate request
    if (!request.question || request.question.trim().length === 0) {
      throw new Error('Question cannot be empty');
    }

    if (request.question.length > 2000) {
      throw new Error('Question exceeds maximum length of 2000 characters');
    }

    if (request.topK !== undefined && (request.topK < 1 || request.topK > 20)) {
      throw new Error('topK must be between 1 and 20');
    }

    // Submit query to backend
    const response = await apiClient.post<QueryResponse>('/api/v1/query', request);

    // Validate response structure
    if (!response.data || typeof response.data.answer !== 'string') {
      throw new Error('Invalid response format from server');
    }

    if (!Array.isArray(response.data.sources)) {
      throw new Error('Invalid sources format in response');
    }

    return response.data;
  } catch (error: any) {
    // Enhanced error handling with detailed messages
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;

      if (status === 400) {
        throw new Error(`Bad request: ${detail || 'Invalid query parameters'}`);
      } else if (status === 422) {
        throw new Error(`Validation error: ${detail || 'Query data is invalid'}`);
      } else if (status === 500) {
        throw new Error('Server error: The backend encountered an error processing your query. Please try again.');
      } else if (status === 503) {
        throw new Error('Service unavailable: The backend service is temporarily unavailable. Please try again later.');
      } else {
        throw new Error(`Query failed: ${detail || error.message}`);
      }
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      throw new Error('Query timeout: The server took too long to respond. Please try a simpler query or try again later.');
    } else if (error.code === 'ERR_NETWORK' || !error.response) {
      // Network error
      throw new Error('Network error: Unable to reach the backend server. Please check your connection and ensure the backend is running.');
    } else {
      // Other errors (validation, etc.)
      throw new Error(error.message || 'An unexpected error occurred while submitting the query');
    }
  }
}

export default {
  submitQuery,
};
