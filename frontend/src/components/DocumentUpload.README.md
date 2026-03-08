# DocumentUpload Component

A fully-featured document upload component with drag-and-drop support, file validation, and progress tracking.

## Features

- **Drag-and-Drop Zone** (Requirement 4.1): Interactive drop zone with visual feedback
- **File Selection Button** (Requirement 4.2): Click to open file picker
- **File Type Validation** (Requirements 4.3, 9.4): Validates PDF, MD, and TXT files
- **File Size Validation** (Requirements 4.4, 9.5): Enforces 10MB maximum file size
- **Error Messages** (Requirements 4.5, 4.6, 4.7): Displays specific validation errors
- **Upload Progress** (Requirements 5.2, 5.3, 5.4, 5.5): Shows progress bars and status indicators
- **Multiple File Support**: Handles multiple simultaneous uploads
- **Accessibility** (Requirement 15.3): Full keyboard support and screen reader announcements
- **Responsive Design** (Requirement 16.3): Works on all screen sizes

## Usage

### Basic Usage

```tsx
import { DocumentUpload } from './components/DocumentUpload';
import { useUploadStore } from './stores/uploadStore';
import { uploadFiles } from './services/ingestService';

function MyComponent() {
  const { isUploading, setUploading, setProgress, updateFileProgress } = useUploadStore();

  const handleUpload = async (files: File[]) => {
    setUploading(true);
    setProgress(files.map(f => ({
      fileName: f.name,
      progress: 0,
      status: 'pending',
    })));

    await uploadFiles(files, (progress) => {
      updateFileProgress(progress.fileName, progress);
    });

    setUploading(false);
  };

  return (
    <DocumentUpload 
      onUpload={handleUpload}
      isUploading={isUploading}
    />
  );
}
```

### Custom Configuration

```tsx
<DocumentUpload 
  onUpload={handleUpload}
  isUploading={isUploading}
  acceptedTypes={['.pdf', '.txt']}
  maxSize={5 * 1024 * 1024} // 5MB
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onUpload` | `(files: File[]) => void` | Required | Callback when valid files are selected |
| `isUploading` | `boolean` | `false` | Whether upload is in progress |
| `acceptedTypes` | `readonly string[]` | `['.pdf', '.md', '.txt']` | Accepted file extensions |
| `maxSize` | `number` | `10485760` (10MB) | Maximum file size in bytes |

## File Validation

The component validates files before upload:

1. **File Type**: Only accepts PDF, Markdown (.md), and text (.txt) files
2. **File Size**: Rejects files larger than 10MB (configurable)
3. **Error Display**: Shows specific error messages for each invalid file

Invalid files are displayed in a red error box with details about why they were rejected.

## Upload Progress

The component displays real-time upload progress for each file:

- **Progress Bar**: Visual indicator of upload completion (0-100%)
- **Percentage**: Numeric display of progress
- **Status Icons**: 
  - ✓ Green checkmark for successful uploads
  - ✗ Red X for failed uploads
- **Error Messages**: Detailed error information for failed uploads

## Accessibility Features

- **Keyboard Navigation**: Full keyboard support (Enter/Space to open file picker)
- **ARIA Labels**: Proper labels for all interactive elements
- **Screen Reader Announcements**: Live regions announce upload status changes
- **Focus Management**: Proper focus handling for keyboard users
- **Semantic HTML**: Uses appropriate HTML elements and roles

## Integration with Upload Store

The component reads upload progress from the Zustand upload store:

```typescript
const progress = useUploadStore((state) => state.progress);
```

The store should be updated by the upload handler:

```typescript
// Initialize progress
setProgress(files.map(f => ({
  fileName: f.name,
  progress: 0,
  status: 'pending',
})));

// Update individual file progress
updateFileProgress(fileName, {
  progress: 50,
  status: 'uploading',
});

// Mark as complete
updateFileProgress(fileName, {
  progress: 100,
  status: 'success',
});
```

## Styling

The component uses TailwindCSS for styling with:

- Responsive design that works on all screen sizes
- Hover states for better user feedback
- Color-coded status indicators (blue for uploading, green for success, red for error)
- Smooth transitions and animations

## Requirements Coverage

This component satisfies the following requirements:

- **4.1**: Drag-and-drop zone for file selection
- **4.2**: File selection button
- **4.3**: File type validation
- **4.4**: File size validation
- **4.5-4.7**: Specific error messages for invalid files
- **5.2**: Progress bar display
- **5.3**: Percentage display
- **5.4**: Error indicators
- **5.5**: Multiple simultaneous uploads
- **9.4**: File type validation (PDF, MD, TXT)
- **9.5**: File size validation (max 10MB)
- **15.3**: Accessibility features
- **16.3**: Responsive design

## Example: Complete Upload Flow

See `DocumentUpload.demo.tsx` for a complete working example that demonstrates:

1. File selection (drag-and-drop or button click)
2. File validation
3. Upload progress tracking
4. Success/error handling
5. Integration with upload store
