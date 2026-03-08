import { create } from 'zustand';
import type { UploadProgress } from '../types';

interface UploadState {
  // State
  isUploading: boolean;
  progress: UploadProgress[];

  // Actions
  setUploading: (uploading: boolean) => void;
  setProgress: (progress: UploadProgress[]) => void;
  updateFileProgress: (fileName: string, update: Partial<UploadProgress>) => void;
}

export const useUploadStore = create<UploadState>((set) => ({
  // Initial state
  isUploading: false,
  progress: [],

  // Actions
  setUploading: (uploading: boolean) =>
    set({
      isUploading: uploading,
    }),

  setProgress: (progress: UploadProgress[]) =>
    set({
      progress: progress.map((item) => ({
        ...item,
        // Ensure progress values stay between 0-100
        progress: Math.max(0, Math.min(100, item.progress)),
      })),
    }),

  updateFileProgress: (fileName: string, update: Partial<UploadProgress>) =>
    set((state) => {
      const updatedProgress = state.progress.map((item) => {
        if (item.fileName === fileName) {
          const updatedItem = { ...item, ...update };
          // Ensure progress values stay between 0-100
          if (updatedItem.progress !== undefined) {
            updatedItem.progress = Math.max(0, Math.min(100, updatedItem.progress));
          }
          return updatedItem;
        }
        return item;
      });

      return { progress: updatedProgress };
    }),
}));
