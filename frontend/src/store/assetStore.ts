/**
 * CryptoPulse - Asset Store
 * Estado global para ativos e scores
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import {
  AssetWithScore,
  ScoreWithAsset,
  DashboardResponse,
  DashboardStats,
  AssetFilter,
  ScoreStatus,
} from '@/types';
import { api } from '@/lib/api';

// =========================================
// Types
// =========================================

interface AssetState {
  // Data
  assets: ScoreWithAsset[];
  stats: DashboardStats;
  selectedAsset: ScoreWithAsset | null;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  
  // Filters
  filter: AssetFilter;
  
  // Actions
  fetchDashboard: () => Promise<void>;
  fetchAsset: (symbol: string) => Promise<void>;
  setFilter: (filter: Partial<AssetFilter>) => void;
  resetFilter: () => void;
  setSelectedAsset: (asset: ScoreWithAsset | null) => void;
  updateAssetScore: (assetId: number, newScore: number, status: ScoreStatus) => void;
  clearError: () => void;
}

// =========================================
// Initial State
// =========================================

const initialFilter: AssetFilter = {
  status: 'all',
  search: '',
  sortBy: 'score',
  sortOrder: 'desc',
};

const initialStats: DashboardStats = {
  totalAssets: 0,
  highCount: 0,
  attentionCount: 0,
  lowCount: 0,
};

// =========================================
// Store
// =========================================

export const useAssetStore = create<AssetState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial Data
      assets: [],
      stats: initialStats,
      selectedAsset: null,
      
      // Initial UI State
      isLoading: false,
      error: null,
      lastUpdated: null,
      
      // Initial Filters
      filter: initialFilter,

      // =========================================
      // Actions
      // =========================================

      fetchDashboard: async () => {
        set({ isLoading: true, error: null });

        try {
          const data: DashboardResponse = await api.signals.dashboard();

          set({
            assets: data.assets,
            stats: {
              totalAssets: data.total_assets,
              highCount: data.high_count,
              attentionCount: data.attention_count,
              lowCount: data.low_count,
            },
            lastUpdated: new Date(data.updated_at),
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Erro ao carregar dashboard';
          set({ error: message, isLoading: false });
        }
      },

      fetchAsset: async (symbol: string) => {
        set({ isLoading: true, error: null });

        try {
          const data = await api.signals.detail(symbol);
          
          // Buscar informações do asset
          const assetData = await api.assets.get(symbol);
          
          const scoreWithAsset: ScoreWithAsset = {
            ...data,
            symbol: assetData.symbol,
            asset_name: assetData.name,
          };

          set({
            selectedAsset: scoreWithAsset,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Erro ao carregar ativo';
          set({ error: message, isLoading: false, selectedAsset: null });
        }
      },

      setFilter: (newFilter: Partial<AssetFilter>) => {
        set((state) => ({
          filter: { ...state.filter, ...newFilter },
        }));
      },

      resetFilter: () => {
        set({ filter: initialFilter });
      },

      setSelectedAsset: (asset: ScoreWithAsset | null) => {
        set({ selectedAsset: asset });
      },

      updateAssetScore: (assetId: number, newScore: number, status: ScoreStatus) => {
        set((state) => ({
          assets: state.assets.map((asset) =>
            asset.asset_id === assetId
              ? { ...asset, explosion_score: newScore, status }
              : asset
          ),
        }));
      },

      clearError: () => {
        set({ error: null });
      },
    })),
    { name: 'asset-store' }
  )
);

// =========================================
// Selectors
// =========================================

export const selectFilteredAssets = (state: AssetState): ScoreWithAsset[] => {
  let filtered = [...state.assets];
  const { filter } = state;

  // Filter by status
  if (filter.status && filter.status !== 'all') {
    filtered = filtered.filter((asset) => asset.status === filter.status);
  }

  // Filter by search
  if (filter.search) {
    const search = filter.search.toLowerCase();
    filtered = filtered.filter(
      (asset) =>
        asset.symbol.toLowerCase().includes(search) ||
        asset.asset_name.toLowerCase().includes(search)
    );
  }

  // Sort
  if (filter.sortBy) {
    filtered.sort((a, b) => {
      let aVal: number | string;
      let bVal: number | string;

      switch (filter.sortBy) {
        case 'score':
          aVal = a.explosion_score;
          bVal = b.explosion_score;
          break;
        case 'name':
          aVal = a.symbol;
          bVal = b.symbol;
          break;
        case 'change':
          aVal = a.price_change_24h || 0;
          bVal = b.price_change_24h || 0;
          break;
        default:
          return 0;
      }

      if (aVal < bVal) return filter.sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return filter.sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

  return filtered;
};

export const selectHighScoreAssets = (state: AssetState): ScoreWithAsset[] => {
  return state.assets.filter((asset) => asset.status === 'high');
};

export const selectAssetBySymbol = (state: AssetState, symbol: string): ScoreWithAsset | undefined => {
  return state.assets.find((asset) => asset.symbol === symbol);
};

// =========================================
// Export
// =========================================

export default useAssetStore;
