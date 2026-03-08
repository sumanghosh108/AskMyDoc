# MetricsPanel Component

## Overview

The `MetricsPanel` component displays system performance metrics including query count, average latency, cache hit rate, and document count. It supports manual and automatic refresh functionality.

## Features

- **Card Layout**: Displays metrics in an organized card-based layout
- **Detailed Cache Stats**: Shows comprehensive cache statistics when available
- **Manual Refresh**: Button to manually refresh metrics
- **Auto-Refresh**: Automatically refreshes metrics at configurable intervals (default: 30s)
- **Responsive Design**: Grid layout on large screens, stacked on small screens
- **Last Updated Timestamp**: Shows when metrics were last refreshed

## Props

```typescript
interface MetricsPanelProps {
  metrics: SystemMetrics | null;
  onRefresh: () => void;
  refreshInterval?: number; // in milliseconds, default 30000 (30s)
  isLoading?: boolean;
}
```

### `metrics`
- Type: `SystemMetrics | null`
- Required: Yes
- Description: The current system metrics to display

### `onRefresh`
- Type: `() => void`
- Required: Yes
- Description: Callback function to refresh metrics

### `refreshInterval`
- Type: `number`
- Required: No
- Default: `30000` (30 seconds)
- Description: Auto-refresh interval in milliseconds. Set to 0 to disable auto-refresh.

### `isLoading`
- Type: `boolean`
- Required: No
- Default: `false`
- Description: Whether metrics are currently being loaded

## Usage Example

```tsx
import { MetricsPanel } from '@/components';
import { useSystemStore } from '@/stores/systemStore';
import { fetchMetrics } from '@/services/metricsService';

function MetricsPage() {
  const metrics = useSystemStore((state) => state.metrics);
  const setMetrics = useSystemStore((state) => state.setMetrics);
  const [isLoading, setIsLoading] = useState(false);

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      const newMetrics = await fetchMetrics();
      setMetrics(newMetrics);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MetricsPanel
      metrics={metrics}
      onRefresh={handleRefresh}
      refreshInterval={30000}
      isLoading={isLoading}
    />
  );
}
```

## Metrics Displayed

### Main Metrics
1. **Total Queries**: Total number of queries processed
2. **Avg Latency**: Average query processing time (formatted as ms or s)
3. **Cache Hit Rate**: Percentage of queries served from cache
4. **Documents**: Total documents in vector store

### Cache Statistics (when available)
- **Cache Status**: Enabled/Connected indicators
- **Total RAG Keys**: Number of keys in cache
- **Keyspace Hits**: Number of cache hits
- **Keyspace Misses**: Number of cache misses
- **Hit Rate**: Cache hit rate percentage

## Styling

The component uses TailwindCSS for styling and follows a responsive design pattern:
- **Mobile**: Single column layout
- **Tablet**: 2-column grid
- **Desktop**: 4-column grid

## Accessibility

- Proper ARIA labels on interactive elements
- Semantic HTML structure
- Keyboard navigation support
- Loading states clearly indicated

## Requirements

Implements requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 16.4
