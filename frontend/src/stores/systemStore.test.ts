import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useSystemStore } from './systemStore';
import type { SystemMetrics, HealthStatus } from '../types';

describe('systemStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useSystemStore.setState({
      metrics: null,
      healthStatus: null,
    });
    // Reset date mocks
    vi.useRealTimers();
  });

  it('should initialize with default state', () => {
    const state = useSystemStore.getState();
    expect(state.metrics).toBeNull();
    expect(state.healthStatus).toBeNull();
  });

  it('should set metrics', () => {
    const { setMetrics } = useSystemStore.getState();
    const mockMetrics: SystemMetrics = {
      totalQueries: 100,
      avgLatencyMs: 250,
      cacheHitRate: 0.85,
      vectorStoreDocs: 50,
    };

    setMetrics(mockMetrics);
    expect(useSystemStore.getState().metrics).toEqual(mockMetrics);
  });

  it('should set metrics with cache stats', () => {
    const { setMetrics } = useSystemStore.getState();
    const mockMetrics: SystemMetrics = {
      totalQueries: 100,
      avgLatencyMs: 250,
      cacheHitRate: 0.85,
      vectorStoreDocs: 50,
      cacheStats: {
        enabled: true,
        connected: true,
        totalRagKeys: 25,
        keyspaceHits: 85,
        keyspaceMisses: 15,
        hitRate: 0.85,
      },
    };

    setMetrics(mockMetrics);
    expect(useSystemStore.getState().metrics).toEqual(mockMetrics);
  });

  it('should set health status and add lastChecked timestamp', () => {
    const { setHealthStatus } = useSystemStore.getState();
    const mockStatus: Omit<HealthStatus, 'lastChecked'> = {
      status: 'ok',
      service: 'rag-api',
      database: 'healthy',
      databaseTables: 3,
    };

    const beforeTime = new Date();
    setHealthStatus(mockStatus);
    const afterTime = new Date();

    const state = useSystemStore.getState();
    expect(state.healthStatus).toBeDefined();
    expect(state.healthStatus?.status).toBe('ok');
    expect(state.healthStatus?.service).toBe('rag-api');
    expect(state.healthStatus?.database).toBe('healthy');
    expect(state.healthStatus?.databaseTables).toBe(3);
    expect(state.healthStatus?.lastChecked).toBeInstanceOf(Date);
    expect(state.healthStatus?.lastChecked.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime());
    expect(state.healthStatus?.lastChecked.getTime()).toBeLessThanOrEqual(afterTime.getTime());
  });

  it('should set unhealthy status with error message', () => {
    const { setHealthStatus } = useSystemStore.getState();
    const mockStatus: Omit<HealthStatus, 'lastChecked'> = {
      status: 'error',
      service: 'rag-api',
      database: 'unhealthy',
      databaseError: 'Connection refused',
    };

    setHealthStatus(mockStatus);

    const state = useSystemStore.getState();
    expect(state.healthStatus?.status).toBe('error');
    expect(state.healthStatus?.database).toBe('unhealthy');
    expect(state.healthStatus?.databaseError).toBe('Connection refused');
    expect(state.healthStatus?.lastChecked).toBeInstanceOf(Date);
  });

  it('should update lastChecked timestamp on each health status update', () => {
    vi.useFakeTimers();
    const { setHealthStatus } = useSystemStore.getState();
    
    const mockStatus: Omit<HealthStatus, 'lastChecked'> = {
      status: 'ok',
      service: 'rag-api',
      database: 'healthy',
    };

    // First update
    const time1 = new Date('2024-01-01T10:00:00Z');
    vi.setSystemTime(time1);
    setHealthStatus(mockStatus);
    const firstCheck = useSystemStore.getState().healthStatus?.lastChecked;

    // Second update
    const time2 = new Date('2024-01-01T10:00:10Z');
    vi.setSystemTime(time2);
    setHealthStatus(mockStatus);
    const secondCheck = useSystemStore.getState().healthStatus?.lastChecked;

    expect(firstCheck).toEqual(time1);
    expect(secondCheck).toEqual(time2);
    expect(secondCheck?.getTime()).toBeGreaterThan(firstCheck?.getTime() || 0);
  });

  it('should handle unknown status', () => {
    const { setHealthStatus } = useSystemStore.getState();
    const mockStatus: Omit<HealthStatus, 'lastChecked'> = {
      status: 'unknown',
      service: 'rag-api',
      database: 'unknown',
    };

    setHealthStatus(mockStatus);

    const state = useSystemStore.getState();
    expect(state.healthStatus?.status).toBe('unknown');
    expect(state.healthStatus?.database).toBe('unknown');
  });

  it('should replace previous metrics when setting new metrics', () => {
    const { setMetrics } = useSystemStore.getState();
    
    const firstMetrics: SystemMetrics = {
      totalQueries: 100,
      avgLatencyMs: 250,
      cacheHitRate: 0.85,
      vectorStoreDocs: 50,
    };

    const secondMetrics: SystemMetrics = {
      totalQueries: 200,
      avgLatencyMs: 300,
      cacheHitRate: 0.90,
      vectorStoreDocs: 75,
    };

    setMetrics(firstMetrics);
    expect(useSystemStore.getState().metrics).toEqual(firstMetrics);

    setMetrics(secondMetrics);
    expect(useSystemStore.getState().metrics).toEqual(secondMetrics);
  });

  it('should replace previous health status when setting new status', () => {
    const { setHealthStatus } = useSystemStore.getState();
    
    const firstStatus: Omit<HealthStatus, 'lastChecked'> = {
      status: 'ok',
      service: 'rag-api',
      database: 'healthy',
      databaseTables: 3,
    };

    const secondStatus: Omit<HealthStatus, 'lastChecked'> = {
      status: 'error',
      service: 'rag-api',
      database: 'unhealthy',
      databaseError: 'Connection lost',
    };

    setHealthStatus(firstStatus);
    const firstState = useSystemStore.getState().healthStatus;
    expect(firstState?.status).toBe('ok');

    setHealthStatus(secondStatus);
    const secondState = useSystemStore.getState().healthStatus;
    expect(secondState?.status).toBe('error');
    expect(secondState?.databaseError).toBe('Connection lost');
    expect(secondState?.databaseTables).toBeUndefined();
  });
});
