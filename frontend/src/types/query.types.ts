// Query-related type definitions

export interface QueryRequest {
  question: string;
  topK?: number;
  useHybrid: boolean;
  useReranker: boolean;
}

export interface QueryResponse {
  answer: string;
  sources: SourceMeta[];
  contextChunks: number;
}

export interface QueryOptions {
  topK: number;
  useHybrid: boolean;
  useReranker: boolean;
}

export interface SourceMeta {
  source: string;
  page?: number;
  relevanceScore?: number;
  rerankerScore?: number;
}

export interface QueryHistoryItem {
  id: string;
  question: string;
  answer: string;
  sources: SourceMeta[];
  timestamp: Date;
  contextChunks: number;
}
