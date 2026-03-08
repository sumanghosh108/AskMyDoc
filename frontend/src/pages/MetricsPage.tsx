import { useEffect } from 'react';
import { MetricsPanel } from '@/components';
import { useSystemStore } from '@/stores';
import { fetchMetrics } from '@/services';
import toast from 'react-hot-toast';

export default function MetricsPage() {
  const { metrics, setMetrics } = useSystemStore();

  const handleRefresh = async () => {
    try {
      const data = await fetchMetrics();
      setMetrics(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch metrics';
      toast.error(errorMessage);
    }
  };

  // Initial fetch on mount
  useEffect(() => {
    handleRefresh();
  }, []);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">System Metrics</h2>
        <p className="text-gray-600 mt-1">
          Monitor system performance and usage statistics
        </p>
      </div>

      <MetricsPanel metrics={metrics} onRefresh={handleRefresh} />

      {/* Additional Information */}
      <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">About Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Total Queries</h4>
            <p>Total number of queries processed by the system</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Average Latency</h4>
            <p>Average response time for query processing</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Cache Hit Rate</h4>
            <p>Percentage of queries served from cache</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Document Count</h4>
            <p>Total number of documents in the knowledge base</p>
          </div>
        </div>
      </div>
    </div>
  );
}
