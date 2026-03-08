import apiClient from './apiClient';
import type { SystemMetrics } from '../types';

/**
 * Metrics Service
 * 
 * Handles fetching system metrics from the backend API.
 * 
 * Features:
 * - Fetches metrics from /api/v1/metrics endpoint
 * - Supports auto-refresh with configurable interval
 * - Provides detailed error handling
 * - Manages refresh intervals and cleanup
 * 
 * Requirements: 7.1, 7.7
 */

/**
 * Fetch current system metrics
 * 
 * @returns Promise resolving to system metrics
 * @throws Error with detailed message on failure
 * 
 * @example
 * const metrics = await fetchMetrics();
 * console.log(`Total queries: ${metrics.totalQueries}`);
 */
export async function fetchMetrics(): Promise<SystemMetrics> {
  try {
    const response = await apiClient.get<SystemMetrics>('/api/v1/metrics');

    // Validate response structure
    if (!response.data || typeof response.data.totalQueries !== 'number') {
      throw new Error('Invalid metrics format from server');
    }

    return response.data;
  } catch (error: any) {
    // Enhanced error handling
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;

      if (status === 500) {
        throw new Error('Server error: Unable to retrieve metrics. Please try again.');
      } else if (status === 503) {
        throw new Error('Service unavailable: Metrics service is temporarily unavailable.');
      } else {
        throw new Error(`Failed to fetch metrics: ${detail || error.message}`);
      }
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Metrics request timeout: The server took too long to respond.');
    } else if (error.code === 'ERR_NETWORK' || !error.response) {
      throw new Error('Network error: Unable to reach the backend server.');
    } else {
      throw new Error(error.message || 'An unexpected error occurred while fetching metrics');
    }
  }
}

/**
 * Start auto-refresh of metrics with configurable interval
 * 
 * @param callback - Function to call with updated metrics
 * @param intervalMs - Refresh interval in milliseconds (default: 30000ms = 30s)
 * @returns Cleanup function to stop auto-refresh
 * 
 * @example
 * const stopRefresh = startAutoRefresh((metrics) => {
 *   console.log('Metrics updated:', metrics);
 * }, 30000);
 * 
 * // Later, stop auto-refresh
 * stopRefresh();
 */
export function startAutoRefresh(
  callback: (metrics: SystemMetrics) => void,
  intervalMs: number = 30000
): () => void {
  // Validate interval
  if (intervalMs < 1000) {
    console.warn('Auto-refresh interval too short, using minimum of 1000ms');
    intervalMs = 1000;
  }

  // Fetch immediately
  fetchMetrics()
    .then(callback)
    .catch((error) => {
      console.error('Failed to fetch initial metrics:', error);
    });

  // Set up interval for periodic refresh
  const intervalId = setInterval(() => {
    fetchMetrics()
      .then(callback)
      .catch((error) => {
        console.error('Failed to fetch metrics during auto-refresh:', error);
      });
  }, intervalMs);

  // Return cleanup function
  return () => {
    clearInterval(intervalId);
  };
}

export default {
  fetchMetrics,
  startAutoRefresh,
};
