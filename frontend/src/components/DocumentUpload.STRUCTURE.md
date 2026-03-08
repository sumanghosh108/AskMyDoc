# DocumentUpload Component Structure

## Component Architecture

```
DocumentUpload
├── Drag-and-Drop Zone
│   ├── Visual feedback (hover states)
│   ├── Drop handlers
│   └── Click to upload
├── File Input (hidden)
├── Validation Error Display
│   └── List of invalid files with errors
└── Upload Progress Display
    └── Progress items (per file)
        ├── File name
        ├── Progress bar
        ├── Percentage
        └── Status icon
```

## State Management

### Local State (useState)
- `isDragging`: Boolean tracking drag-over state
- `validationErrors`: Array of files that failed validation

### Global State (Zustand)
- `progress`: Array of UploadProgress objects from upload store
- `isUploading`: Boolean from upload store (via props)

## Event Handlers

### Drag-and-Drop Events
1. `handleDragEnter`: Sets isDragging to true
2. `handleDragLeave`: Sets isDragging to false
3. `handleDragOver`: Prevents default to allow drop
4. `handleDrop`: Processes dropped files

### File Selection Events
1. `handleFileSelect`: Processes files from file input
2. `handleButtonClick`: Triggers file input click
3. `handleKeyDown`: Keyboard support (Enter/Space)

### File Processing
1. `handleFiles`: Main file processing logic
   - Validates files using `validateFiles` utility
   - Separates valid and invalid files
   - Updates validation errors
   - Calls `onUpload` callback with valid files

## File Validation Flow

```
Files Selected
    ↓
validateFiles(files)
    ↓
Split into valid/invalid
    ↓
Display errors for invalid files
    ↓
Call onUpload(validFiles)
```

## Upload Progress Flow

```
onUpload called
    ↓
Initialize progress in store
    ↓
Upload files via ingestService
    ↓
Update progress via callbacks
    ↓
Display progress bars
    ↓
Show success/error status
```

## Accessibility Features

### ARIA Attributes
- `role="button"` on drop zone
- `tabIndex={0}` for keyboard focus
- `aria-label` on interactive elements
- `aria-live="polite"` on status regions
- `role="progressbar"` with aria-valuenow/min/max
- `role="alert"` on error messages

### Screen Reader Support
- Hidden text with `sr-only` class for status announcements
- Announces upload progress changes
- Announces success/error states
- Proper semantic HTML structure

### Keyboard Support
- Tab navigation to drop zone
- Enter/Space to open file picker
- Focus management

## Styling Classes

### Drop Zone States
- Default: `border-gray-300 hover:border-gray-400 hover:bg-gray-50`
- Dragging: `border-blue-500 bg-blue-50`
- Uploading: `opacity-50 cursor-not-allowed`

### Progress Bar Colors
- Uploading: `bg-blue-500`
- Success: `bg-green-500`
- Error: `bg-red-500`

### Status Icons
- Success: Green CheckCircleIcon
- Error: Red XCircleIcon

## Integration Points

### Required Props
- `onUpload`: Callback function to handle valid files
- `isUploading`: Boolean to disable during upload

### Optional Props
- `acceptedTypes`: Array of file extensions (default: ['.pdf', '.md', '.txt'])
- `maxSize`: Maximum file size in bytes (default: 10MB)

### Dependencies
- `validateFiles` from `utils/validation.ts`
- `useUploadStore` from `stores/uploadStore.ts`
- `UploadProgress` type from `types/ingest.types.ts`
- Heroicons for icons
- TailwindCSS for styling

## Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| 4.1 | Drag-and-drop zone with event handlers |
| 4.2 | File selection button and hidden input |
| 4.3 | File type validation via validateFiles |
| 4.4 | File size validation via validateFiles |
| 4.5-4.7 | Error display with specific messages |
| 5.2 | Progress bar with percentage |
| 5.3 | Numeric percentage display |
| 5.4 | Success/error status icons |
| 5.5 | Multiple file progress tracking |
| 9.4 | PDF, MD, TXT validation |
| 9.5 | 10MB size limit enforcement |
| 15.3 | ARIA labels and screen reader support |
| 16.3 | Responsive TailwindCSS layout |

## Testing Considerations

### Unit Tests (Optional - Task 8.5)
- File type validation
- File size validation
- Drag-and-drop handlers
- Progress display
- Error message display
- Keyboard navigation

### Property Tests (Optional - Task 8.6)
- File validation consistency
- Progress value bounds (0-100)
- Valid files always pass validation

## Performance Considerations

- File validation happens synchronously (fast)
- Progress updates trigger re-renders (optimized by Zustand)
- Large file lists may need virtualization (future enhancement)
- File input reset after selection allows re-selecting same file
