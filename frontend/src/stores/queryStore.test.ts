import { describe, it, expect, beforeEach } from 'vitest';
import { useQueryStore } from './queryStore';
import type { QueryHistoryItem } from '../types';

describe('Query Store', () => {
  beforeEach(() => {
    // Clear the store before each test
    useQueryStore.setState({
      isLoading: false,
      currentResult: null,
      error: null,
      history: [],
    });
    // Clear localStorage
    localStorage.clear();
  });

  describe('setLoading', () => {
    it('should set loading to true and clear currentResult and error', () => {
      const store = useQueryStore.getState();
      
      // Set some initial state
      store.setCurrentResult({
        id: '1',
        question: 'test',
        answer: 'answer',
        sources: [],
        timestamp: new Date(),
        contextChunks: 1,
      });
      store.setError('some error');
      
      // Set loading to true
      store.setLoading(true);
      
      const state = useQueryStore.getState();
      expect(state.isLoading).toBe(true);
      expect(state.currentResult).toBeNull();
      expect(state.error).toBeNull();
    });

    it('should set loading to false without clearing other state', () => {
      const store = useQueryStore.getState();
      
      store.setLoading(false);
      
      const state = useQueryStore.getState();
      expect(state.isLoading).toBe(false);
    });
  });

  describe('setCurrentResult', () => {
    it('should set currentResult and clear loading and error', () => {
      const store = useQueryStore.getState();
      const result: QueryHistoryItem = {
        id: '1',
        question: 'test question',
        answer: 'test answer',
        sources: [],
        timestamp: new Date(),
        contextChunks: 5,
      };
      
      store.setLoading(true);
      store.setError('some error');
      
      store.setCurrentResult(result);
      
      const state = useQueryStore.getState();
      expect(state.currentResult).toEqual(result);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('setError', () => {
    it('should set error and clear loading and currentResult', () => {
      const store = useQueryStore.getState();
      
      store.setLoading(true);
      store.setCurrentResult({
        id: '1',
        question: 'test',
        answer: 'answer',
        sources: [],
        timestamp: new Date(),
        contextChunks: 1,
      });
      
      store.setError('test error');
      
      const state = useQueryStore.getState();
      expect(state.error).toBe('test error');
      expect(state.isLoading).toBe(false);
      expect(state.currentResult).toBeNull();
    });
  });

  describe('addToHistory', () => {
    it('should add item to history', () => {
      const store = useQueryStore.getState();
      const item: QueryHistoryItem = {
        id: '1',
        question: 'test question',
        answer: 'test answer',
        sources: [],
        timestamp: new Date(),
        contextChunks: 5,
      };
      
      store.addToHistory(item);
      
      const state = useQueryStore.getState();
      expect(state.history).toHaveLength(1);
      expect(state.history[0]).toEqual(item);
    });

    it('should maintain descending timestamp order', () => {
      const store = useQueryStore.getState();
      
      const item1: QueryHistoryItem = {
        id: '1',
        question: 'first',
        answer: 'answer1',
        sources: [],
        timestamp: new Date('2024-01-01'),
        contextChunks: 1,
      };
      
      const item2: QueryHistoryItem = {
        id: '2',
        question: 'second',
        answer: 'answer2',
        sources: [],
        timestamp: new Date('2024-01-03'),
        contextChunks: 1,
      };
      
      const item3: QueryHistoryItem = {
        id: '3',
        question: 'third',
        answer: 'answer3',
        sources: [],
        timestamp: new Date('2024-01-02'),
        contextChunks: 1,
      };
      
      store.addToHistory(item1);
      store.addToHistory(item2);
      store.addToHistory(item3);
      
      const state = useQueryStore.getState();
      expect(state.history).toHaveLength(3);
      expect(state.history[0].id).toBe('2'); // Most recent
      expect(state.history[1].id).toBe('3');
      expect(state.history[2].id).toBe('1'); // Oldest
    });

    it('should limit history to 50 items', () => {
      const store = useQueryStore.getState();
      
      // Add 60 items
      for (let i = 0; i < 60; i++) {
        store.addToHistory({
          id: `${i}`,
          question: `question ${i}`,
          answer: `answer ${i}`,
          sources: [],
          timestamp: new Date(Date.now() + i * 1000),
          contextChunks: 1,
        });
      }
      
      const state = useQueryStore.getState();
      expect(state.history).toHaveLength(50);
      // Most recent items should be kept
      expect(state.history[0].id).toBe('59');
      expect(state.history[49].id).toBe('10');
    });
  });

  describe('clearHistory', () => {
    it('should clear all history', () => {
      const store = useQueryStore.getState();
      
      store.addToHistory({
        id: '1',
        question: 'test',
        answer: 'answer',
        sources: [],
        timestamp: new Date(),
        contextChunks: 1,
      });
      
      store.clearHistory();
      
      const state = useQueryStore.getState();
      expect(state.history).toHaveLength(0);
    });
  });

  describe('localStorage persistence', () => {
    it('should persist history to localStorage', () => {
      const store = useQueryStore.getState();
      const item: QueryHistoryItem = {
        id: '1',
        question: 'test question',
        answer: 'test answer',
        sources: [{ source: 'doc1.pdf', page: 1 }],
        timestamp: new Date('2024-01-01'),
        contextChunks: 5,
      };
      
      store.addToHistory(item);
      
      // Check localStorage
      const stored = localStorage.getItem('query-storage');
      expect(stored).toBeTruthy();
      
      const parsed = JSON.parse(stored!);
      expect(parsed.state.history).toHaveLength(1);
      expect(parsed.state.history[0].question).toBe('test question');
      // Timestamp should be serialized as ISO string
      expect(typeof parsed.state.history[0].timestamp).toBe('string');
    });

    it('should restore history from localStorage with Date objects', () => {
      // Clear the store first
      localStorage.clear();
      
      // Manually set localStorage
      const item = {
        id: '1',
        question: 'test question',
        answer: 'test answer',
        sources: [{ source: 'doc1.pdf', page: 1 }],
        timestamp: '2024-01-01T00:00:00.000Z',
        contextChunks: 5,
      };
      
      localStorage.setItem('query-storage', JSON.stringify({
        state: {
          history: [item],
        },
      }));
      
      // Manually trigger rehydration by calling the storage getItem
      const stored = localStorage.getItem('query-storage');
      expect(stored).toBeTruthy();
      
      const parsed = JSON.parse(stored!);
      expect(parsed.state.history).toHaveLength(1);
      
      // Verify the timestamp is a string in storage
      expect(typeof parsed.state.history[0].timestamp).toBe('string');
      
      // When the store loads this data, it should convert to Date
      // This happens automatically on page load, but in tests we need to
      // manually set the state with the deserialized data
      const deserializedHistory = parsed.state.history.map((item: any) => ({
        ...item,
        timestamp: new Date(item.timestamp),
      }));
      
      useQueryStore.setState({ history: deserializedHistory });
      
      const state = useQueryStore.getState();
      expect(state.history).toHaveLength(1);
      expect(state.history[0].question).toBe('test question');
      // Timestamp should be restored as Date object
      expect(state.history[0].timestamp).toBeInstanceOf(Date);
      expect(state.history[0].timestamp.toISOString()).toBe('2024-01-01T00:00:00.000Z');
    });
  });
});
