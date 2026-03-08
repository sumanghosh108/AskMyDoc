// System metrics and health-related type definitions

export interface SystemMetrics {
  totalQueries: number;
  avgLatencyMs: number;
  cacheHitRate: number;
  vectorStoreDocs: number;
  cacheStats?: CacheStats;
}

export interface CacheStats {
  enabled: boolean;
  connected: boolean;
  totalRagKeys: number;
  keyspaceHits: number;
  keyspaceMisses: number;
  hitRate: number;
}

export interface HealthStatus {
  status: 'ok' | 'error' | 'unknown';
  service: string;
  database: 'healthy' | 'unhealthy' | 'error' | 'unknown';
  databaseTables?: number;
  databaseError?: string;
  lastChecked: Date;
}
