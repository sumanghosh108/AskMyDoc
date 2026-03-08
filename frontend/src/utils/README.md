# Validation Utilities

This module provides comprehensive validation utilities for the React RAG Frontend application.

## Overview

The validation utilities ensure that all user input is validated before being sent to the backend API. This includes query validation, file upload validation, and parameter validation.

## Requirements Coverage

- **Requirement 9.1**: Query cannot be empty or whitespace-only
- **Requirement 9.2**: Query cannot exceed 2000 characters
- **Requirement 9.3**: TopK must be between 1 and 20
- **Requirement 9.4**: Only PDF, MD, and TXT files are accepted
- **Requirement 9.5**: Files cannot exceed 10MB

## Functions

### `validateQuery(question: string): ValidationResult`

Validates a query question string.

**Parameters:**
- `question` - The query question to validate

**Returns:**
- `ValidationResult` object with `isValid` boolean and optional `error` message

**Examples:**
```typescript
validateQuery('What is machine learning?');
// { isValid: true }

validateQuery('');
// { isValid: false, error: 'Question cannot be empty' }

validateQuery('a'.repeat(2001));
// { isValid: false, error: 'Question cannot exceed 2000 characters' }
```

### `validateFile(file: File): ValidationResult`

Validates a file for upload.

**Parameters:**
- `file` - The File object to validate

**Returns:**
- `ValidationResult` object with `isValid` boolean and optional `error` message

**Examples:**
```typescript
const pdfFile = new File(['content'], 'doc.pdf', { type: 'application/pdf' });
validateFile(pdfFile);
// { isValid: true }

const imageFile = new File(['content'], 'image.jpg', { type: 'image/jpeg' });
validateFile(imageFile);
// { isValid: false, error: 'File type not supported...' }
```

### `validateTopK(topK: number): ValidationResult`

Validates the topK parameter.

**Parameters:**
- `topK` - The topK value to validate

**Returns:**
- `ValidationResult` object with `isValid` boolean and optional `error` message

**Examples:**
```typescript
validateTopK(5);
// { isValid: true }

validateTopK(0);
// { isValid: false, error: 'topK must be between 1 and 20' }

validateTopK(5.5);
// { isValid: false, error: 'topK must be an integer' }
```

### `validateFiles(files: File[]): { validFiles: File[], invalidFiles: Array<{ file: File, error: string }> }`

Validates multiple files at once.

**Parameters:**
- `files` - Array of File objects to validate

**Returns:**
- Object with `validFiles` array and `invalidFiles` array with error messages

**Examples:**
```typescript
const files = [
  new File(['content'], 'doc.pdf', { type: 'application/pdf' }),
  new File(['content'], 'image.jpg', { type: 'image/jpeg' }),
];

const result = validateFiles(files);
// {
//   validFiles: [File { name: 'doc.pdf' }],
//   invalidFiles: [{ file: File { name: 'image.jpg' }, error: '...' }]
// }
```

### `getRemainingCharacters(question: string): number`

Gets the remaining character count for a query.

**Parameters:**
- `question` - The current query question

**Returns:**
- Number of characters remaining

**Examples:**
```typescript
getRemainingCharacters('Hello');
// 1995 (2000 - 5)
```

### `isNearCharacterLimit(question: string, threshold?: number): boolean`

Checks if a query is at or near the character limit.

**Parameters:**
- `question` - The current query question
- `threshold` - Warning threshold in characters (default: 50)

**Returns:**
- True if within threshold of limit

**Examples:**
```typescript
isNearCharacterLimit('a'.repeat(1960));
// true (within 50 characters of 2000 limit)

isNearCharacterLimit('Hello');
// false
```

## Constants

### `VALIDATION_RULES`

Object containing all validation rule constants:

```typescript
{
  QUERY_MAX_LENGTH: 2000,
  QUERY_MIN_LENGTH: 1,
  MAX_FILE_SIZE: 10485760, // 10MB in bytes
  ACCEPTED_FILE_TYPES: ['.pdf', '.md', '.txt'],
  ACCEPTED_MIME_TYPES: ['application/pdf', 'text/markdown', 'text/plain'],
  TOP_K_MIN: 1,
  TOP_K_MAX: 20,
}
```

## Usage in Components

### Query Interface Component

```typescript
import { validateQuery, getRemainingCharacters } from '@/utils';

function QueryInterface() {
  const [question, setQuestion] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    const validation = validateQuery(question);
    if (!validation.isValid) {
      setError(validation.error);
      return;
    }
    // Proceed with submission
  };

  const remaining = getRemainingCharacters(question);

  return (
    <div>
      <textarea value={question} onChange={(e) => setQuestion(e.target.value)} />
      <p>{remaining} characters remaining</p>
      {error && <p className="error">{error}</p>}
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
```

### Document Upload Component

```typescript
import { validateFiles } from '@/utils';

function DocumentUpload() {
  const handleFileSelect = (files: File[]) => {
    const { validFiles, invalidFiles } = validateFiles(files);

    if (invalidFiles.length > 0) {
      invalidFiles.forEach(({ file, error }) => {
        console.error(`${file.name}: ${error}`);
      });
    }

    if (validFiles.length > 0) {
      // Proceed with upload
      uploadFiles(validFiles);
    }
  };

  return (
    <input
      type="file"
      multiple
      accept=".pdf,.md,.txt"
      onChange={(e) => handleFileSelect(Array.from(e.target.files || []))}
    />
  );
}
```

## Testing

The validation utilities include comprehensive unit tests covering:

- Valid and invalid queries
- Empty and whitespace-only queries
- Queries at and exceeding character limits
- Valid and invalid file types
- Files at and exceeding size limits
- TopK range validation
- Multiple file validation
- Helper functions

Run tests with:
```bash
npm test -- validation.test.ts
```

## Type Definitions

```typescript
interface ValidationResult {
  isValid: boolean;
  error?: string;
}
```

## Error Messages

The validation utilities provide clear, user-friendly error messages:

- `"Question cannot be empty"` - When query is empty or whitespace-only
- `"Question cannot exceed 2000 characters"` - When query is too long
- `"File size exceeds 10MB limit"` - When file is too large
- `"File type not supported. Accepted types: .pdf, .md, .txt"` - When file type is invalid
- `"topK must be between 1 and 20"` - When topK is out of range
- `"topK must be an integer"` - When topK is not a whole number

## Best Practices

1. **Always validate before submission**: Call validation functions before making API requests
2. **Display errors immediately**: Show validation errors as users type for better UX
3. **Use constants**: Reference `VALIDATION_RULES` constants instead of hardcoding values
4. **Handle multiple files**: Use `validateFiles()` for batch validation with detailed error reporting
5. **Show character count**: Use `getRemainingCharacters()` to help users stay within limits
6. **Warn near limits**: Use `isNearCharacterLimit()` to show warnings before hitting the limit

## Security Considerations

- Client-side validation is for UX only - backend must also validate
- File type validation checks both extension and MIME type
- File size limits prevent large uploads that could impact performance
- Query length limits prevent potential DoS attacks
- All validation is performed before any API calls
