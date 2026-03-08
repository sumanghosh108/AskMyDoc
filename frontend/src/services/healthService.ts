import apiClient from './apiClient';
import type { HealthStatus } from '../types';

/**
 * Health Service
 * 
 * Handles health check requests to the backend API.
 * 
 * Features:
 * - Checks health status from /health endpoint
 * - Supports auto-check with configurable interval
 * - Handles connection errors gracefully
 * - Manages check intervals and cleanup
 * 
 * Requirements: 8.1, 8.7, 8.8, 10.1
 */

/**
 * Check backend health status
 * 
 * @returns Promise resolving to health status
 * @throws Error with detailed message on failure
 * 
 * @example
 * const health = await checkHealth();
 * console.log(`Service status: ${health.status}`);
 */
export async function checkHealth(): Promise<HealthStatus> {
  try {
    const response = await apiClient.get<Omit<HealthStatus, 'lastChecked'>>('/health');

    // Validate response structure
    if (!response.data || typeof response.data.status !== 'string') {
      throw new Error('Invalid health status format from server');
    }

    // Add lastChecked timestamp
    const healthStatus: HealthStatus = {
      ...response.data,
      lastChecked: new Date(),
    };

    return healthStatus;
  } catch (error: any) {
    // Handle connection errors gracefully - return error status instead of throwing
    if (error.code === 'ERR_NETWORK' || !error.response) {
      // Backend is unreachable - return error status
      return {
        status: 'error',
        service: 'unreachable',
        database: 'unknown',
        databaseError: 'Unable to reach backend server',
        lastChecked: new Date(),
      };
    } else if (error.code === 'ECONNABORTED') {
      // Timeout - return error status
      return {
        status: 'error',
        service: 'timeout',
        database: 'unknown',
        databaseError: 'Health check timeout',
        lastChecked: new Date(),
      };
    } else if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;

      if (status === 500 || status === 503) {
        // Server error - return error status
        return {
          status: 'error',
          service: 'error',
          database: 'unknown',
          databaseError: detail || 'Server error',
          lastChecked: new Date(),
        };
      } else {
        // Other error - return error status
        return {
          status: 'error',
          service: 'error',
          database: 'unknown',
          databaseError: detail || error.message || 'Unknown error',
          lastChecked: new Date(),
        };
      }
    } else {
      // Unexpected error - return error status
      return {
        status: 'error',
        service: 'error',
        database: 'unknown',
        databaseError: error.message || 'Unexpected error',
        lastChecked: new Date(),
      };
    }
  }
}

/**
 * Start auto-check of health status with configurable interval
 * 
 * @param callback - Function to call with updated health status
 * @param intervalMs - Check interval in milliseconds (default: 10000ms = 10s)
 * @returns Cleanup function to stop auto-check
 * 
 * @example
 * const stopCheck = startAutoCheck((health) => {
 *   console.log('Health status updated:', health);
 * }, 10000);
 * 
 * // Later, stop auto-check
 * stopCheck();
 */
export function startAutoCheck(
  callback: (health: HealthStatus) => void,
  intervalMs: number = 10000
): () => void {
  // Validate interval
  if (intervalMs < 1000) {
    console.warn('Auto-check interval too short, using minimum of 1000ms');
    intervalMs = 1000;
  }

  // Check immediately
  checkHealth()
    .then(callback)
    .catch((error) => {
      // This should not happen since checkHealth handles errors gracefully
      console.error('Unexpected error during initial health check:', error);
    });

  // Set up interval for periodic checks
  const intervalId = setInterval(() => {
    checkHealth()
      .then(callback)
      .catch((error) => {
        // This should not happen since checkHealth handles errors gracefully
        console.error('Unexpected error during auto health check:', error);
      });
  }, intervalMs);

  // Return cleanup function
  return () => {
    clearInterval(intervalId);
  };
}

export default {
  checkHealth,
  startAutoCheck,
};
