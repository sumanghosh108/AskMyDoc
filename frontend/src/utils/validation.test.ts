import { describe, it, expect } from 'vitest';
import {
  validateQuery,
  validateFile,
  validateTopK,
  validateFiles,
  getRemainingCharacters,
  isNearCharacterLimit,
  VALIDATION_RULES,
} from './validation';

describe('validateQuery', () => {
  it('should accept valid non-empty query', () => {
    const result = validateQuery('What is machine learning?');
    expect(result.isValid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('should reject empty string', () => {
    const result = validateQuery('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Question cannot be empty');
  });

  it('should reject whitespace-only string', () => {
    const result = validateQuery('   ');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Question cannot be empty');
  });

  it('should reject query exceeding 2000 characters', () => {
    const longQuery = 'a'.repeat(2001);
    const result = validateQuery(longQuery);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('2000 characters');
  });

  it('should accept query at exactly 2000 characters', () => {
    const maxQuery = 'a'.repeat(2000);
    const result = validateQuery(maxQuery);
    expect(result.isValid).toBe(true);
  });

  it('should accept query with special characters', () => {
    const result = validateQuery('What is AI? How does it work?!');
    expect(result.isValid).toBe(true);
  });
});

describe('validateFile', () => {
  it('should accept valid PDF file under size limit', () => {
    const file = new File(['content'], 'document.pdf', {
      type: 'application/pdf',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('should accept valid Markdown file', () => {
    const file = new File(['# Title'], 'readme.md', {
      type: 'text/markdown',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(true);
  });

  it('should accept valid text file', () => {
    const file = new File(['text content'], 'notes.txt', {
      type: 'text/plain',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(true);
  });

  it('should reject file exceeding 10MB', () => {
    const largeContent = new Uint8Array(11 * 1024 * 1024); // 11MB
    const file = new File([largeContent], 'large.pdf', {
      type: 'application/pdf',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('10MB limit');
  });

  it('should accept file at exactly 10MB', () => {
    const maxContent = new Uint8Array(10 * 1024 * 1024); // Exactly 10MB
    const file = new File([maxContent], 'max.pdf', {
      type: 'application/pdf',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(true);
  });

  it('should reject unsupported file type', () => {
    const file = new File(['content'], 'image.jpg', {
      type: 'image/jpeg',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('not supported');
  });

  it('should reject file with no extension', () => {
    const file = new File(['content'], 'document', {
      type: 'application/octet-stream',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(false);
  });

  it('should handle uppercase file extensions', () => {
    const file = new File(['content'], 'DOCUMENT.PDF', {
      type: 'application/pdf',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(true);
  });

  it('should handle mixed case file extensions', () => {
    const file = new File(['content'], 'Document.Txt', {
      type: 'text/plain',
    });
    const result = validateFile(file);
    expect(result.isValid).toBe(true);
  });
});

describe('validateTopK', () => {
  it('should accept valid topK value', () => {
    const result = validateTopK(5);
    expect(result.isValid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('should accept minimum topK value (1)', () => {
    const result = validateTopK(1);
    expect(result.isValid).toBe(true);
  });

  it('should accept maximum topK value (20)', () => {
    const result = validateTopK(20);
    expect(result.isValid).toBe(true);
  });

  it('should reject topK below minimum', () => {
    const result = validateTopK(0);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('between 1 and 20');
  });

  it('should reject topK above maximum', () => {
    const result = validateTopK(21);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('between 1 and 20');
  });

  it('should reject negative topK', () => {
    const result = validateTopK(-5);
    expect(result.isValid).toBe(false);
  });

  it('should reject non-integer topK', () => {
    const result = validateTopK(5.5);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('must be an integer');
  });
});

describe('validateFiles', () => {
  it('should separate valid and invalid files', () => {
    const validFile1 = new File(['content'], 'doc1.pdf', {
      type: 'application/pdf',
    });
    const validFile2 = new File(['content'], 'doc2.txt', {
      type: 'text/plain',
    });
    const invalidFile = new File(['content'], 'image.jpg', {
      type: 'image/jpeg',
    });

    const result = validateFiles([validFile1, validFile2, invalidFile]);

    expect(result.validFiles).toHaveLength(2);
    expect(result.invalidFiles).toHaveLength(1);
    expect(result.validFiles).toContain(validFile1);
    expect(result.validFiles).toContain(validFile2);
    expect(result.invalidFiles[0].file).toBe(invalidFile);
    expect(result.invalidFiles[0].error).toBeTruthy();
  });

  it('should handle all valid files', () => {
    const file1 = new File(['content'], 'doc1.pdf', {
      type: 'application/pdf',
    });
    const file2 = new File(['content'], 'doc2.md', {
      type: 'text/markdown',
    });

    const result = validateFiles([file1, file2]);

    expect(result.validFiles).toHaveLength(2);
    expect(result.invalidFiles).toHaveLength(0);
  });

  it('should handle all invalid files', () => {
    const file1 = new File(['content'], 'image.jpg', {
      type: 'image/jpeg',
    });
    const file2 = new File(['content'], 'video.mp4', {
      type: 'video/mp4',
    });

    const result = validateFiles([file1, file2]);

    expect(result.validFiles).toHaveLength(0);
    expect(result.invalidFiles).toHaveLength(2);
  });

  it('should handle empty array', () => {
    const result = validateFiles([]);

    expect(result.validFiles).toHaveLength(0);
    expect(result.invalidFiles).toHaveLength(0);
  });
});

describe('getRemainingCharacters', () => {
  it('should return correct remaining characters', () => {
    const question = 'Hello';
    const remaining = getRemainingCharacters(question);
    expect(remaining).toBe(VALIDATION_RULES.QUERY_MAX_LENGTH - 5);
  });

  it('should return max length for empty string', () => {
    const remaining = getRemainingCharacters('');
    expect(remaining).toBe(VALIDATION_RULES.QUERY_MAX_LENGTH);
  });

  it('should return 0 for string at max length', () => {
    const maxQuery = 'a'.repeat(VALIDATION_RULES.QUERY_MAX_LENGTH);
    const remaining = getRemainingCharacters(maxQuery);
    expect(remaining).toBe(0);
  });

  it('should return negative for string exceeding max length', () => {
    const longQuery = 'a'.repeat(VALIDATION_RULES.QUERY_MAX_LENGTH + 10);
    const remaining = getRemainingCharacters(longQuery);
    expect(remaining).toBe(-10);
  });
});

describe('isNearCharacterLimit', () => {
  it('should return true when within default threshold', () => {
    const question = 'a'.repeat(VALIDATION_RULES.QUERY_MAX_LENGTH - 30);
    expect(isNearCharacterLimit(question)).toBe(true);
  });

  it('should return false when not near limit', () => {
    const question = 'a'.repeat(100);
    expect(isNearCharacterLimit(question)).toBe(false);
  });

  it('should return true when at exactly threshold', () => {
    const question = 'a'.repeat(VALIDATION_RULES.QUERY_MAX_LENGTH - 50);
    expect(isNearCharacterLimit(question, 50)).toBe(true);
  });

  it('should use custom threshold', () => {
    const question = 'a'.repeat(VALIDATION_RULES.QUERY_MAX_LENGTH - 100);
    expect(isNearCharacterLimit(question, 100)).toBe(true);
    expect(isNearCharacterLimit(question, 50)).toBe(false);
  });

  it('should return true when at max length', () => {
    const question = 'a'.repeat(VALIDATION_RULES.QUERY_MAX_LENGTH);
    expect(isNearCharacterLimit(question)).toBe(true);
  });
});
