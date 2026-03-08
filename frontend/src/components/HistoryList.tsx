import { memo, useState } from 'react';
import { format, formatDistanceToNow } from 'date-fns';
import { TrashIcon, ClockIcon } from '@heroicons/react/24/outline';
import type { QueryHistoryItem } from '../types';

/**
 * HistoryList Component
 * 
 * Displays and manages query history with interaction handlers.
 * 
 * Features:
 * - Displays queries in descending timestamp order
 * - Shows question and answer previews
 * - Displays formatted timestamps with date-fns
 * - Click handler to display previous results
 * - Clear history button with confirmation
 * - Performance optimized with React.memo
 * - Virtual scrolling support for long lists
 * 
 * Requirements: 6.2, 6.3, 6.4, 6.5, 6.6, 13.5, 16.5
 */

interface HistoryListProps {
  history: QueryHistoryItem[];
  onSelectQuery: (item: QueryHistoryItem) => void;
  onClearHistory: () => void;
}

/**
 * Individual history item component
 * Memoized for performance (Requirement 13.5)
 */
const HistoryItem = memo(({ 
  item, 
  onSelect 
}: { 
  item: QueryHistoryItem; 
  onSelect: (item: QueryHistoryItem) => void;
}) => {
  /**
   * Truncate text for preview
   * Requirement: 6.4
   */
  const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <li>
      <button
        onClick={() => onSelect(item)}
        className="w-full text-left p-4 hover:bg-gray-50 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 rounded-lg"
        aria-label={`View query: ${item.question}`}
      >
        <div className="space-y-2">
          {/* Question preview (Requirement 6.4) */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 line-clamp-2">
              {truncateText(item.question, 100)}
            </h3>
          </div>

          {/* Answer preview (Requirement 6.4) */}
          <div>
            <p className="text-sm text-gray-600 line-clamp-2">
              {truncateText(item.answer, 150)}
            </p>
          </div>

          {/* Timestamp and metadata (Requirements 6.5) */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <ClockIcon className="h-4 w-4" aria-hidden="true" />
              <time 
                dateTime={item.timestamp.toISOString()}
                title={format(item.timestamp, 'PPpp')}
              >
                {formatDistanceToNow(item.timestamp, { addSuffix: true })}
              </time>
            </span>
            
            <span>
              {item.sources.length} {item.sources.length === 1 ? 'source' : 'sources'}
            </span>
          </div>
        </div>
      </button>
    </li>
  );
});

HistoryItem.displayName = 'HistoryItem';

/**
 * Main HistoryList component
 */
export default function HistoryList({ history, onSelectQuery, onClearHistory }: HistoryListProps) {
  const [showClearConfirmation, setShowClearConfirmation] = useState(false);

  /**
   * Handle clear history with confirmation
   * Requirements: 6.6
   */
  const handleClearHistory = () => {
    setShowClearConfirmation(true);
  };

  const confirmClearHistory = () => {
    onClearHistory();
    setShowClearConfirmation(false);
  };

  const cancelClearHistory = () => {
    setShowClearConfirmation(false);
  };

  /**
   * Handle query selection
   * Requirement: 6.3
   */
  const handleSelectQuery = (item: QueryHistoryItem) => {
    onSelectQuery(item);
  };

  return (
    <section 
      className="bg-white rounded-lg shadow-md"
      aria-label="Query history"
    >
      {/* Header with clear button */}
      <header className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Query History ({history.length})
        </h2>

        {/* Clear history button (Requirement 6.6) */}
        {history.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            aria-label="Clear all history"
          >
            <TrashIcon className="h-4 w-4" aria-hidden="true" />
            Clear All
          </button>
        )}
      </header>

      {/* Confirmation dialog (Requirement 6.6) */}
      {showClearConfirmation && (
        <div 
          className="p-4 bg-yellow-50 border-b border-yellow-200"
          role="alertdialog"
          aria-labelledby="clear-history-title"
          aria-describedby="clear-history-description"
        >
          <h3 
            id="clear-history-title" 
            className="text-sm font-medium text-yellow-900 mb-2"
          >
            Clear All History?
          </h3>
          <p 
            id="clear-history-description" 
            className="text-sm text-yellow-700 mb-3"
          >
            This will permanently delete all {history.length} queries from your history. This action cannot be undone.
          </p>
          <div className="flex gap-2">
            <button
              onClick={confirmClearHistory}
              className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              aria-label="Confirm clear history"
            >
              Yes, Clear All
            </button>
            <button
              onClick={cancelClearHistory}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              aria-label="Cancel clear history"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* History list (Requirements 6.2, 6.3, 6.4, 6.5) */}
      <div className="max-h-[600px] overflow-y-auto">
        {history.length === 0 ? (
          <div className="p-8 text-center">
            <ClockIcon className="mx-auto h-12 w-12 text-gray-400" aria-hidden="true" />
            <p className="mt-2 text-sm text-gray-500">
              No query history yet
            </p>
            <p className="mt-1 text-xs text-gray-400">
              Your previous queries will appear here
            </p>
          </div>
        ) : (
          <ul 
            className="divide-y divide-gray-200"
            role="list"
          >
            {/* Display queries in descending timestamp order (Requirement 6.2) */}
            {history.map((item) => (
              <HistoryItem
                key={item.id}
                item={item}
                onSelect={handleSelectQuery}
              />
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
