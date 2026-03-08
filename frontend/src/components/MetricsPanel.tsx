import { useEffect, useState } from 'react';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import type { SystemMetrics } from '../types';
import { formatNumber, formatLatency, formatPercentage, formatRelativeTime } from '../utils/formatters';

/**
 * MetricsPanel Component
 * 
 * Displays system performance metrics including query count, latency,
 * cache hit rate, and document count. Supports manual and auto-refresh.
 * 
 * Features:
 * - Card layout for metrics display
 * - Detailed cache statistics when available
 * - Manual refresh button
 * - Auto-refresh every 30 seconds
 * - Responsive layout (grid on large screens, stack on small)
 * - Last updated timestamp
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 16.4
 */

interface MetricsPanelProps {
  metrics: SystemMetrics | null;
  onRefresh: () => void;
  refreshInterval?: number; // in milliseconds, default 30000 (30s)
  isLoading?: boolean;
}

export default function MetricsPanel({
  metrics,
  onRefresh,
  refreshInterval = 30000,
  isLoading = false,
}: MetricsPanelProps) {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Auto-refresh metrics at specified interval
  useEffect(() => {
    if (refreshInterval <= 0) return;

    const intervalId = setInterval(() => {
      onRefresh();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [refreshInterval, onRefresh]);

  // Update lastUpdated timestamp when metrics change
  useEffect(() => {
    if (metrics) {
      setLastUpdated(new Date());
    }
  }, [metrics]);

  const handleManualRefresh = () => {
    onRefresh();
  };

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">System Metrics</h2>
        <div className="flex items-center gap-4">
          {lastUpdated && (
            <span className="text-sm text-gray-500">
              Updated {formatRelativeTime(lastUpdated)}
            </span>
          )}
          <button
            onClick={handleManualRefresh}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Refresh metrics"
          >
            <ArrowPathIcon
              className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`}
            />
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics grid - responsive layout */}
      {metrics ? (
        <>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {/* Total Queries */}
            <MetricCard
              title="Total Queries"
              value={formatNumber(metrics.totalQueries)}
              description="Total number of queries processed"
            />

            {/* Average Latency */}
            <MetricCard
              title="Avg Latency"
              value={formatLatency(metrics.avgLatencyMs)}
              description="Average query processing time"
            />

            {/* Cache Hit Rate */}
            <MetricCard
              title="Cache Hit Rate"
              value={formatPercentage(metrics.cacheHitRate, 1, true)}
              description="Percentage of queries served from cache"
            />

            {/* Document Count */}
            <MetricCard
              title="Documents"
              value={formatNumber(metrics.vectorStoreDocs)}
              description="Total documents in vector store"
            />
          </div>

          {/* Detailed cache statistics */}
          {metrics.cacheStats && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Cache Statistics
              </h3>
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                {/* Cache status */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    Cache Status
                  </span>
                  <div className="flex items-center gap-4">
                    <StatusBadge
                      label="Enabled"
                      status={metrics.cacheStats.enabled}
                    />
                    <StatusBadge
                      label="Connected"
                      status={metrics.cacheStats.connected}
                    />
                  </div>
                </div>

                {/* Cache metrics grid */}
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 pt-4 border-t border-gray-200">
                  <CacheStatItem
                    label="Total RAG Keys"
                    value={formatNumber(metrics.cacheStats.totalRagKeys)}
                  />
                  <CacheStatItem
                    label="Keyspace Hits"
                    value={formatNumber(metrics.cacheStats.keyspaceHits)}
                  />
                  <CacheStatItem
                    label="Keyspace Misses"
                    value={formatNumber(metrics.cacheStats.keyspaceMisses)}
                  />
                  <CacheStatItem
                    label="Hit Rate"
                    value={formatPercentage(metrics.cacheStats.hitRate, 2, true)}
                  />
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 text-gray-500">
          {isLoading ? 'Loading metrics...' : 'No metrics available'}
        </div>
      )}
    </div>
  );
}

/**
 * MetricCard Component
 * 
 * Displays a single metric in a card layout
 */
interface MetricCardProps {
  title: string;
  value: string;
  description: string;
}

function MetricCard({ title, value, description }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-xs text-gray-600">{description}</p>
    </div>
  );
}

/**
 * StatusBadge Component
 * 
 * Displays a status indicator with label
 */
interface StatusBadgeProps {
  label: string;
  status: boolean;
}

function StatusBadge({ label, status }: StatusBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">{label}:</span>
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          status
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}
      >
        {status ? 'Yes' : 'No'}
      </span>
    </div>
  );
}

/**
 * CacheStatItem Component
 * 
 * Displays a single cache statistic
 */
interface CacheStatItemProps {
  label: string;
  value: string;
}

function CacheStatItem({ label, value }: CacheStatItemProps) {
  return (
    <div>
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}
