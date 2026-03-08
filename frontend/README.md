# RAG System Frontend

Production-grade React frontend for the RAG (Retrieval-Augmented Generation) system.

## Features

- **Query Interface**: Submit questions with configurable options (hybrid search, reranker, topK)
- **Answer Display**: View answers with markdown rendering, source citations, and relevance scores
- **Document Upload**: Upload PDF, Markdown, and text files with drag-and-drop support
- **Query History**: Browse and revisit previous queries with localStorage persistence
- **System Metrics**: Monitor performance metrics and cache statistics
- **Health Monitoring**: Real-time backend health status with auto-check
- **Responsive Design**: Mobile-friendly interface with TailwindCSS
- **Accessibility**: WCAG 2.1 compliant with ARIA labels and keyboard navigation

## Tech Stack

- **React 19.2** - UI framework
- **TypeScript 5.9** - Type safety
- **Vite 8.0** - Build tool and dev server
- **TailwindCSS 4.2** - Styling
- **Zustand** - State management
- **Axios** - HTTP client
- **React Router** - Client-side routing
- **React Hot Toast** - Notifications
- **React Markdown** - Markdown rendering
- **DOMPurify** - XSS protection
- **Vitest** - Unit testing

## Prerequisites

- Node.js 18+ and npm
- Backend API running at `http://localhost:8000` (configurable)

## Installation

```bash
# Install dependencies
npm install
```

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=60000
```

See `.env.example` for all available variables.

## Development

```bash
# Start development server (http://localhost:5173)
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Type check
npm run type-check

# Lint
npm run lint
```

## Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

The build output will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   │   ├── QueryInterface.tsx
│   │   ├── AnswerDisplay.tsx
│   │   ├── DocumentUpload.tsx
│   │   ├── HistoryList.tsx
│   │   ├── MetricsPanel.tsx
│   │   ├── HealthIndicator.tsx
│   │   └── Layout.tsx
│   ├── pages/          # Page components
│   │   ├── QueryPage.tsx
│   │   ├── UploadPage.tsx
│   │   └── MetricsPage.tsx
│   ├── stores/         # Zustand state stores
│   │   ├── queryStore.ts
│   │   ├── uploadStore.ts
│   │   └── systemStore.ts
│   ├── services/       # API services
│   │   ├── apiClient.ts
│   │   ├── queryService.ts
│   │   ├── ingestService.ts
│   │   ├── metricsService.ts
│   │   └── healthService.ts
│   ├── types/          # TypeScript types
│   │   ├── query.types.ts
│   │   ├── ingest.types.ts
│   │   └── system.types.ts
│   ├── utils/          # Utility functions
│   │   ├── validation.ts
│   │   ├── formatters.ts
│   │   └── helpers.ts
│   ├── App.tsx         # Root component with routing
│   └── main.tsx        # Application entry point
├── public/             # Static assets
├── dist/               # Production build output
└── package.json        # Dependencies and scripts
```

## Usage

### Query Page

1. Navigate to the home page (`/`)
2. Enter your question in the text area
3. Configure options:
   - **Hybrid Search**: Combine keyword and semantic search (default: enabled)
   - **Reranker**: Re-rank results for better relevance (default: enabled)
   - **Top K**: Number of results to retrieve (1-20, default: 5)
4. Click "Submit Query"
5. View the answer with source citations
6. Browse query history in the sidebar

### Upload Page

1. Navigate to `/upload`
2. Drag and drop files or click to select
3. Supported formats: PDF, Markdown (.md), Text (.txt)
4. Maximum file size: 10 MB per file
5. Monitor upload progress for each file
6. Files are automatically indexed in the knowledge base

### Metrics Page

1. Navigate to `/metrics`
2. View system performance metrics:
   - Total queries processed
   - Average latency
   - Cache hit rate
   - Document count
3. View detailed cache statistics (if Redis is enabled)
4. Click "Refresh" to update metrics manually
5. Metrics auto-refresh every 30 seconds

## API Integration

The frontend communicates with the backend API at the configured base URL:

- `POST /api/v1/query` - Submit queries
- `POST /api/v1/ingest` - Upload documents
- `GET /api/v1/metrics` - Fetch system metrics
- `GET /health` - Check backend health

## State Management

The application uses Zustand for state management with three stores:

- **queryStore**: Query state, results, error, and history (persisted to localStorage)
- **uploadStore**: Upload state and progress tracking
- **systemStore**: System metrics and health status

## Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test validation.test.ts
```

Test files are located next to their source files with `.test.ts` extension.

## Accessibility

The application follows WCAG 2.1 Level AA guidelines:

- Semantic HTML structure
- ARIA labels and live regions
- Keyboard navigation support
- Focus management
- Color contrast compliance
- Screen reader compatibility

## Security

- Input sanitization with DOMPurify
- XSS protection for markdown content
- File type and size validation
- Environment variable validation
- No sensitive data in logs
- HTTPS recommended for production

## Performance

- React.memo for expensive components
- Lazy loading with code splitting
- Optimized bundle size (< 200KB gzipped)
- Debounced inputs
- Virtual scrolling for long lists
- Efficient state updates

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Backend Connection Issues

If you see "Network error - unable to reach server":

1. Verify the backend is running at `http://localhost:8000`
2. Check the `VITE_API_BASE_URL` in `.env.local`
3. Ensure CORS is configured on the backend
4. Check browser console for detailed errors

### Build Errors

If TypeScript compilation fails:

1. Run `npm run type-check` to see all errors
2. Ensure all dependencies are installed: `npm install`
3. Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### Test Failures

If tests fail:

1. Ensure all dependencies are installed
2. Check for TypeScript errors: `npm run type-check`
3. Run tests in watch mode for debugging: `npm run test:watch`

## License

MIT
