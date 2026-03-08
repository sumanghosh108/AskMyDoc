// Validation utilities for query and file inputs

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Constants for validation rules
 */
export const VALIDATION_RULES = {
  // Query validation (Requirements 9.1, 9.2)
  QUERY_MAX_LENGTH: 2000,
  QUERY_MIN_LENGTH: 1,
  
  // File validation (Requirements 9.4, 9.5)
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB in bytes
  ACCEPTED_FILE_TYPES: ['.pdf', '.md', '.txt'],
  ACCEPTED_MIME_TYPES: [
    'application/pdf',
    'text/markdown',
    'text/plain',
  ],
  
  // TopK validation (Requirement 9.3)
  TOP_K_MIN: 1,
  TOP_K_MAX: 20,
} as const;

/**
 * Validates a query question string
 * Requirements: 9.1, 9.2
 * 
 * @param question - The query question to validate
 * @returns ValidationResult with isValid flag and optional error message
 */
export function validateQuery(question: string): ValidationResult {
  // Check if question is empty or whitespace-only (Requirement 9.1)
  if (!question || question.trim().length === 0) {
    return {
      isValid: false,
      error: 'Question cannot be empty',
    };
  }

  // Check if question exceeds maximum length (Requirement 9.2)
  if (question.length > VALIDATION_RULES.QUERY_MAX_LENGTH) {
    return {
      isValid: false,
      error: `Question cannot exceed ${VALIDATION_RULES.QUERY_MAX_LENGTH} characters`,
    };
  }

  return { isValid: true };
}

/**
 * Validates a file for upload
 * Requirements: 9.4, 9.5
 * 
 * @param file - The File object to validate
 * @returns ValidationResult with isValid flag and optional error message
 */
export function validateFile(file: File): ValidationResult {
  // Check file size (Requirement 9.5)
  if (file.size > VALIDATION_RULES.MAX_FILE_SIZE) {
    const maxSizeMB = VALIDATION_RULES.MAX_FILE_SIZE / (1024 * 1024);
    return {
      isValid: false,
      error: `File size exceeds ${maxSizeMB}MB limit`,
    };
  }

  // Check file type by extension (Requirement 9.4)
  const fileName = file.name.toLowerCase();
  const hasValidExtension = VALIDATION_RULES.ACCEPTED_FILE_TYPES.some(
    (ext) => fileName.endsWith(ext)
  );

  if (!hasValidExtension) {
    return {
      isValid: false,
      error: `File type not supported. Accepted types: ${VALIDATION_RULES.ACCEPTED_FILE_TYPES.join(', ')}`,
    };
  }

  // Additional check: validate MIME type if available
  if (file.type && !(VALIDATION_RULES.ACCEPTED_MIME_TYPES as readonly string[]).includes(file.type)) {
    // Some browsers may not set the correct MIME type, so we only warn if it's set but wrong
    // We still allow the file if the extension is correct
    console.warn(`File MIME type "${file.type}" may not be supported, but extension is valid`);
  }

  return { isValid: true };
}

/**
 * Validates topK parameter
 * Requirement: 9.3
 * 
 * @param topK - The topK value to validate
 * @returns ValidationResult with isValid flag and optional error message
 */
export function validateTopK(topK: number): ValidationResult {
  // Check if topK is within valid range (Requirement 9.3)
  if (topK < VALIDATION_RULES.TOP_K_MIN || topK > VALIDATION_RULES.TOP_K_MAX) {
    return {
      isValid: false,
      error: `topK must be between ${VALIDATION_RULES.TOP_K_MIN} and ${VALIDATION_RULES.TOP_K_MAX}`,
    };
  }

  // Check if topK is an integer
  if (!Number.isInteger(topK)) {
    return {
      isValid: false,
      error: 'topK must be an integer',
    };
  }

  return { isValid: true };
}

/**
 * Validates multiple files at once
 * Requirements: 9.4, 9.5
 * 
 * @param files - Array of File objects to validate
 * @returns Object with valid files array and invalid files with error messages
 */
export function validateFiles(files: File[]): {
  validFiles: File[];
  invalidFiles: Array<{ file: File; error: string }>;
} {
  const validFiles: File[] = [];
  const invalidFiles: Array<{ file: File; error: string }> = [];

  for (const file of files) {
    const result = validateFile(file);
    if (result.isValid) {
      validFiles.push(file);
    } else {
      invalidFiles.push({
        file,
        error: result.error || 'Unknown validation error',
      });
    }
  }

  return { validFiles, invalidFiles };
}

/**
 * Gets the remaining character count for a query
 * 
 * @param question - The current query question
 * @returns Number of characters remaining
 */
export function getRemainingCharacters(question: string): number {
  return VALIDATION_RULES.QUERY_MAX_LENGTH - question.length;
}

/**
 * Checks if a query is at or near the character limit
 * 
 * @param question - The current query question
 * @param threshold - Warning threshold (default 50 characters)
 * @returns True if within threshold of limit
 */
export function isNearCharacterLimit(question: string, threshold = 50): boolean {
  return getRemainingCharacters(question) <= threshold;
}
