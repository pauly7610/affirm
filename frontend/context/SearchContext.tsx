import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { SearchResponse, RefineChip } from '../types';
import { searchQuery } from '../lib/api';

interface SearchState {
  query: string;
  results: SearchResponse | null;
  loading: boolean;
  error: string | null;
  activeRefines: Record<string, boolean>;
}

interface SearchContextValue extends SearchState {
  runSearch: (query: string, refine?: Record<string, unknown>) => Promise<void>;
  setQuery: (q: string) => void;
  toggleRefine: (key: string) => void;
  clearResults: () => void;
}

const SearchContext = createContext<SearchContextValue | null>(null);

export function SearchProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SearchState>({
    query: '',
    results: null,
    loading: false,
    error: null,
    activeRefines: {},
  });

  const runSearch = useCallback(async (q: string, refine?: Record<string, unknown>) => {
    setState(prev => ({ ...prev, query: q, loading: true, error: null }));
    try {
      const res = await searchQuery({
        query: q,
        refine: refine as SearchState['activeRefines'] & {
          onlyZeroApr?: boolean;
          maxMonthly?: number;
          sort?: 'lowest_monthly' | 'lowest_total' | 'shortest_term';
          category?: string;
        },
      });
      setState(prev => ({ ...prev, results: res, loading: false }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Search failed';
      setState(prev => ({ ...prev, error: message, loading: false }));
    }
  }, []);

  const setQuery = useCallback((q: string) => {
    setState(prev => ({ ...prev, query: q }));
  }, []);

  const toggleRefine = useCallback((key: string) => {
    setState(prev => {
      const newRefines = { ...prev.activeRefines, [key]: !prev.activeRefines[key] };
      // Build refine object from active toggles
      const refine: Record<string, unknown> = {};
      if (newRefines['only_zero_apr']) refine.onlyZeroApr = true;
      if (newRefines['lowest_monthly']) refine.sort = 'lowest_monthly';
      if (newRefines['lowest_total']) refine.sort = 'lowest_total';
      if (newRefines['shortest_term']) refine.sort = 'shortest_term';

      return { ...prev, activeRefines: newRefines };
    });
  }, []);

  const clearResults = useCallback(() => {
    setState(prev => ({ ...prev, results: null, error: null, activeRefines: {} }));
  }, []);

  return (
    <SearchContext.Provider value={{ ...state, runSearch, setQuery, toggleRefine, clearResults }}>
      {children}
    </SearchContext.Provider>
  );
}

export function useSearch(): SearchContextValue {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error('useSearch must be inside SearchProvider');
  return ctx;
}
