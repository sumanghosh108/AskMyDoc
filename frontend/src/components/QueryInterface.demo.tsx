/**
 * QueryInterface Component Demo
 * 
 * This file demonstrates the QueryInterface component functionality.
 * It can be imported into App.tsx for visual testing.
 */

import { useState } from 'react';
import QueryInterface from './QueryInterface';
import type { QueryOptions } from '../types';

export default function QueryInterfaceDemo() {
  const [isLoading, setIsLoading] = useState(false);
  const [lastSubmission, setLastSubmission] = useState<{
    question: string;
    options: QueryOptions;
  } | null>(null);

  const handleSubmit = (question: string, options: QueryOptions) => {
    console.log('Query submitted:', { question, options });
    
    // Simulate loading state
    setIsLoading(true);
    setLastSubmission({ question, options });
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      console.log('Query completed');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            QueryInterface Component Demo
          </h1>
          
          <QueryInterface 
            onSubmit={handleSubmit}
            isLoading={isLoading}
          />
          
          {lastSubmission && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h2 className="text-lg font-semibold text-blue-900 mb-2">
                Last Submission:
              </h2>
              <div className="space-y-2 text-sm">
                <p><strong>Question:</strong> {lastSubmission.question}</p>
                <p><strong>TopK:</strong> {lastSubmission.options.topK}</p>
                <p><strong>Hybrid Search:</strong> {lastSubmission.options.useHybrid ? 'Enabled' : 'Disabled'}</p>
                <p><strong>Reranker:</strong> {lastSubmission.options.useReranker ? 'Enabled' : 'Disabled'}</p>
              </div>
            </div>
          )}
        </div>
        
        <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Component Features Implemented:
          </h2>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>✅ Task 6.1: Component structure with textarea and submit button</li>
            <li>✅ Task 6.1: Character count display (2000 char limit)</li>
            <li>✅ Task 6.1: Form validation (empty check, length limit)</li>
            <li>✅ Task 6.1: Loading state with spinner</li>
            <li>✅ Task 6.2: Hybrid search toggle (default enabled)</li>
            <li>✅ Task 6.2: Reranker toggle (default enabled)</li>
            <li>✅ Task 6.2: TopK number input (1-20, default 5)</li>
            <li>✅ Task 6.2: TopK range validation</li>
            <li>✅ Task 6.3: ARIA labels on all interactive elements</li>
            <li>✅ Task 6.3: Keyboard navigation support</li>
            <li>✅ Task 6.3: Focus management with refs</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
