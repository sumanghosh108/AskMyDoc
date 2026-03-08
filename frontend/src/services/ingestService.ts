import apiClient from './apiClient';
import type { IngestResponse, UploadProgress } from '../types';

/**
 * Ingest Service
 * 
 * Handles file uploads to the backend API for document ingestion.
 * 
 * Features:
 * - Uploads files using FormData
 * - Tracks upload progress for each file
 * - Handles multi-file uploads sequentially
 * - Provides detailed error handling
 * 
 * Requirements: 4.8, 5.1, 12.5
 */

/**
 * Upload files to the RAG system for ingestion
 * 
 * @param files - Array of files to upload
 * @param onProgress - Optional callback for progress updates
 * @returns Promise resolving to array of upload results
 * @throws Error with detailed message on failure
 * 
 * @example
 * const results = await uploadFiles(files, (progress) => {
 *   console.log(`${progress.fileName}: ${progress.progress}%`);
 * });
 */
export async function uploadFiles(
  files: File[],
  onProgress?: (progress: UploadProgress) => void
): Promise<IngestResponse[]> {
  if (!files || files.length === 0) {
    throw new Error('No files provided for upload');
  }

  const results: IngestResponse[] = [];
  const errors: string[] = [];

  // Process files sequentially to avoid overwhelming the server
  for (const file of files) {
    try {
      // Notify upload starting
      if (onProgress) {
        onProgress({
          fileName: file.name,
          progress: 0,
          status: 'uploading',
        });
      }

      // Create FormData with the file
      const formData = new FormData();
      formData.append('file', file);

      // Upload file with progress tracking to the new upload endpoint
      const response = await apiClient.post<IngestResponse>('/api/v1/ingest/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress({
              fileName: file.name,
              progress: percentCompleted,
              status: 'uploading',
            });
          }
        },
      });

      // Validate response
      if (!response.data || typeof response.data.status !== 'string') {
        throw new Error('Invalid response format from server');
      }

      results.push(response.data);

      // Notify upload success
      if (onProgress) {
        onProgress({
          fileName: file.name,
          progress: 100,
          status: 'success',
        });
      }
    } catch (error: any) {
      // Handle individual file upload error
      const errorMessage = extractErrorMessage(error, file.name);
      errors.push(`${file.name}: ${errorMessage}`);

      // Notify upload error
      if (onProgress) {
        onProgress({
          fileName: file.name,
          progress: 0,
          status: 'error',
          error: errorMessage,
        });
      }
    }
  }

  // If all uploads failed, throw error
  if (errors.length === files.length) {
    throw new Error(`All uploads failed:\n${errors.join('\n')}`);
  }

  // If some uploads failed, include error details in results
  if (errors.length > 0) {
    console.warn('Some uploads failed:', errors);
  }

  return results;
}

/**
 * Extract detailed error message from upload error
 */
function extractErrorMessage(error: any, _fileName: string): string {
  if (error.response) {
    const status = error.response.status;
    const detail = error.response.data?.detail || error.response.data?.message;

    if (status === 400) {
      return detail || 'Invalid file format or data';
    } else if (status === 413) {
      return 'File size exceeds server limit';
    } else if (status === 415) {
      return 'Unsupported file type';
    } else if (status === 422) {
      return detail || 'File validation failed';
    } else if (status === 500) {
      return 'Server error during file processing';
    } else if (status === 503) {
      return 'Service temporarily unavailable';
    } else {
      return detail || error.message || 'Upload failed';
    }
  } else if (error.code === 'ECONNABORTED') {
    return 'Upload timeout - file may be too large';
  } else if (error.code === 'ERR_NETWORK' || !error.response) {
    return 'Network error - unable to reach server';
  } else {
    return error.message || 'Unexpected error during upload';
  }
}

export default {
  uploadFiles,
};
