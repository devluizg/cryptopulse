/**
 * CryptoPulse - Alert Store
 * Estado global para alertas
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import {
  AlertWithAsset,
  AlertStats,
  AlertFilter,
  AlertSeverity,
} from '@/types';
import { api } from '@/lib/api';

// =========================================
// Types
// =========================================

interface AlertState {
  // Data
  alerts: AlertWithAsset[];
  stats: AlertStats | null;
  unreadCount: number;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  
  // Filters
  filter: AlertFilter;
  
  // Actions
  fetchAlerts: (options?: Partial<AlertFilter>) => Promise<void>;
  fetchStats: () => Promise<void>;
  markAsRead: (alertIds: number[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  dismissAlert: (alertId: number) => Promise<void>;
  setFilter: (filter: Partial<AlertFilter>) => void;
  resetFilter: () => void;
  addAlert: (alert: AlertWithAsset) => void;
  clearError: () => void;
}

// =========================================
// Initial State
// =========================================

const initialFilter: AlertFilter = {
  unreadOnly: false,
  severity: 'all',
  type: 'all',
};

// =========================================
// Store
// =========================================

export const useAlertStore = create<AlertState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial Data
      alerts: [],
      stats: null,
      unreadCount: 0,
      
      // Initial UI State
      isLoading: false,
      error: null,
      lastUpdated: null,
      
      // Initial Filters
      filter: initialFilter,

      // =========================================
      // Actions
      // =========================================

      fetchAlerts: async (options?: Partial<AlertFilter>) => {
        set({ isLoading: true, error: null });

        try {
          const filter = { ...get().filter, ...options };
          
          const data = await api.alerts.list({
            unreadOnly: filter.unreadOnly,
            severity: filter.severity === 'all' ? undefined : filter.severity,
            limit: 50,
          });

          set({
            alerts: data.items,
            unreadCount: data.unread_count,
            lastUpdated: new Date(),
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Erro ao carregar alertas';
          set({ error: message, isLoading: false });
        }
      },

      fetchStats: async () => {
        try {
          const stats = await api.alerts.stats();
          set({ stats, unreadCount: stats.unread });
        } catch (error) {
          console.error('Erro ao carregar estatísticas:', error);
        }
      },

      markAsRead: async (alertIds: number[]) => {
        if (alertIds.length === 0) return;
        
        try {
          await api.alerts.markRead(alertIds);

          set((state) => ({
            alerts: state.alerts.map((alert) =>
              alertIds.includes(alert.id)
                ? { ...alert, is_read: true, read_at: new Date().toISOString() }
                : alert
            ),
            unreadCount: Math.max(0, state.unreadCount - alertIds.length),
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Erro ao marcar como lido';
          console.error('[AlertStore] markAsRead error:', error);
          set({ error: message });
        }
      },

      markAllAsRead: async () => {
        try {
          // Usar a rota dedicada para marcar todos
          await api.alerts.markAllRead();

          set((state) => ({
            alerts: state.alerts.map((alert) => ({
              ...alert,
              is_read: true,
              read_at: alert.is_read ? alert.read_at : new Date().toISOString(),
            })),
            unreadCount: 0,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Erro ao marcar todos como lido';
          console.error('[AlertStore] markAllAsRead error:', error);
          set({ error: message });
        }
      },

      dismissAlert: async (alertId: number) => {
        try {
          await api.alerts.dismiss(alertId);

          set((state) => ({
            alerts: state.alerts.filter((alert) => alert.id !== alertId),
            unreadCount: state.alerts.find((a) => a.id === alertId && !a.is_read)
              ? state.unreadCount - 1
              : state.unreadCount,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Erro ao dispensar alerta';
          console.error('[AlertStore] dismissAlert error:', error);
          set({ error: message });
        }
      },

      setFilter: (newFilter: Partial<AlertFilter>) => {
        set((state) => ({
          filter: { ...state.filter, ...newFilter },
        }));
      },

      resetFilter: () => {
        set({ filter: initialFilter });
      },

      addAlert: (alert: AlertWithAsset) => {
        set((state) => ({
          alerts: [alert, ...state.alerts],
          unreadCount: state.unreadCount + 1,
        }));
      },

      clearError: () => {
        set({ error: null });
      },
    })),
    { name: 'alert-store' }
  )
);

// =========================================
// Selectors
// =========================================

export const selectFilteredAlerts = (state: AlertState): AlertWithAsset[] => {
  let filtered = [...state.alerts];
  const { filter } = state;

  // Filter by unread
  if (filter.unreadOnly) {
    filtered = filtered.filter((alert) => !alert.is_read);
  }

  // Filter by severity
  if (filter.severity && filter.severity !== 'all') {
    filtered = filtered.filter((alert) => alert.severity === filter.severity);
  }

  // Filter by type
  if (filter.type && filter.type !== 'all') {
    filtered = filtered.filter((alert) => alert.alert_type === filter.type);
  }

  // Filter by asset
  if (filter.assetId) {
    filtered = filtered.filter((alert) => alert.asset_id === filter.assetId);
  }

  return filtered;
};

export const selectUnreadAlerts = (state: AlertState): AlertWithAsset[] => {
  return state.alerts.filter((alert) => !alert.is_read);
};

export const selectAlertsBySeverity = (
  state: AlertState,
  severity: AlertSeverity
): AlertWithAsset[] => {
  return state.alerts.filter((alert) => alert.severity === severity);
};

export const selectCriticalAlerts = (state: AlertState): AlertWithAsset[] => {
  return state.alerts.filter(
    (alert) => alert.severity === 'critical' && !alert.is_read
  );
};

// =========================================
// Export
// =========================================

export default useAlertStore;
