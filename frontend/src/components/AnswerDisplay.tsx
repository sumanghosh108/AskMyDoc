import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import DOMPurify from 'dompurify';
import { formatDistanceToNow } from 'date-fns';
import { ClipboardDocumentIcon, CheckIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import type { SourceMeta } from '../types';

/**
 * AnswerDisplay Component
 * 
 * Displays generated answers with citations and source references.
 * 
 * Features:
 * - Renders formatted answer text with markdown support
 * - Sanitizes markdown with DOMPurify for XSS protection
 * - Displays source citations with relevance scores
 * - Shows expandable source details
 * - Provides copy-to-clipboard functionality
 * - Displays timestamp and context chunk count
 * - Full accessibility support with semantic HTML
 * 
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 14.2, 15.4, 18.3
 */

interface AnswerDisplayProps {
  answer: string;
  sources: SourceMeta[];
  contextChunks: number;
  timestamp: Date;
}

export default function AnswerDisplay({ answer, sources, contextChunks, timestamp }: AnswerDisplayProps) {
  const [copiedToClipboard, setCopiedToClipboard] = useState(false);
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

  /**
   * Handle copy to clipboard
   * Requirements: 3.4, 18.3
   */
  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(answer);
      setCopiedToClipboard(true);
      
      // Reset after 2 seconds
      setTimeout(() => {
        setCopiedToClipboard(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  /**
   * Toggle source expansion
   * Requirement: 3.3
   */
  const toggleSourceExpansion = (index: number) => {
    setExpandedSources((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  /**
   * Sanitize markdown content
   * Requirements: 14.2
   */
  const sanitizeMarkdown = (content: string): string => {
    return DOMPurify.sanitize(content, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'a'],
      ALLOWED_ATTR: ['href', 'target', 'rel'],
    });
  };

  /**
   * Format relevance score as percentage
   */
  const formatScore = (score?: number): string => {
    if (score === undefined) return 'N/A';
    return `${(score * 100).toFixed(1)}%`;
  };

  return (
    <article 
      className="space-y-6"
      aria-label="Query answer and sources"
      data-testid="answer-display"
    >
      {/* Answer Section */}
      <section className="bg-white rounded-lg shadow-md p-6">
        {/* Header with metadata and copy button */}
        <header className="flex justify-between items-start mb-4 pb-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">
              Answer
            </h2>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              {/* Timestamp (Requirement 3.6) */}
              <time dateTime={timestamp.toISOString()}>
                {formatDistanceToNow(timestamp, { addSuffix: true })}
              </time>
              
              {/* Context chunks count (Requirement 3.5) */}
              <span aria-label={`Used ${contextChunks} context chunks`}>
                {contextChunks} context {contextChunks === 1 ? 'chunk' : 'chunks'}
              </span>
            </div>
          </div>

          {/* Copy to clipboard button (Requirements 3.4, 18.3) */}
          <button
            onClick={handleCopyToClipboard}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium
              transition-colors duration-200
              focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
              ${
                copiedToClipboard
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
            aria-label={copiedToClipboard ? 'Copied to clipboard' : 'Copy answer to clipboard'}
          >
            {copiedToClipboard ? (
              <>
                <CheckIcon className="h-5 w-5" aria-hidden="true" />
                Copied!
              </>
            ) : (
              <>
                <ClipboardDocumentIcon className="h-5 w-5" aria-hidden="true" />
                Copy
              </>
            )}
          </button>
        </header>

        {/* Answer text with markdown rendering (Requirements 3.1, 14.2) */}
        <div 
          className="prose prose-sm max-w-none"
          data-testid="answer-text"
        >
          <ReactMarkdown
            components={{
              // Custom rendering to sanitize content
              p: ({ children }) => (
                <p dangerouslySetInnerHTML={{ __html: sanitizeMarkdown(String(children)) }} />
              ),
              code: ({ children }) => (
                <code className="bg-gray-100 px-1 py-0.5 rounded text-sm">
                  {children}
                </code>
              ),
              pre: ({ children }) => (
                <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto">
                  {children}
                </pre>
              ),
            }}
          >
            {answer}
          </ReactMarkdown>
        </div>
      </section>

      {/* Sources Section (Requirements 3.2, 3.3, 3.7) */}
      <section className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Sources ({sources.length})
        </h2>

        {sources.length === 0 ? (
          <p className="text-gray-500 text-sm">No sources available</p>
        ) : (
          <ul className="space-y-3" role="list">
            {sources.map((source, index) => {
              const isExpanded = expandedSources.has(index);
              
              return (
                <li 
                  key={index}
                  className="border border-gray-200 rounded-lg overflow-hidden"
                  data-testid="source-item"
                >
                  {/* Source header - clickable to expand (Requirement 3.3) */}
                  <button
                    onClick={() => toggleSourceExpansion(index)}
                    className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                    aria-expanded={isExpanded}
                    aria-controls={`source-details-${index}`}
                  >
                    <div className="flex-1 min-w-0">
                      {/* Source name and page number (Requirements 3.2, 3.7) */}
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {source.source}
                        {source.page !== undefined && (
                          <span className="ml-2 text-gray-500">
                            (Page {source.page})
                          </span>
                        )}
                      </h3>
                      
                      {/* Relevance score (Requirement 3.2) */}
                      <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                        {source.relevanceScore !== undefined && (
                          <span>
                            Relevance: {formatScore(source.relevanceScore)}
                          </span>
                        )}
                        
                        {/* Reranker score if present (Requirement 3.7) */}
                        {source.rerankerScore !== undefined && (
                          <span>
                            Reranker: {formatScore(source.rerankerScore)}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Expand/collapse icon */}
                    {isExpanded ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" aria-hidden="true" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" aria-hidden="true" />
                    )}
                  </button>

                  {/* Expandable source details (Requirement 3.3) */}
                  {isExpanded && (
                    <div 
                      id={`source-details-${index}`}
                      className="px-4 pb-4 bg-gray-50 border-t border-gray-200"
                    >
                      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                        <div>
                          <dt className="font-medium text-gray-700">Source:</dt>
                          <dd className="text-gray-900 break-words">{source.source}</dd>
                        </div>
                        
                        {source.page !== undefined && (
                          <div>
                            <dt className="font-medium text-gray-700">Page:</dt>
                            <dd className="text-gray-900">{source.page}</dd>
                          </div>
                        )}
                        
                        {source.relevanceScore !== undefined && (
                          <div>
                            <dt className="font-medium text-gray-700">Relevance Score:</dt>
                            <dd className="text-gray-900">{formatScore(source.relevanceScore)}</dd>
                          </div>
                        )}
                        
                        {source.rerankerScore !== undefined && (
                          <div>
                            <dt className="font-medium text-gray-700">Reranker Score:</dt>
                            <dd className="text-gray-900">{formatScore(source.rerankerScore)}</dd>
                          </div>
                        )}
                      </dl>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </article>
  );
}
