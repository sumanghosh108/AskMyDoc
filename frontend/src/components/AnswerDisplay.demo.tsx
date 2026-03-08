/**
 * AnswerDisplay Component Demo
 * 
 * This file demonstrates how to use the AnswerDisplay component
 * with sample data for testing and development purposes.
 */

import AnswerDisplay from './AnswerDisplay';
import type { SourceMeta } from '../types';

// Sample data for demonstration
const sampleAnswer = `# Machine Learning Overview

Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## Key Concepts

- **Supervised Learning**: Training with labeled data
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error

Machine learning algorithms can be applied to various domains including:

1. Natural Language Processing
2. Computer Vision
3. Recommendation Systems
4. Predictive Analytics

\`\`\`python
# Simple example
model.fit(X_train, y_train)
predictions = model.predict(X_test)
\`\`\`

The field continues to evolve with advances in deep learning and neural networks.`;

const sampleSources: SourceMeta[] = [
  {
    source: 'Introduction_to_ML.pdf',
    page: 15,
    relevanceScore: 0.92,
    rerankerScore: 0.88,
  },
  {
    source: 'Deep_Learning_Fundamentals.pdf',
    page: 3,
    relevanceScore: 0.85,
    rerankerScore: 0.91,
  },
  {
    source: 'AI_Handbook.md',
    relevanceScore: 0.78,
    rerankerScore: 0.82,
  },
  {
    source: 'neural_networks_guide.txt',
    page: 42,
    relevanceScore: 0.71,
  },
];

export default function AnswerDisplayDemo() {
  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        AnswerDisplay Component Demo
      </h1>
      
      <AnswerDisplay
        answer={sampleAnswer}
        sources={sampleSources}
        contextChunks={4}
        timestamp={new Date()}
      />

      {/* Demo with minimal data */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Minimal Example
        </h2>
        <AnswerDisplay
          answer="This is a simple answer without markdown formatting."
          sources={[
            {
              source: 'simple_doc.txt',
              relevanceScore: 0.95,
            },
          ]}
          contextChunks={1}
          timestamp={new Date(Date.now() - 1000 * 60 * 5)} // 5 minutes ago
        />
      </div>

      {/* Demo with no sources */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          No Sources Example
        </h2>
        <AnswerDisplay
          answer="This answer has no associated sources."
          sources={[]}
          contextChunks={0}
          timestamp={new Date(Date.now() - 1000 * 60 * 60)} // 1 hour ago
        />
      </div>
    </div>
  );
}
