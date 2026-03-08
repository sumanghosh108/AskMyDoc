// Ingest/upload-related type definitions

export interface IngestRequest {
  sources: string[];
  chunkSize?: number;
  chunkOverlap?: number;
}

export interface IngestResponse {
  status: string;
  chunksIngested: number;
  sources: string[];
}

export interface UploadProgress {
  fileName: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}
