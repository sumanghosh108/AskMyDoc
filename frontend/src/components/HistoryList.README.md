# HistoryList Component

## Overview

The `HistoryList` component displays and manages query history for the RAG system. It provides an interactive list of previous queries with the ability to view past results and clear history.

## Features

- **Descending Order Display**: Queries are displayed in descending timestamp order (most recent first)
- **Question & Answer Previews**: Shows truncated previews of questions and answers
- **Formatted Timestamps**: Uses date-fns for human-readable relative timestamps
- **Click to View**: Click any history item to display the full previous result
- **Clear History**: Button to clear all history with confirmation dialog
- **Performance Optimized**: Uses React.memo for list items to prevent unnecessary re-renders
- **Responsive Design**: Scrollable list with max height for long histories
- **Accessibility**: Full keyboard navigation and screen reader support

## Requirements Satisfied

- **6.2**: Display queries in descending order by timestamp
- **6.3**: Click handler to display previous results
- **6.4**: Show question and answer previews
- **6.5**: Display formatted timestamps
- **6.6**: Clear history button with confirmation
- **13.5**: React.memo for performance optimization
- **16.5**: Responsive and scrollable for all screen sizes

## Props

```typescript
interface HistoryListProps {
  history: QueryHistoryItem[];        // Array of query history items
  onSelectQuery: (item: QueryHistoryItem) => void;  // Callback when item is clicked
  onClearHistory: () => void;         // Callback when clear history is confirmed
}
```

## Usage

### Basic Usage with queryStore

```tsx
import { useQueryStore } from '../stores/queryStore';
import HistoryList from './HistoryList';

function MyComponent() {
  const { history, setCurrentResult, clearHistory } = useQueryStore();

  return (
    <HistoryList
      history={history}
      onSelectQuery={setCurrentResult}
      onClearHistory={clearHistory}
    />
  );
}
```

### With Custom Handlers

```tsx
import HistoryList from './HistoryList';

function MyComponent() {
  const handleSelectQuery = (item: QueryHistoryItem) => {
    console.log('Selected query:', item.question);
    // Display the result in your UI
  };

  const handleClearHistory = () => {
    console.log('Clearing history');
    // Clear history from your state management
  };

  return (
    <HistoryList
      history={myHistory}
      onSelectQuery={handleSelectQuery}
      onClearHistory={handleClearHistory}
    />
  );
}
```

## Component Structure

### HistoryItem (Memoized)

Individual history item component that displays:
- Question preview (truncated to 100 characters)
- Answer preview (truncated to 150 characters)
- Relative timestamp (e.g., "2 hours ago")
- Number of sources
- Hover and focus states for accessibility

### HistoryList (Main Component)

Main container that includes:
- Header with title and clear button
- Confirmation dialog for clearing history
- Scrollable list of history items
- Empty state when no history exists

## Styling

The component uses TailwindCSS for styling with:
- Responsive design that works on all screen sizes
- Hover states for interactive elements
- Focus rings for keyboard navigation
- Color-coded clear button (red) for destructive action
- Smooth transitions for better UX

## Performance Considerations

1. **React.memo**: Individual `HistoryItem` components are memoized to prevent unnecessary re-renders when other items change
2. **Scrollable Container**: Max height of 600px with overflow-y-auto prevents performance issues with long lists
3. **Virtual Scrolling**: For extremely long lists (>100 items), consider adding react-window for virtual scrolling

## Accessibility

- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **ARIA Labels**: Proper labels for screen readers
- **Semantic HTML**: Uses semantic elements (section, header, ul, li)
- **Focus Management**: Clear focus indicators for keyboard users
- **Alert Dialog**: Confirmation dialog uses proper ARIA roles

## Empty State

When there's no history, the component displays:
- Clock icon
- "No query history yet" message
- Helpful hint about where queries will appear

## Clear History Confirmation

The confirmation dialog:
- Shows the number of items to be deleted
- Warns that the action cannot be undone
- Provides clear "Yes, Clear All" and "Cancel" buttons
- Uses yellow background to indicate caution

## Integration with queryStore

The component is designed to work seamlessly with the Zustand queryStore:

```typescript
const { history, setCurrentResult, clearHistory } = useQueryStore();

<HistoryList
  history={history}
  onSelectQuery={setCurrentResult}
  onClearHistory={clearHistory}
/>
```

The queryStore automatically:
- Maintains descending timestamp order
- Persists history to localStorage
- Limits history to 50 most recent items

## Example with Full Integration

See `HistoryList.demo.tsx` for a complete example showing:
- Integration with queryStore
- Display of selected query with AnswerDisplay component
- Side-by-side layout for history and results
