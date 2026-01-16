/**
 * CryptoPulse - useSignals Hook
 * Hook para dados de sinais e histórico
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { ScoreDetail, ScoreHistoryResponse, ScoreWithAsset } from '@/types';

interface UseSignalDetailReturn {
  signal: ScoreDetail | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

interface UseSignalHistoryReturn {
  history: ScoreDetail[];
  symbol: string;
  count: number;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

interface UseHighSignalsReturn {
  signals: ScoreWithAsset[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

/**
 * Hook para detalhes de um sinal específico
 */
export function useSignalDetail(symbol: string): UseSignalDetailReturn {
  const [signal, setSignal] = useState<ScoreDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSignal = useCallback(async () => {
    if (!symbol) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await api.signals.detail(symbol);
      setSignal(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar sinal';
      setError(message);
      setSignal(null);
    } finally {
      setIsLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    fetchSignal();
  }, [fetchSignal]);

  return {
    signal,
    isLoading,
    error,
    refresh: fetchSignal,
  };
}

/**
 * Hook para histórico de sinais
 */
export function useSignalHistory(
  symbol: string,
  hours: number = 24
): UseSignalHistoryReturn {
  const [data, setData] = useState<ScoreHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!symbol) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.signals.history(symbol, hours);
      setData(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar histórico';
      setError(message);
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, hours]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    history: data?.scores || [],
    symbol: data?.symbol || symbol,
    count: data?.count || 0,
    isLoading,
    error,
    refresh: fetchHistory,
  };
}

/**
 * Hook para sinais com score alto
 */
export function useHighSignals(threshold: number = 70): UseHighSignalsReturn {
  const [signals, setSignals] = useState<ScoreWithAsset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHighSignals = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await api.signals.high(threshold);
      setSignals(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar sinais';
      setError(message);
      setSignals([]);
    } finally {
      setIsLoading(false);
    }
  }, [threshold]);

  useEffect(() => {
    fetchHighSignals();
  }, [fetchHighSignals]);

  return {
    signals,
    isLoading,
    error,
    refresh: fetchHighSignals,
  };
}

/**
 * Hook para monitorar mudanças de score
 */
export function useScoreChange(
  currentScore: number,
  previousScore: number | null
): {
  hasChanged: boolean;
  direction: 'up' | 'down' | 'none';
  difference: number;
} {
  if (previousScore === null) {
    return { hasChanged: false, direction: 'none', difference: 0 };
  }

  const difference = currentScore - previousScore;
  const hasChanged = Math.abs(difference) > 0.5; // Threshold mínimo

  let direction: 'up' | 'down' | 'none' = 'none';
  if (difference > 0) direction = 'up';
  else if (difference < 0) direction = 'down';

  return { hasChanged, direction, difference };
}

export default useSignalDetail;
