/**
 * HealthIndicator Demo
 * 
 * Example usage of the HealthIndicator component with the systemStore
 */

import HealthIndicator from './HealthIndicator';
import { useSystemStore } from '../stores/systemStore';
import { checkHealth } from '../services/healthService';

export default function HealthIndicatorDemo() {
  const healthStatus = useSystemStore((state) => state.healthStatus);
  const setHealthStatus = useSystemStore((state) => state.setHealthStatus);

  const handleCheck = async () => {
    try {
      const newStatus = await checkHealth();
      setHealthStatus(newStatus);
    } catch (error) {
      console.error('Failed to check health:', error);
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Health Indicator Demo
        </h1>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              System Status
            </h2>
            <HealthIndicator
              status={healthStatus}
              onCheck={handleCheck}
              checkInterval={10000} // 10 seconds
            />
          </div>

          {/* Additional info */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Hover over the status indicator to see detailed health information.
              The health check runs automatically every 10 seconds.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
