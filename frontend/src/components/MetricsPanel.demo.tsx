/**
 * MetricsPanel Demo
 * 
 * Example usage of the MetricsPanel component with the systemStore
 */

import { useEffect } from 'react';
import MetricsPanel from './MetricsPanel';
import { useSystemStore } from '../stores/systemStore';
import { fetchMetrics } from '../services/metricsService';

export default function MetricsPanelDemo() {
  const metrics = useSystemStore((state) => state.metrics);
  const setMetrics = useSystemStore((state) => state.setMetrics);

  const handleRefresh = async () => {
    try {
      const newMetrics = await fetchMetrics();
      setMetrics(newMetrics);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  // Fetch metrics on mount
  useEffect(() => {
    handleRefresh();
  }, []);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <MetricsPanel
        metrics={metrics}
        onRefresh={handleRefresh}
        refreshInterval={30000} // 30 seconds
      />
    </div>
  );
}
