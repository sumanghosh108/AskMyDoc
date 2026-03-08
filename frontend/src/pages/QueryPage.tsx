import { QueryInterface, AnswerDisplay, HistoryList } from '@/components';
import { useQueryStore } from '@/stores';
import { submitQuery } from '@/services';
import toast from 'react-hot-toast';
import type { QueryOptions, QueryHistoryItem } from '@/types';

export default function QueryPage() {
  const { isLoading, currentResult, error, history, setLoading, setCurrentResult, setError, addToHistory, clearHistory } = useQueryStore();

  const handleSubmit = async (question: string, options: QueryOptions) => {
    setLoading(true);
    
    try {
      const result = await submitQuery({
        question,
        topK: options.topK,
        useHybrid: options.useHybrid,
        useReranker: options.useReranker,
      });
      
      setCurrentResult({
        id: Date.now().toString(),
        question,
        answer: result.answer,
        sources: result.sources,
        timestamp: new Date(),
        contextChunks: result.contextChunks,
      });
      
      addToHistory({
        id: Date.now().toString(),
        question,
        answer: result.answer,
        timestamp: new Date(),
        sources: result.sources,
        contextChunks: result.contextChunks,
      });
      
      toast.success('Query completed successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit query';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const handleSelectQuery = (item: QueryHistoryItem) => {
    setCurrentResult(item);
  };

  const handleClearHistory = () => {
    clearHistory();
    toast.success('History cleared');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Query Area */}
      <div className="lg:col-span-2 space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Ask a Question</h2>
          <QueryInterface onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {/* Answer Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        
        {currentResult && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Answer</h2>
            <AnswerDisplay 
              answer={currentResult.answer}
              sources={currentResult.sources}
              contextChunks={currentResult.contextChunks}
              timestamp={currentResult.timestamp}
            />
          </div>
        )}
      </div>

      {/* History Sidebar */}
      <div className="lg:col-span-1">
        <div className="bg-white rounded-lg shadow-sm p-6 sticky top-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Query History</h2>
          <HistoryList 
            history={history}
            onSelectQuery={handleSelectQuery}
            onClearHistory={handleClearHistory}
          />
        </div>
      </div>
    </div>
  );
}
