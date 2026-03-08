# AnswerDisplay Component Structure

## Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│ AnswerDisplay Component                                      │
│ <article>                                                    │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Answer Section <section>                               │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ Header <header>                                  │  │ │
│  │  │                                                   │  │ │
│  │  │  Answer                        [📋 Copy Button]  │  │ │
│  │  │  5 minutes ago • 3 context chunks               │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ Answer Text <div.prose>                          │  │ │
│  │  │                                                   │  │ │
│  │  │  # Markdown Heading                              │  │ │
│  │  │                                                   │  │ │
│  │  │  This is the **formatted** answer text with      │  │ │
│  │  │  *markdown* support.                             │  │ │
│  │  │                                                   │  │ │
│  │  │  - Bullet points                                 │  │ │
│  │  │  - Code blocks                                   │  │ │
│  │  │  - And more...                                   │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Sources Section <section>                              │ │
│  │                                                         │ │
│  │  Sources (4)                                           │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ ▼ ML_Guide.pdf (Page 15)                    [▼] │  │ │
│  │  │   Relevance: 92.0% • Reranker: 88.0%            │  │ │
│  │  │                                                   │  │ │
│  │  │  ┌─────────────────────────────────────────────┐ │  │ │
│  │  │  │ Expanded Details                            │ │  │ │
│  │  │  │                                              │ │  │ │
│  │  │  │ Source:          ML_Guide.pdf               │ │  │ │
│  │  │  │ Page:            15                          │ │  │ │
│  │  │  │ Relevance Score: 92.0%                      │ │  │ │
│  │  │  │ Reranker Score:  88.0%                      │ │  │ │
│  │  │  └─────────────────────────────────────────────┘ │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ ▶ Deep_Learning.pdf (Page 3)                [▶] │  │ │
│  │  │   Relevance: 85.0% • Reranker: 91.0%            │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ ▶ AI_Handbook.md                            [▶] │  │ │
│  │  │   Relevance: 78.0% • Reranker: 82.0%            │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ ▶ neural_networks.txt (Page 42)             [▶] │  │ │
│  │  │   Relevance: 71.0%                               │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Tree

```
AnswerDisplay
├── <article> (main container)
│   ├── aria-label="Query answer and sources"
│   └── data-testid="answer-display"
│
├── Answer Section
│   ├── <section> (answer container)
│   │   ├── <header> (metadata and actions)
│   │   │   ├── <div> (metadata)
│   │   │   │   ├── <h2> "Answer"
│   │   │   │   └── <div> (timestamp + chunks)
│   │   │   │       ├── <time> (relative timestamp)
│   │   │   │       └── <span> (context chunks)
│   │   │   └── <button> (copy to clipboard)
│   │   │       ├── ClipboardDocumentIcon / CheckIcon
│   │   │       └── "Copy" / "Copied!"
│   │   └── <div.prose> (answer text)
│   │       └── <ReactMarkdown> (sanitized content)
│
└── Sources Section
    └── <section> (sources container)
        ├── <h2> "Sources (count)"
        └── <ul> (sources list)
            └── <li> (for each source)
                ├── <button> (source header - clickable)
                │   ├── <div> (source info)
                │   │   ├── <h3> (source name + page)
                │   │   └── <div> (scores)
                │   │       ├── <span> (relevance score)
                │   │       └── <span> (reranker score)
                │   └── ChevronUpIcon / ChevronDownIcon
                └── <div> (expandable details)
                    └── <dl> (details grid)
                        ├── <dt> + <dd> (Source)
                        ├── <dt> + <dd> (Page)
                        ├── <dt> + <dd> (Relevance Score)
                        └── <dt> + <dd> (Reranker Score)
```

## State Management

```typescript
// Local component state
const [copiedToClipboard, setCopiedToClipboard] = useState(false);
const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

// State transitions
Copy Button Click → copiedToClipboard = true → (2s delay) → copiedToClipboard = false
Source Click → Toggle index in expandedSources Set
```

## Data Flow

```
Props (from parent)
    ↓
┌─────────────────────┐
│  AnswerDisplay      │
│                     │
│  answer: string     │ → Sanitize → ReactMarkdown → Rendered HTML
│  sources: []        │ → Map → Source Items → Expandable Details
│  contextChunks: n   │ → Display in header
│  timestamp: Date    │ → Format → Display relative time
└─────────────────────┘
    ↓
User Interactions
    ↓
┌─────────────────────┐
│  Local State        │
│                     │
│  copiedToClipboard  │ → Update button appearance
│  expandedSources    │ → Show/hide source details
└─────────────────────┘
```

## Styling Classes

### Container Classes
- `space-y-6` - Vertical spacing between sections
- `bg-white` - White background for cards
- `rounded-lg` - Rounded corners
- `shadow-md` - Medium shadow for depth
- `p-6` - Padding inside cards

### Typography Classes
- `text-lg font-semibold` - Section headings
- `text-sm text-gray-500` - Metadata text
- `prose prose-sm max-w-none` - Markdown content styling

### Interactive Classes
- `hover:bg-gray-50` - Hover state for clickable items
- `focus:outline-none focus:ring-2` - Focus indicators
- `transition-colors duration-200` - Smooth transitions
- `disabled:opacity-50` - Disabled state styling

### Color Scheme
- Primary: Blue (`bg-blue-600`, `text-blue-700`)
- Success: Green (`bg-green-100`, `text-green-700`)
- Neutral: Gray scale (`gray-50` to `gray-900`)
- Borders: `border-gray-200`

## Accessibility Features

### Semantic HTML
```html
<article aria-label="Query answer and sources">
  <section> <!-- Answer -->
    <header>
      <h2>Answer</h2>
      <time datetime="2024-01-15T10:30:00Z">5 minutes ago</time>
    </header>
  </section>
  
  <section> <!-- Sources -->
    <h2>Sources (4)</h2>
    <ul role="list">
      <li>
        <button aria-expanded="true" aria-controls="source-details-0">
          <h3>Source Name</h3>
        </button>
        <div id="source-details-0">
          <dl>
            <dt>Source:</dt>
            <dd>ML_Guide.pdf</dd>
          </dl>
        </div>
      </li>
    </ul>
  </section>
</article>
```

### Keyboard Navigation
- Tab: Navigate between interactive elements
- Enter/Space: Activate buttons (copy, expand/collapse)
- Focus indicators visible on all interactive elements

### Screen Reader Support
- Descriptive ARIA labels
- Semantic HTML elements
- Proper heading hierarchy
- Time elements with ISO datetime
- List structure for sources

## Security Implementation

### DOMPurify Configuration
```typescript
DOMPurify.sanitize(content, {
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'em', 'u',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'code', 'pre', 'blockquote',
    'a'
  ],
  ALLOWED_ATTR: ['href', 'target', 'rel']
});
```

### XSS Prevention
- All user-generated content sanitized
- Markdown rendered through react-markdown
- Custom components for safe rendering
- No dangerouslySetInnerHTML without sanitization

## Performance Considerations

### Efficient State Management
- Set data structure for O(1) expansion checks
- Minimal re-renders with isolated state
- No unnecessary prop drilling

### Optimizations
- Sanitization only on render
- Efficient source mapping
- No heavy computations in render
- Clean component structure

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Clipboard API support required
- CSS Grid support required
- ES6+ JavaScript features
