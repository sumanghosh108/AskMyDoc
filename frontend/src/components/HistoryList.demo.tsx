/**
 * HistoryList Component Demo
 * 
 * This file demonstrates how to use the HistoryList component
 * with the queryStore for managing query history.
 */

import { useQueryStore } from '../stores/queryStore';
import HistoryList from './HistoryList';
import AnswerDisplay from './AnswerDisplay';

export default function HistoryListDemo() {
  const { history, currentResult, setCurrentResult, clearHistory } = useQueryStore();

  /**
   * Handle query selection from history
   * Displays the selected query result
   */
  const handleSelectQuery = (item: typeof history[0]) => {
    setCurrentResult(item);
  };

  /**
   * Handle clear history
   * Clears all query history from the store
   */
  const handleClearHistory = () => {
    clearHistory();
  };

  return (
    <div className="container mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* History List */}
        <div>
          <HistoryList
            history={history}
            onSelectQuery={handleSelectQuery}
            onClearHistory={handleClearHistory}
          />
        </div>

        {/* Selected Query Display */}
        <div>
          {currentResult ? (
            <AnswerDisplay
              answer={currentResult.answer}
              sources={currentResult.sources}
              contextChunks={currentResult.contextChunks}
              timestamp={currentResult.timestamp}
            />
          ) : (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <p className="text-gray-500">
                Select a query from history to view details
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
