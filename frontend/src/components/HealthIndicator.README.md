# HealthIndicator Component

## Overview

The `HealthIndicator` component displays backend health status with a colored indicator and detailed tooltip. It automatically checks health at configurable intervals and handles backend unreachable scenarios gracefully.

## Features

- **Colored Status Indicator**: Green (healthy), Yellow (unknown), Red (error)
- **Service Status**: Shows backend service status
- **Database Status**: Shows database connection status
- **Detailed Tooltip**: Hover to see comprehensive health information
- **Auto-Check**: Automatically checks health at configurable intervals (default: 10s)
- **Graceful Error Handling**: Handles backend unreachable scenarios
- **Accessibility**: Text alternatives for colors, ARIA live regions for status updates

## Props

```typescript
interface HealthIndicatorProps {
  status: HealthStatus | null;
  onCheck: () => void;
  checkInterval?: number; // in milliseconds, default 10000 (10s)
}
```

### `status`
- Type: `HealthStatus | null`
- Required: Yes
- Description: The current health status to display

### `onCheck`
- Type: `() => void`
- Required: Yes
- Description: Callback function to check health status

### `checkInterval`
- Type: `number`
- Required: No
- Default: `10000` (10 seconds)
- Description: Auto-check interval in milliseconds. Set to 0 to disable auto-check.

## Usage Example

```tsx
import { HealthIndicator } from '@/components';
import { useSystemStore } from '@/stores/systemStore';
import { checkHealth } from '@/services/healthService';

function Header() {
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
    <header className="flex items-center justify-between p-4">
      <h1>RAG System</h1>
      <HealthIndicator
        status={healthStatus}
        onCheck={handleCheck}
        checkInterval={10000}
      />
    </header>
  );
}
```

## Status Colors

- **Green**: System is healthy (status: 'ok', database: 'healthy')
- **Yellow**: Status is unknown (status: 'unknown' or database: 'unknown')
- **Red**: System has errors (status: 'error' or database: 'unhealthy'/'error')
- **Gray**: Checking status (initial state)

## Status Text

- **Healthy**: All systems operational
- **Unknown**: Status cannot be determined
- **Unreachable**: Backend server is unreachable
- **Timeout**: Health check timed out
- **Error**: System error occurred

## Tooltip Information

The tooltip displays:
1. **Service Status**: Backend service name and status
2. **Database Status**: Database connection status
3. **Database Tables**: Number of tables (when healthy)
4. **Error Details**: Error message (when unhealthy)
5. **Last Checked**: Relative timestamp of last health check

## Accessibility Features

- **Text Alternatives**: Status text provides alternative to color coding
- **ARIA Live Regions**: Screen readers announce status updates
- **Semantic HTML**: Proper use of roles and attributes
- **Keyboard Support**: Tooltip accessible via keyboard navigation

## Auto-Check Behavior

The component automatically:
1. Checks health immediately on mount
2. Sets up interval to check at specified interval
3. Cleans up interval on unmount
4. Handles errors gracefully without throwing

## Requirements

Implements requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 15.5
