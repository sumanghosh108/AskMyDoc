/**
 * Example usage of the API client
 * This file demonstrates how to use the configured Axios instance
 * 
 * NOTE: This is an example file for reference only.
 * It is not imported or used in the application.
 */

import { apiClient } from './apiClient.js';

// Example 1: Health check
export async function exampleHealthCheck() {
  try {
    const response = await apiClient.get('/health');
    console.log('Health status:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Health check failed:', error.message);
    throw error;
  }
}

// Example 2: Submit a query
export async function exampleQuerySubmission() {
  try {
    const response = await apiClient.post('/api/v1/query', {
      question: 'What is machine learning?',
      topK: 5,
      useHybrid: true,
      useReranker: true,
    });
    console.log('Query result:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Query failed:', error.message);
    // Error details are available in error.details
    if ((error as any).details) {
      console.error('Error details:', (error as any).details);
    }
    throw error;
  }
}

// Example 3: Upload a file with progress tracking
export async function exampleFileUpload(file: File) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/api/v1/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log(`Upload progress: ${percentCompleted}%`);
        }
      },
    });

    console.log('Upload successful:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Upload failed:', error.message);
    throw error;
  }
}

// Example 4: Fetch metrics
export async function exampleFetchMetrics() {
  try {
    const response = await apiClient.get('/api/v1/metrics');
    console.log('System metrics:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Failed to fetch metrics:', error.message);
    throw error;
  }
}

// Example 5: Handle timeout scenario
export async function exampleWithCustomTimeout() {
  try {
    // Override default timeout for this specific request
    const response = await apiClient.get('/api/v1/slow-endpoint', {
      timeout: 5000, // 5 seconds
    });
    return response.data;
  } catch (error: any) {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timed out after 5 seconds');
    }
    throw error;
  }
}

// Example 6: Handle network errors
export async function exampleNetworkErrorHandling() {
  try {
    const response = await apiClient.get('/api/v1/query');
    return response.data;
  } catch (error: any) {
    if (error.code === 'ERR_NETWORK') {
      console.error('Backend is unreachable. Please check if the server is running.');
      // Show user-friendly message in UI
    } else if (error.response?.status === 500) {
      console.error('Server error occurred. Please try again later.');
    } else if (error.response?.status === 400) {
      console.error('Invalid request:', error.message);
    }
    throw error;
  }
}
