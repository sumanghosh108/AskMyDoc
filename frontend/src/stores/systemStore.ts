import { create } from 'zustand';
import type { SystemMetrics, HealthStatus } from '../types';

interface SystemState {
  // State
  metrics: SystemMetrics | null;
  healthStatus: HealthStatus | null;

  // Actions
  setMetrics: (metrics: SystemMetrics) => void;
  setHealthStatus: (status: Omit<HealthStatus, 'lastChecked'>) => void;
}

export const useSystemStore = create<SystemState>((set) => ({
  // Initial state
  metrics: null,
  healthStatus: null,

  // Actions
  setMetrics: (metrics: SystemMetrics) =>
    set({
      metrics,
    }),

  setHealthStatus: (status: Omit<HealthStatus, 'lastChecked'>) =>
    set({
      healthStatus: {
        ...status,
        // Add lastChecked timestamp to health status updates
        lastChecked: new Date(),
      },
    }),
}));
