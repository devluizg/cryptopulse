/**
 * CryptoPulse - useAlerts Hook
 * Hook para gerenciamento de alertas
 */

import { useEffect, useCallback } from 'react';
import { useAlertStore, selectFilteredAlerts, selectCriticalAlerts } from '@/store';
import { useSettingsStore } from '@/store';
import { AlertWithAsset, AlertFilter, AlertStats, AlertSeverity } from '@/types';
import { ALERTS_REFRESH_INTERVAL } from '@/lib/constants';

interface UseAlertsReturn {
  // Data
  alerts: AlertWithAsset[];
  filteredAlerts: AlertWithAsset[];
  criticalAlerts: AlertWithAsset[];
  stats: AlertStats | null;
  unreadCount: number;
  
  // State
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  
  // Filter
  filter: AlertFilter;
  
  // Actions
  refresh: () => Promise<void>;
  markAsRead: (alertIds: number[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  dismiss: (alertId: number) => Promise<void>;
  setFilter: (filter: Partial<AlertFilter>) => void;
  resetFilter: () => void;
}

interface UseAlertsOptions {
  autoFetch?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function useAlerts(options: UseAlertsOptions = {}): UseAlertsReturn {
  const {
    autoFetch = true,
    autoRefresh = true,
    refreshInterval = ALERTS_REFRESH_INTERVAL,
  } = options;

  // Store state
  const alerts = useAlertStore((state) => state.alerts);
  const stats = useAlertStore((state) => state.stats);
  const unreadCount = useAlertStore((state) => state.unreadCount);
  const isLoading = useAlertStore((state) => state.isLoading);
  const error = useAlertStore((state) => state.error);
  const lastUpdated = useAlertStore((state) => state.lastUpdated);
  const filter = useAlertStore((state) => state.filter);

  // Store actions
  const fetchAlerts = useAlertStore((state) => state.fetchAlerts);
  const fetchStats = useAlertStore((state) => state.fetchStats);
  const markAsReadAction = useAlertStore((state) => state.markAsRead);
  const markAllAsReadAction = useAlertStore((state) => state.markAllAsRead);
  const dismissAction = useAlertStore((state) => state.dismissAlert);
  const setFilterAction = useAlertStore((state) => state.setFilter);
  const resetFilterAction = useAlertStore((state) => state.resetFilter);

  // Filtered alerts
  const filteredAlerts = useAlertStore(selectFilteredAlerts);
  const criticalAlerts = useAlertStore(selectCriticalAlerts);

  // Settings
  const autoRefreshEnabled = useSettingsStore((state) => state.autoRefresh);

  // Initial fetch
  useEffect(() => {
    if (autoFetch) {
      fetchAlerts();
      fetchStats();
    }
  }, [autoFetch, fetchAlerts, fetchStats]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh || !autoRefreshEnabled) return;

    const interval = setInterval(() => {
      fetchAlerts();
      fetchStats();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, autoRefreshEnabled, refreshInterval, fetchAlerts, fetchStats]);

  // Actions
  const refresh = useCallback(async () => {
    await Promise.all([fetchAlerts(), fetchStats()]);
  }, [fetchAlerts, fetchStats]);

  const markAsRead = useCallback(
    async (alertIds: number[]) => {
      await markAsReadAction(alertIds);
    },
    [markAsReadAction]
  );

  const markAllAsRead = useCallback(async () => {
    await markAllAsReadAction();
  }, [markAllAsReadAction]);

  const dismiss = useCallback(
    async (alertId: number) => {
      await dismissAction(alertId);
    },
    [dismissAction]
  );

  const setFilter = useCallback(
    (newFilter: Partial<AlertFilter>) => {
      setFilterAction(newFilter);
    },
    [setFilterAction]
  );

  const resetFilter = useCallback(() => {
    resetFilterAction();
  }, [resetFilterAction]);

  return {
    alerts,
    filteredAlerts,
    criticalAlerts,
    stats,
    unreadCount,
    isLoading,
    error,
    lastUpdated,
    filter,
    refresh,
    markAsRead,
    markAllAsRead,
    dismiss,
    setFilter,
    resetFilter,
  };
}

// =========================================
// Additional Hooks
// =========================================

/**
 * Hook para contagem de alertas não lidos
 */
export function useUnreadCount(): number {
  return useAlertStore((state) => state.unreadCount);
}

/**
 * Hook para verificar se há alertas críticos
 */
export function useHasCriticalAlerts(): boolean {
  const criticalAlerts = useAlertStore(selectCriticalAlerts);
  return criticalAlerts.length > 0;
}

/**
 * Hook para alertas de um ativo específico
 */
export function useAssetAlerts(assetId: number): AlertWithAsset[] {
  const alerts = useAlertStore((state) => state.alerts);
  return alerts.filter((a) => a.asset_id === assetId);
}

export default useAlerts;
