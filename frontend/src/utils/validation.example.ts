/**
 * Example usage of validation utilities
 * This file demonstrates how to use the validation functions
 */

import {
  validateQuery,
  validateFile,
  validateTopK,
  validateFiles,
  getRemainingCharacters,
  isNearCharacterLimit,
  VALIDATION_RULES,
} from './validation';

// Example 1: Query validation
console.log('=== Query Validation Examples ===');

const validQuery = 'What is machine learning?';
const emptyQuery = '';
const longQuery = 'a'.repeat(2001);

console.log('Valid query:', validateQuery(validQuery));
// Output: { isValid: true }

console.log('Empty query:', validateQuery(emptyQuery));
// Output: { isValid: false, error: 'Question cannot be empty' }

console.log('Long query:', validateQuery(longQuery));
// Output: { isValid: false, error: 'Question cannot exceed 2000 characters' }

// Example 2: Character count helpers
console.log('\n=== Character Count Examples ===');

const question = 'Hello, how are you?';
console.log('Remaining characters:', getRemainingCharacters(question));
// Output: 1981 (2000 - 19)

const nearLimitQuery = 'a'.repeat(1960);
console.log('Near limit?', isNearCharacterLimit(nearLimitQuery));
// Output: true (within 50 characters of limit)

// Example 3: File validation
console.log('\n=== File Validation Examples ===');

// Valid PDF file
const pdfFile = new File(['content'], 'document.pdf', {
  type: 'application/pdf',
});
console.log('Valid PDF:', validateFile(pdfFile));
// Output: { isValid: true }

// Invalid file type
const imageFile = new File(['content'], 'image.jpg', {
  type: 'image/jpeg',
});
console.log('Invalid type:', validateFile(imageFile));
// Output: { isValid: false, error: 'File type not supported...' }

// File too large (simulated)
const largeFile = new File([new Uint8Array(11 * 1024 * 1024)], 'large.pdf', {
  type: 'application/pdf',
});
console.log('Too large:', validateFile(largeFile));
// Output: { isValid: false, error: 'File size exceeds 10MB limit' }

// Example 4: Multiple file validation
console.log('\n=== Multiple File Validation Examples ===');

const files = [
  new File(['content'], 'doc1.pdf', { type: 'application/pdf' }),
  new File(['content'], 'doc2.txt', { type: 'text/plain' }),
  new File(['content'], 'image.jpg', { type: 'image/jpeg' }),
];

const result = validateFiles(files);
console.log('Valid files:', result.validFiles.length);
// Output: 2

console.log('Invalid files:', result.invalidFiles.length);
// Output: 1

console.log('Invalid file errors:', result.invalidFiles.map(f => f.error));
// Output: ['File type not supported...']

// Example 5: TopK validation
console.log('\n=== TopK Validation Examples ===');

console.log('Valid topK (5):', validateTopK(5));
// Output: { isValid: true }

console.log('Invalid topK (0):', validateTopK(0));
// Output: { isValid: false, error: 'topK must be between 1 and 20' }

console.log('Invalid topK (21):', validateTopK(21));
// Output: { isValid: false, error: 'topK must be between 1 and 20' }

console.log('Invalid topK (5.5):', validateTopK(5.5));
// Output: { isValid: false, error: 'topK must be an integer' }

// Example 6: Using validation rules constants
console.log('\n=== Validation Rules Constants ===');

console.log('Max query length:', VALIDATION_RULES.QUERY_MAX_LENGTH);
// Output: 2000

console.log('Max file size:', VALIDATION_RULES.MAX_FILE_SIZE);
// Output: 10485760 (10MB in bytes)

console.log('Accepted file types:', VALIDATION_RULES.ACCEPTED_FILE_TYPES);
// Output: ['.pdf', '.md', '.txt']

console.log('TopK range:', VALIDATION_RULES.TOP_K_MIN, '-', VALIDATION_RULES.TOP_K_MAX);
// Output: 1 - 20

// Example 7: Real-world usage in a component
console.log('\n=== Component Usage Example ===');

function handleQuerySubmit(question: string, topK: number) {
  // Validate query
  const queryValidation = validateQuery(question);
  if (!queryValidation.isValid) {
    console.error('Query validation failed:', queryValidation.error);
    return;
  }

  // Validate topK
  const topKValidation = validateTopK(topK);
  if (!topKValidation.isValid) {
    console.error('TopK validation failed:', topKValidation.error);
    return;
  }

  // Proceed with submission
  console.log('Submitting query:', question);
  console.log('With topK:', topK);
}

handleQuerySubmit('What is AI?', 5);
// Output: Submitting query: What is AI?
//         With topK: 5

handleQuerySubmit('', 5);
// Output: Query validation failed: Question cannot be empty

handleQuerySubmit('What is AI?', 25);
// Output: TopK validation failed: topK must be between 1 and 20

// Example 8: File upload handler
console.log('\n=== File Upload Handler Example ===');

function handleFileUpload(files: File[]) {
  const { validFiles, invalidFiles } = validateFiles(files);

  if (invalidFiles.length > 0) {
    console.log('Some files are invalid:');
    invalidFiles.forEach(({ file, error }) => {
      console.log(`- ${file.name}: ${error}`);
    });
  }

  if (validFiles.length > 0) {
    console.log(`Uploading ${validFiles.length} valid file(s)...`);
    validFiles.forEach(file => {
      console.log(`- ${file.name} (${file.size} bytes)`);
    });
  }
}

const uploadFiles = [
  new File(['content'], 'doc.pdf', { type: 'application/pdf' }),
  new File(['content'], 'notes.txt', { type: 'text/plain' }),
  new File(['content'], 'photo.jpg', { type: 'image/jpeg' }),
];

handleFileUpload(uploadFiles);
// Output: Some files are invalid:
//         - photo.jpg: File type not supported...
//         Uploading 2 valid file(s)...
//         - doc.pdf (7 bytes)
//         - notes.txt (7 bytes)
