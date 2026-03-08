import React, { useRef, useState } from 'react';
import { ArrowUpTrayIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { validateFiles, VALIDATION_RULES } from '../utils/validation';
import { useUploadStore } from '../stores/uploadStore';
import type { UploadProgress } from '../types';

interface DocumentUploadProps {
  onUpload: (files: File[]) => void;
  acceptedTypes?: readonly string[];
  maxSize?: number;
  isUploading?: boolean;
}

/**
 * DocumentUpload component for handling file uploads with drag-and-drop
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.2, 5.3, 5.4, 5.5, 15.3, 16.3
 */
export function DocumentUpload({
  onUpload,
  acceptedTypes = VALIDATION_RULES.ACCEPTED_FILE_TYPES,
  maxSize = VALIDATION_RULES.MAX_FILE_SIZE,
  isUploading = false,
}: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Array<{ file: File; error: string }>>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const progress = useUploadStore((state) => state.progress);

  // Requirement 4.1: Drag-and-drop zone handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  // Requirement 4.2: File selection button handler
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    handleFiles(files);
    // Reset input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Requirements 4.3, 4.4, 4.5, 4.6, 4.7, 9.4, 9.5: File validation
  const handleFiles = (files: File[]) => {
    if (files.length === 0) return;

    // Validate all files
    const { validFiles, invalidFiles } = validateFiles(files);

    // Requirement 4.7: Display specific error messages for invalid files
    if (invalidFiles.length > 0) {
      setValidationErrors(invalidFiles);
    } else {
      setValidationErrors([]);
    }

    // Requirement 4.8: Initiate upload for valid files
    if (validFiles.length > 0) {
      onUpload(validFiles);
    }
  };

  // Requirement 4.2: Trigger file picker
  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  // Requirement 15.3: Keyboard support for file selection
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleButtonClick();
    }
  };

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  // Get status icon for upload progress
  const getStatusIcon = (status: UploadProgress['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" aria-hidden="true" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" aria-hidden="true" />;
      default:
        return null;
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      {/* Requirement 4.1: Drag-and-drop zone with hover states */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleButtonClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-label="Upload documents by clicking or dragging files"
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200 ease-in-out
          ${isDragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-400" aria-hidden="true" />
        <p className="mt-2 text-sm font-medium text-gray-900">
          {isDragging ? 'Drop files here' : 'Click to upload or drag and drop'}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          {acceptedTypes.join(', ').toUpperCase()} up to {formatFileSize(maxSize)}
        </p>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          disabled={isUploading}
          aria-label="File input"
        />
      </div>

      {/* Requirement 4.7: Display validation errors */}
      {validationErrors.length > 0 && (
        <div 
          className="bg-red-50 border border-red-200 rounded-lg p-4"
          role="alert"
          aria-live="polite"
        >
          <h3 className="text-sm font-medium text-red-800 mb-2">
            Invalid Files ({validationErrors.length})
          </h3>
          <ul className="space-y-1">
            {validationErrors.map((item, index) => (
              <li key={index} className="text-sm text-red-700">
                <span className="font-medium">{item.file.name}</span>: {item.error}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Requirements 5.2, 5.3, 5.4, 5.5: Upload progress display */}
      {progress.length > 0 && (
        <div 
          className="bg-white border border-gray-200 rounded-lg p-4 space-y-3"
          role="region"
          aria-label="Upload progress"
          aria-live="polite"
          aria-atomic="false"
        >
          <h3 className="text-sm font-medium text-gray-900">
            Uploading Files ({progress.length})
          </h3>
          {progress.map((item, index) => (
            <div key={index} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700 truncate flex-1">
                  {item.fileName}
                </span>
                <div className="flex items-center gap-2 ml-2">
                  {/* Requirement 5.2: Display percentage */}
                  <span 
                    className="text-gray-600 tabular-nums"
                    aria-label={`Upload progress: ${item.progress}%`}
                  >
                    {item.progress}%
                  </span>
                  {/* Requirements 5.3, 5.4: Success/error indicators */}
                  {getStatusIcon(item.status)}
                </div>
              </div>
              
              {/* Requirement 5.2: Progress bar */}
              <div 
                className="w-full bg-gray-200 rounded-full h-2 overflow-hidden"
                role="progressbar"
                aria-valuenow={item.progress}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`${item.fileName} upload progress`}
              >
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    item.status === 'error' 
                      ? 'bg-red-500' 
                      : item.status === 'success'
                      ? 'bg-green-500'
                      : 'bg-blue-500'
                  }`}
                  style={{ width: `${item.progress}%` }}
                />
              </div>

              {/* Requirement 5.4: Display error message */}
              {item.status === 'error' && item.error && (
                <p className="text-xs text-red-600 mt-1" role="alert">
                  Error: {item.error}
                </p>
              )}

              {/* Requirement 15.3: Screen reader announcements */}
              <span className="sr-only">
                {item.status === 'success' && `${item.fileName} uploaded successfully`}
                {item.status === 'error' && `${item.fileName} upload failed: ${item.error}`}
                {item.status === 'uploading' && `${item.fileName} uploading: ${item.progress}%`}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
