import { useState, useRef } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { Switch } from '@headlessui/react';
import type { QueryOptions } from '../types';
import { validateQuery, validateTopK, getRemainingCharacters, isNearCharacterLimit, VALIDATION_RULES } from '../utils/validation';

/**
 * QueryInterface Component
 * 
 * Main query input component for submitting questions to the RAG system.
 * 
 * Features:
 * - Textarea for question input with character count
 * - Submit button with loading state
 * - Form validation (empty check, 2000 char limit)
 * - Query options controls (hybrid search, reranker, topK)
 * - Full accessibility support with ARIA labels and keyboard navigation
 * 
 * Requirements: 1.5, 1.6, 1.7, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 9.1, 9.2, 9.3, 15.1, 15.2, 15.6
 */

interface QueryInterfaceProps {
  onSubmit: (question: string, options: QueryOptions) => void;
  isLoading: boolean;
}

export default function QueryInterface({ onSubmit, isLoading }: QueryInterfaceProps) {
  // Form state
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(5); // Default: 5 (Requirement 2.7)
  const [useHybrid, setUseHybrid] = useState(true); // Default: enabled (Requirement 2.5)
  const [useReranker, setUseReranker] = useState(true); // Default: enabled (Requirement 2.6)
  
  // Validation state
  const [validationError, setValidationError] = useState<string | null>(null);
  const [topKError, setTopKError] = useState<string | null>(null);
  
  // Refs for focus management (Requirement 15.6)
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const submitButtonRef = useRef<HTMLButtonElement>(null);

  // Character count calculations
  const remainingChars = getRemainingCharacters(question);
  const nearLimit = isNearCharacterLimit(question);
  const charCountColor = nearLimit ? 'text-orange-600' : 'text-gray-500';

  /**
   * Handle question input change
   * Validates input in real-time (Requirement 9.1, 9.2)
   */
  const handleQuestionChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setQuestion(value);
    
    // Real-time validation
    const validation = validateQuery(value);
    setValidationError(validation.isValid ? null : validation.error || null);
  };

  /**
   * Handle topK input change
   * Validates range in real-time (Requirement 9.3)
   */
  const handleTopKChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    setTopK(value);
    
    // Validate topK range
    if (!isNaN(value)) {
      const validation = validateTopK(value);
      setTopKError(validation.isValid ? null : validation.error || null);
    } else {
      setTopKError('Please enter a valid number');
    }
  };

  /**
   * Handle form submission
   * Validates and submits query (Requirements 1.5, 1.6, 1.7)
   */
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Final validation before submission
    const queryValidation = validateQuery(question);
    if (!queryValidation.isValid) {
      setValidationError(queryValidation.error || 'Invalid query');
      textareaRef.current?.focus();
      return;
    }
    
    const topKValidation = validateTopK(topK);
    if (!topKValidation.isValid) {
      setTopKError(topKValidation.error || 'Invalid topK value');
      return;
    }
    
    // Clear errors and submit
    setValidationError(null);
    setTopKError(null);
    
    const options: QueryOptions = {
      topK,
      useHybrid,
      useReranker,
    };
    
    onSubmit(question.trim(), options);
  };

  /**
   * Check if form can be submitted
   * Requirements: 1.5, 9.1, 9.2, 9.3
   */
  const canSubmit = () => {
    if (isLoading) return false;
    if (!question.trim()) return false;
    if (question.length > VALIDATION_RULES.QUERY_MAX_LENGTH) return false;
    if (topK < VALIDATION_RULES.TOP_K_MIN || topK > VALIDATION_RULES.TOP_K_MAX) return false;
    return true;
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="space-y-6"
      aria-label="Query submission form"
    >
      {/* Question Input Section */}
      <div>
        <label 
          htmlFor="question-input" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Ask a Question
        </label>
        
        <textarea
          ref={textareaRef}
          id="question-input"
          name="question"
          rows={4}
          value={question}
          onChange={handleQuestionChange}
          disabled={isLoading}
          placeholder="Enter your question here..."
          className={`
            block w-full rounded-md shadow-sm
            text-gray-900
            focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            disabled:bg-gray-100 disabled:cursor-not-allowed
            ${validationError ? 'border-red-300' : 'border-gray-300'}
          `}
          aria-label="Question input"
          aria-describedby="char-count validation-error"
          aria-invalid={!!validationError}
          aria-required="true"
        />
        
        {/* Character Count (Requirements 1.6, 9.2) */}
        <div className="mt-2 flex justify-between items-center">
          <span 
            id="char-count" 
            className={`text-sm ${charCountColor}`}
            aria-live="polite"
          >
            {remainingChars} characters remaining
          </span>
          
          {/* Validation Error (Requirement 9.1, 9.2) */}
          {validationError && (
            <span 
              id="validation-error" 
              className="text-sm text-red-600"
              role="alert"
            >
              {validationError}
            </span>
          )}
        </div>
      </div>

      {/* Query Options Section (Requirements 2.1-2.7) */}
      <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700">Query Options</h3>
        
        {/* Hybrid Search Toggle (Requirements 2.1, 2.5) */}
        <div className="flex items-center justify-between">
          <label 
            htmlFor="hybrid-toggle" 
            className="text-sm text-gray-700"
          >
            Hybrid Search
            <span className="ml-2 text-xs text-gray-500">
              (Combines semantic and keyword search)
            </span>
          </label>
          
          <Switch
            id="hybrid-toggle"
            checked={useHybrid}
            onChange={setUseHybrid}
            disabled={isLoading}
            className={`
              ${useHybrid ? 'bg-blue-600' : 'bg-gray-200'}
              relative inline-flex h-6 w-11 items-center rounded-full
              transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            aria-label="Toggle hybrid search"
            aria-checked={useHybrid}
          >
            <span
              className={`
                ${useHybrid ? 'translate-x-6' : 'translate-x-1'}
                inline-block h-4 w-4 transform rounded-full bg-white transition-transform
              `}
            />
          </Switch>
        </div>

        {/* Reranker Toggle (Requirements 2.2, 2.6) */}
        <div className="flex items-center justify-between">
          <label 
            htmlFor="reranker-toggle" 
            className="text-sm text-gray-700"
          >
            Reranker
            <span className="ml-2 text-xs text-gray-500">
              (Improves result relevance)
            </span>
          </label>
          
          <Switch
            id="reranker-toggle"
            checked={useReranker}
            onChange={setUseReranker}
            disabled={isLoading}
            className={`
              ${useReranker ? 'bg-blue-600' : 'bg-gray-200'}
              relative inline-flex h-6 w-11 items-center rounded-full
              transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            aria-label="Toggle reranker"
            aria-checked={useReranker}
          >
            <span
              className={`
                ${useReranker ? 'translate-x-6' : 'translate-x-1'}
                inline-block h-4 w-4 transform rounded-full bg-white transition-transform
              `}
            />
          </Switch>
        </div>

        {/* TopK Input (Requirements 2.3, 2.4, 2.7, 9.3) */}
        <div>
          <label 
            htmlFor="topk-input" 
            className="block text-sm text-gray-700 mb-1"
          >
            Number of Results (topK)
          </label>
          
          <input
            id="topk-input"
            type="number"
            min={VALIDATION_RULES.TOP_K_MIN}
            max={VALIDATION_RULES.TOP_K_MAX}
            value={topK}
            onChange={handleTopKChange}
            disabled={isLoading}
            className={`
              block w-full rounded-md shadow-sm
              text-gray-900
              focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              disabled:bg-gray-100 disabled:cursor-not-allowed
              ${topKError ? 'border-red-300' : 'border-gray-300'}
            `}
            aria-label="Number of results to retrieve"
            aria-describedby="topk-help topk-error"
            aria-invalid={!!topKError}
            aria-valuemin={VALIDATION_RULES.TOP_K_MIN}
            aria-valuemax={VALIDATION_RULES.TOP_K_MAX}
            aria-valuenow={topK}
          />
          
          <div className="mt-1 flex justify-between items-center">
            <span 
              id="topk-help" 
              className="text-xs text-gray-500"
            >
              Range: {VALIDATION_RULES.TOP_K_MIN}-{VALIDATION_RULES.TOP_K_MAX}
            </span>
            
            {topKError && (
              <span 
                id="topk-error" 
                className="text-xs text-red-600"
                role="alert"
              >
                {topKError}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Submit Button (Requirements 1.7, 15.2) */}
      <div>
        <button
          ref={submitButtonRef}
          type="submit"
          disabled={!canSubmit()}
          className={`
            w-full flex justify-center items-center
            px-4 py-2 border border-transparent rounded-md shadow-sm
            text-sm font-medium text-white
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            ${
              canSubmit()
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-300 cursor-not-allowed'
            }
            transition-colors duration-200
          `}
          aria-label={isLoading ? 'Submitting query' : 'Submit query'}
          aria-busy={isLoading}
        >
          {isLoading ? (
            <>
              <svg 
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle 
                  className="opacity-25" 
                  cx="12" 
                  cy="12" 
                  r="10" 
                  stroke="currentColor" 
                  strokeWidth="4"
                />
                <path 
                  className="opacity-75" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Processing...
            </>
          ) : (
            'Submit Query'
          )}
        </button>
      </div>
    </form>
  );
}
