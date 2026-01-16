/**
 * CryptoPulse - useAssets Hook
 * Hook para gerenciamento de ativos
 */

import { useEffect, useCallback, useMemo } from 'react';
import { useAssetStore, selectFilteredAssets } from '@/store';
import { useSettingsStore } from '@/store';
import { ScoreWithAsset, AssetFilter, ScoreStatus } from '@/types';

interface UseAssetsReturn {
  // Data
  assets: ScoreWithAsset[];
  filteredAssets: ScoreWithAsset[];
  selectedAsset: ScoreWithAsset | null;
  stats: {
    totalAssets: number;
    highCount: number;
    attentionCount: number;
    lowCount: number;
  };
  
  // State
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  
  // Filter
  filter: AssetFilter;
  
  // Actions
  refresh: () => Promise<void>;
  setFilter: (filter: Partial<AssetFilter>) => void;
  resetFilter: () => void;
  selectAsset: (symbol: string) => Promise<void>;
  clearSelection: () => void;
  getAssetBySymbol: (symbol: string) => ScoreWithAsset | undefined;
}

interface UseAssetsOptions {
  autoFetch?: boolean;
  autoRefresh?: boolean;
}

export function useAssets(options: UseAssetsOptions = {}): UseAssetsReturn {
  const { autoFetch = true, autoRefresh = true } = options;
  
  // Store state
  const assets = useAssetStore((state) => state.assets);
  const stats = useAssetStore((state) => state.stats);
  const selectedAsset = useAssetStore((state) => state.selectedAsset);
  const isLoading = useAssetStore((state) => state.isLoading);
  const error = useAssetStore((state) => state.error);
  const lastUpdated = useAssetStore((state) => state.lastUpdated);
  const filter = useAssetStore((state) => state.filter);
  
  // Store actions
  const fetchDashboard = useAssetStore((state) => state.fetchDashboard);
  const fetchAsset = useAssetStore((state) => state.fetchAsset);
  const setFilterAction = useAssetStore((state) => state.setFilter);
  const resetFilterAction = useAssetStore((state) => state.resetFilter);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  
  // Settings
  const refreshInterval = useSettingsStore((state) => state.refreshInterval);
  const autoRefreshEnabled = useSettingsStore((state) => state.autoRefresh);
  
  // Filtered assets
  const filteredAssets = useAssetStore(selectFilteredAssets);

  // Initial fetch
  useEffect(() => {
    if (autoFetch && assets.length === 0) {
      fetchDashboard();
    }
  }, [autoFetch, assets.length, fetchDashboard]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh || !autoRefreshEnabled) return;

    const interval = setInterval(() => {
      fetchDashboard();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, autoRefreshEnabled, refreshInterval, fetchDashboard]);

  // Actions
  const refresh = useCallback(async () => {
    await fetchDashboard();
  }, [fetchDashboard]);

  const setFilter = useCallback(
    (newFilter: Partial<AssetFilter>) => {
      setFilterAction(newFilter);
    },
    [setFilterAction]
  );

  const resetFilter = useCallback(() => {
    resetFilterAction();
  }, [resetFilterAction]);

  const selectAsset = useCallback(
    async (symbol: string) => {
      await fetchAsset(symbol);
    },
    [fetchAsset]
  );

  const clearSelection = useCallback(() => {
    setSelectedAsset(null);
  }, [setSelectedAsset]);

  const getAssetBySymbol = useCallback(
    (symbol: string): ScoreWithAsset | undefined => {
      return assets.find((a) => a.symbol === symbol);
    },
    [assets]
  );

  return {
    assets,
    filteredAssets,
    selectedAsset,
    stats,
    isLoading,
    error,
    lastUpdated,
    filter,
    refresh,
    setFilter,
    resetFilter,
    selectAsset,
    clearSelection,
    getAssetBySymbol,
  };
}

// =========================================
// Additional Hooks
// =========================================

/**
 * Hook para obter apenas ativos com score alto
 */
export function useHighScoreAssets(): ScoreWithAsset[] {
  return useAssetStore((state) =>
    state.assets.filter((a) => a.status === 'high')
  );
}

/**
 * Hook para obter um ativo específico
 */
export function useAsset(symbol: string): {
  asset: ScoreWithAsset | undefined;
  isLoading: boolean;
} {
  const assets = useAssetStore((state) => state.assets);
  const isLoading = useAssetStore((state) => state.isLoading);
  
  const asset = useMemo(
    () => assets.find((a) => a.symbol === symbol),
    [assets, symbol]
  );
  
  return { asset, isLoading };
}

/**
 * Hook para estatísticas do dashboard
 */
export function useDashboardStats() {
  return useAssetStore((state) => state.stats);
}

export default useAssets;
