import { useEffect } from 'react';
import type { HealthStatus } from '../types';
import { formatRelativeTime } from '../utils/formatters';

/**
 * HealthIndicator Component
 * 
 * Displays backend health status with colored indicator and detailed tooltip.
 * Auto-checks health at configurable intervals.
 * 
 * Features:
 * - Colored status indicator (green/yellow/red)
 * - Service and database status display
 * - Detailed tooltip with database info
 * - Auto-check every 10 seconds
 * - Graceful handling of backend unreachable
 * - Accessibility features (text alternatives, ARIA live regions)
 * 
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 15.5
 */

interface HealthIndicatorProps {
  status: HealthStatus | null;
  onCheck: () => void;
  checkInterval?: number; // in milliseconds, default 10000 (10s)
}

export default function HealthIndicator({
  status,
  onCheck,
  checkInterval = 10000,
}: HealthIndicatorProps) {
  // Auto-check health at specified interval
  useEffect(() => {
    if (checkInterval <= 0) return;

    // Check immediately on mount
    onCheck();

    const intervalId = setInterval(() => {
      onCheck();
    }, checkInterval);

    return () => clearInterval(intervalId);
  }, [checkInterval, onCheck]);

  if (!status) {
    return (
      <div className="flex items-center gap-2">
        <StatusDot color="gray" />
        <span className="text-sm text-gray-600">Checking...</span>
      </div>
    );
  }

  const statusColor = getStatusColor(status);
  const statusText = getStatusText(status);

  return (
    <div className="relative group">
      {/* Main indicator */}
      <div className="flex items-center gap-2 cursor-help">
        <StatusDot color={statusColor} />
        <span className="text-sm font-medium text-gray-700">
          {statusText}
        </span>
      </div>

      {/* Detailed tooltip */}
      <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 p-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">
          System Health Details
        </h4>

        <div className="space-y-3">
          {/* Service Status */}
          <DetailRow
            label="Service"
            value={status.service}
            status={status.status === 'ok' ? 'healthy' : 'error'}
          />

          {/* Database Status */}
          <DetailRow
            label="Database"
            value={status.database}
            status={
              status.database === 'healthy'
                ? 'healthy'
                : status.database === 'unhealthy' || status.database === 'error'
                ? 'error'
                : 'unknown'
            }
          />

          {/* Database Tables (when healthy) */}
          {status.database === 'healthy' && status.databaseTables !== undefined && (
            <DetailRow
              label="Tables"
              value={`${status.databaseTables} tables`}
              status="healthy"
            />
          )}

          {/* Database Error (when unhealthy) */}
          {(status.database === 'unhealthy' || status.database === 'error') &&
            status.databaseError && (
              <div className="pt-2 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-700 mb-1">
                  Error Details:
                </p>
                <p className="text-xs text-red-600 break-words">
                  {status.databaseError}
                </p>
              </div>
            )}

          {/* Last Check Timestamp */}
          <div className="pt-2 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Last checked {formatRelativeTime(status.lastChecked)}
            </p>
          </div>
        </div>
      </div>

      {/* ARIA live region for status updates (accessibility) */}
      <div
        className="sr-only"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        System status: {statusText}. Service: {status.service}. Database:{' '}
        {status.database}.
        {status.database === 'healthy' && status.databaseTables !== undefined
          ? ` ${status.databaseTables} tables available.`
          : ''}
        {status.databaseError ? ` Error: ${status.databaseError}` : ''}
      </div>
    </div>
  );
}

/**
 * StatusDot Component
 * 
 * Displays a colored status indicator dot
 */
interface StatusDotProps {
  color: 'green' | 'yellow' | 'red' | 'gray';
}

function StatusDot({ color }: StatusDotProps) {
  const colorClasses = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    gray: 'bg-gray-400',
  };

  return (
    <span
      className={`inline-block h-3 w-3 rounded-full ${colorClasses[color]}`}
      aria-hidden="true"
    />
  );
}

/**
 * DetailRow Component
 * 
 * Displays a single detail row in the tooltip
 */
interface DetailRowProps {
  label: string;
  value: string;
  status: 'healthy' | 'error' | 'unknown';
}

function DetailRow({ label, value, status }: DetailRowProps) {
  const statusColors = {
    healthy: 'text-green-700',
    error: 'text-red-700',
    unknown: 'text-yellow-700',
  };

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-600">{label}:</span>
      <span className={`text-sm font-medium ${statusColors[status]}`}>
        {value}
      </span>
    </div>
  );
}

/**
 * Helper function to determine status color
 */
function getStatusColor(
  status: HealthStatus
): 'green' | 'yellow' | 'red' | 'gray' {
  if (status.status === 'ok' && status.database === 'healthy') {
    return 'green';
  } else if (status.status === 'unknown' || status.database === 'unknown') {
    return 'yellow';
  } else {
    return 'red';
  }
}

/**
 * Helper function to get status text with accessibility
 */
function getStatusText(status: HealthStatus): string {
  if (status.status === 'ok' && status.database === 'healthy') {
    return 'Healthy';
  } else if (status.status === 'unknown' || status.database === 'unknown') {
    return 'Unknown';
  } else if (status.service === 'unreachable') {
    return 'Unreachable';
  } else if (status.service === 'timeout') {
    return 'Timeout';
  } else {
    return 'Error';
  }
}
