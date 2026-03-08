import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { QueryHistoryItem } from '../types';

interface QueryState {
  // State
  isLoading: boolean;
  currentResult: QueryHistoryItem | null;
  error: string | null;
  history: QueryHistoryItem[];

  // Actions
  setLoading: (loading: boolean) => void;
  setCurrentResult: (result: QueryHistoryItem | null) => void;
  setError: (error: string | null) => void;
  addToHistory: (item: QueryHistoryItem) => void;
  clearHistory: () => void;
}

const MAX_HISTORY_SIZE = 50;

export const useQueryStore = create<QueryState>()(
  persist(
    (set) => ({
      // Initial state
      isLoading: false,
      currentResult: null,
      error: null,
      history: [],

      // Actions
      setLoading: (loading: boolean) =>
        set(() => {
          // State consistency: when loading is true, clear currentResult and error
          if (loading) {
            return {
              isLoading: true,
              currentResult: null,
              error: null,
            };
          }
          return { isLoading: false };
        }),

      setCurrentResult: (result: QueryHistoryItem | null) =>
        set({
          currentResult: result,
          isLoading: false,
          error: null,
        }),

      setError: (error: string | null) =>
        set({
          error,
          isLoading: false,
          currentResult: null,
        }),

      addToHistory: (item: QueryHistoryItem) =>
        set((state) => {
          // Add new item to the beginning of the array (most recent first)
          const newHistory = [item, ...state.history];

          // Sort by timestamp in descending order (most recent first)
          newHistory.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

          // Limit to MAX_HISTORY_SIZE items
          const limitedHistory = newHistory.slice(0, MAX_HISTORY_SIZE);

          return { history: limitedHistory };
        }),

      clearHistory: () =>
        set({
          history: [],
        }),
    }),
    {
      name: 'query-storage', // localStorage key
      partialize: (state) => ({
        // Only persist history to localStorage
        history: state.history,
      }),
      // Custom storage to handle Date serialization
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name);
          if (!str) return null;
          
          const parsed = JSON.parse(str);
          return {
            state: {
              history: parsed.state.history.map((item: QueryHistoryItem & { timestamp: string }) => ({
                ...item,
                timestamp: new Date(item.timestamp),
              })),
            },
          };
        },
        setItem: (name, value) => {
          const serialized = {
            state: {
              history: value.state.history.map((item: QueryHistoryItem) => ({
                ...item,
                timestamp: item.timestamp.toISOString(),
              })),
            },
          };
          localStorage.setItem(name, JSON.stringify(serialized));
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
);
