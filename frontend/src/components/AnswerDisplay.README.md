# AnswerDisplay Component

## Overview

The `AnswerDisplay` component is responsible for displaying generated answers from the RAG system along with source citations and metadata. It provides a rich, accessible interface for viewing query results with markdown formatting, expandable source details, and copy-to-clipboard functionality.

## Features

### Task 7.1: Component Structure ✅
- Renders answer text with react-markdown for rich formatting
- Sanitizes markdown content with DOMPurify to prevent XSS attacks
- Displays query timestamp (relative time format)
- Shows context chunk count used in the answer

### Task 7.2: Source Citations Display ✅
- Lists all sources with relevance scores
- Shows page numbers when available
- Provides expandable details for each source
- Displays reranker scores if present
- Formats scores as percentages for readability

### Task 7.3: Copy-to-Clipboard Functionality ✅
- Copy button for answer text
- Visual feedback with success notification
- Automatic reset after 2 seconds
- Accessible button states

### Task 7.4: Accessibility Features ✅
- Semantic HTML structure (article, section, header, time)
- Proper heading hierarchy (h2 for main sections, h3 for source names)
- ARIA labels and attributes for screen readers
- Keyboard navigation support
- Focus management with visible focus indicators

## Props

```typescript
interface AnswerDisplayProps {
  answer: string;           // The generated answer text (supports markdown)
  sources: SourceMeta[];    // Array of source citations
  contextChunks: number;    // Number of context chunks used
  timestamp: Date;          // When the query was executed
}

interface SourceMeta {
  source: string;           // Source document name
  page?: number;            // Optional page number
  relevanceScore?: number;  // Optional relevance score (0-1)
  rerankerScore?: number;   // Optional reranker score (0-1)
}
```

## Usage

### Basic Usage

```typescript
import { AnswerDisplay } from '@/components';

function QueryResults() {
  const { currentResult } = useQueryStore();
  
  if (!currentResult) return null;
  
  return (
    <AnswerDisplay
      answer={currentResult.answer}
      sources={currentResult.sources}
      contextChunks={currentResult.contextChunks}
      timestamp={currentResult.timestamp}
    />
  );
}
```

### With Sample Data

```typescript
import { AnswerDisplay } from '@/components';

function Demo() {
  return (
    <AnswerDisplay
      answer="Machine learning is a subset of AI..."
      sources={[
        {
          source: 'ML_Guide.pdf',
          page: 15,
          relevanceScore: 0.92,
          rerankerScore: 0.88,
        },
      ]}
      contextChunks={3}
      timestamp={new Date()}
    />
  );
}
```

## Component Structure

```
AnswerDisplay
├── Answer Section
│   ├── Header
│   │   ├── Title
│   │   ├── Metadata (timestamp, context chunks)
│   │   └── Copy Button
│   └── Answer Text (markdown rendered)
└── Sources Section
    ├── Title with count
    └── Source List
        └── Source Item (expandable)
            ├── Source Header (clickable)
            │   ├── Source name + page
            │   ├── Scores (relevance, reranker)
            │   └── Expand/collapse icon
            └── Source Details (when expanded)
                └── Detailed information grid
```

## Styling

The component uses TailwindCSS for styling with the following design patterns:

- **Cards**: White background with rounded corners and shadow
- **Typography**: Prose classes for markdown content
- **Interactive Elements**: Hover states and focus rings
- **Responsive**: Adapts to different screen sizes
- **Color Scheme**: Gray scale with blue accents for interactive elements

## Accessibility

### ARIA Attributes
- `aria-label`: Descriptive labels for sections and buttons
- `aria-expanded`: Indicates expansion state of sources
- `aria-controls`: Links buttons to controlled elements
- `role="list"`: Semantic list structure

### Keyboard Navigation
- Tab navigation through all interactive elements
- Enter/Space to expand/collapse sources
- Enter/Space to copy to clipboard
- Visible focus indicators on all interactive elements

### Screen Reader Support
- Semantic HTML elements (article, section, header, time)
- Proper heading hierarchy
- Descriptive button labels
- Time elements with ISO datetime attributes

## Security

### XSS Prevention
The component uses DOMPurify to sanitize markdown content before rendering:

```typescript
const sanitizeMarkdown = (content: string): string => {
  return DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
};
```

This prevents malicious scripts from being executed while allowing safe markdown formatting.

## Requirements Mapping

| Requirement | Description | Status |
|-------------|-------------|--------|
| 3.1 | Render answer text with markdown formatting | ✅ |
| 3.2 | Display source citations with relevance scores | ✅ |
| 3.3 | Expandable source details | ✅ |
| 3.4 | Copy-to-clipboard functionality | ✅ |
| 3.5 | Display context chunk count | ✅ |
| 3.6 | Display query timestamp | ✅ |
| 3.7 | Show page numbers and reranker scores | ✅ |
| 14.2 | Sanitize markdown with DOMPurify | ✅ |
| 15.4 | Semantic HTML structure | ✅ |
| 18.3 | Success notification on copy | ✅ |

## Testing

### Manual Testing
Run the demo file to see the component in action:

```typescript
import AnswerDisplayDemo from './AnswerDisplay.demo';

// Render the demo component to see various examples
```

### Unit Tests (Task 7.5 - Optional)
Recommended test cases:
- Markdown rendering with various formatting
- Source citation display with different score combinations
- Copy-to-clipboard functionality
- Expandable source details interaction
- Empty sources handling
- Timestamp formatting

## Dependencies

- `react`: Core React library
- `react-markdown`: Markdown rendering
- `dompurify`: XSS protection
- `date-fns`: Date formatting
- `@heroicons/react`: Icons (clipboard, check, chevron)
- `@/types`: TypeScript type definitions

## Performance Considerations

- Uses `useState` for local component state (expanded sources, copy status)
- Minimal re-renders due to isolated state management
- Efficient source expansion with Set data structure
- Sanitization only on render, not on every interaction

## Future Enhancements

Potential improvements for future iterations:
- Syntax highlighting for code blocks
- Source preview/excerpt display
- Link to source documents
- Export answer as PDF/markdown
- Share functionality
- Answer rating/feedback
- Highlight search terms in answer
