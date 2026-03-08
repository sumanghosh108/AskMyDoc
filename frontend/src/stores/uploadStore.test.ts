import { describe, it, expect, beforeEach } from 'vitest';
import { useUploadStore } from './uploadStore';
import type { UploadProgress } from '../types';

describe('uploadStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useUploadStore.setState({
      isUploading: false,
      progress: [],
    });
  });

  it('should initialize with default state', () => {
    const state = useUploadStore.getState();
    expect(state.isUploading).toBe(false);
    expect(state.progress).toEqual([]);
  });

  it('should set uploading state', () => {
    const { setUploading } = useUploadStore.getState();
    
    setUploading(true);
    expect(useUploadStore.getState().isUploading).toBe(true);
    
    setUploading(false);
    expect(useUploadStore.getState().isUploading).toBe(false);
  });

  it('should set progress array', () => {
    const { setProgress } = useUploadStore.getState();
    const mockProgress: UploadProgress[] = [
      { fileName: 'file1.pdf', progress: 50, status: 'uploading' },
      { fileName: 'file2.txt', progress: 100, status: 'success' },
    ];

    setProgress(mockProgress);
    expect(useUploadStore.getState().progress).toEqual(mockProgress);
  });

  it('should clamp progress values between 0-100 when setting progress', () => {
    const { setProgress } = useUploadStore.getState();
    const mockProgress: UploadProgress[] = [
      { fileName: 'file1.pdf', progress: 150, status: 'uploading' },
      { fileName: 'file2.txt', progress: -10, status: 'uploading' },
    ];

    setProgress(mockProgress);
    const state = useUploadStore.getState();
    expect(state.progress[0].progress).toBe(100);
    expect(state.progress[1].progress).toBe(0);
  });

  it('should update specific file progress', () => {
    const { setProgress, updateFileProgress } = useUploadStore.getState();
    const mockProgress: UploadProgress[] = [
      { fileName: 'file1.pdf', progress: 0, status: 'pending' },
      { fileName: 'file2.txt', progress: 0, status: 'pending' },
    ];

    setProgress(mockProgress);
    updateFileProgress('file1.pdf', { progress: 50, status: 'uploading' });

    const state = useUploadStore.getState();
    expect(state.progress[0]).toEqual({
      fileName: 'file1.pdf',
      progress: 50,
      status: 'uploading',
    });
    expect(state.progress[1]).toEqual({
      fileName: 'file2.txt',
      progress: 0,
      status: 'pending',
    });
  });

  it('should clamp progress values between 0-100 when updating file progress', () => {
    const { setProgress, updateFileProgress } = useUploadStore.getState();
    const mockProgress: UploadProgress[] = [
      { fileName: 'file1.pdf', progress: 50, status: 'uploading' },
    ];

    setProgress(mockProgress);
    updateFileProgress('file1.pdf', { progress: 150 });

    const state = useUploadStore.getState();
    expect(state.progress[0].progress).toBe(100);
  });

  it('should handle error status in file progress', () => {
    const { setProgress, updateFileProgress } = useUploadStore.getState();
    const mockProgress: UploadProgress[] = [
      { fileName: 'file1.pdf', progress: 50, status: 'uploading' },
    ];

    setProgress(mockProgress);
    updateFileProgress('file1.pdf', {
      status: 'error',
      error: 'Upload failed',
    });

    const state = useUploadStore.getState();
    expect(state.progress[0].status).toBe('error');
    expect(state.progress[0].error).toBe('Upload failed');
  });

  it('should not modify other files when updating specific file', () => {
    const { setProgress, updateFileProgress } = useUploadStore.getState();
    const mockProgress: UploadProgress[] = [
      { fileName: 'file1.pdf', progress: 25, status: 'uploading' },
      { fileName: 'file2.txt', progress: 75, status: 'uploading' },
      { fileName: 'file3.md', progress: 100, status: 'success' },
    ];

    setProgress(mockProgress);
    updateFileProgress('file2.txt', { progress: 100, status: 'success' });

    const state = useUploadStore.getState();
    expect(state.progress[0]).toEqual(mockProgress[0]);
    expect(state.progress[1]).toEqual({
      fileName: 'file2.txt',
      progress: 100,
      status: 'success',
    });
    expect(state.progress[2]).toEqual(mockProgress[2]);
  });
});
