/**
 * CryptoPulse - useLocalStorage Hook
 * Hook para persistência em localStorage
 */

import { useState, useEffect, useCallback } from 'react';
import { isClient, safeJsonParse } from '@/lib/utils';

type SetValue<T> = T | ((prevValue: T) => T);

interface UseLocalStorageReturn<T> {
  value: T;
  setValue: (value: SetValue<T>) => void;
  removeValue: () => void;
  isLoading: boolean;
}

/**
 * Hook para ler e escrever valores no localStorage
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): UseLocalStorageReturn<T> {
  const [isLoading, setIsLoading] = useState(true);
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  // Read from localStorage on mount
  useEffect(() => {
    if (!isClient()) {
      setIsLoading(false);
      return;
    }

    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        setStoredValue(safeJsonParse(item, initialValue));
      }
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
    } finally {
      setIsLoading(false);
    }
  }, [key, initialValue]);

  // Set value
  const setValue = useCallback(
    (value: SetValue<T>) => {
      if (!isClient()) return;

      try {
        // Allow value to be a function
        const valueToStore =
          value instanceof Function ? value(storedValue) : value;

        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));

        // Dispatch storage event for other tabs
        window.dispatchEvent(
          new StorageEvent('storage', {
            key,
            newValue: JSON.stringify(valueToStore),
          })
        );
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Remove value
  const removeValue = useCallback(() => {
    if (!isClient()) return;

    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Listen for changes in other tabs
  useEffect(() => {
    if (!isClient()) return;

    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === key && event.newValue) {
        setStoredValue(safeJsonParse(event.newValue, initialValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, initialValue]);

  return {
    value: storedValue,
    setValue,
    removeValue,
    isLoading,
  };
}

/**
 * Hook para favoritos/watchlist
 */
export function useWatchlist(): {
  watchlist: string[];
  addToWatchlist: (symbol: string) => void;
  removeFromWatchlist: (symbol: string) => void;
  isInWatchlist: (symbol: string) => boolean;
  toggleWatchlist: (symbol: string) => void;
} {
  const { value: watchlist, setValue } = useLocalStorage<string[]>(
    'cryptopulse-watchlist',
    []
  );

  const addToWatchlist = useCallback(
    (symbol: string) => {
      setValue((prev) => {
        if (prev.includes(symbol)) return prev;
        return [...prev, symbol];
      });
    },
    [setValue]
  );

  const removeFromWatchlist = useCallback(
    (symbol: string) => {
      setValue((prev) => prev.filter((s) => s !== symbol));
    },
    [setValue]
  );

  const isInWatchlist = useCallback(
    (symbol: string) => watchlist.includes(symbol),
    [watchlist]
  );

  const toggleWatchlist = useCallback(
    (symbol: string) => {
      if (isInWatchlist(symbol)) {
        removeFromWatchlist(symbol);
      } else {
        addToWatchlist(symbol);
      }
    },
    [isInWatchlist, addToWatchlist, removeFromWatchlist]
  );

  return {
    watchlist,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
    toggleWatchlist,
  };
}

/**
 * Hook para histórico de visualização
 */
export function useViewHistory(): {
  history: string[];
  addToHistory: (symbol: string) => void;
  clearHistory: () => void;
} {
  const { value: history, setValue, removeValue } = useLocalStorage<string[]>(
    'cryptopulse-view-history',
    []
  );

  const addToHistory = useCallback(
    (symbol: string) => {
      setValue((prev) => {
        // Remove se já existe e adiciona no início
        const filtered = prev.filter((s) => s !== symbol);
        const newHistory = [symbol, ...filtered];
        // Limita a 20 itens
        return newHistory.slice(0, 20);
      });
    },
    [setValue]
  );

  const clearHistory = useCallback(() => {
    removeValue();
  }, [removeValue]);

  return {
    history,
    addToHistory,
    clearHistory,
  };
}

export default useLocalStorage;
