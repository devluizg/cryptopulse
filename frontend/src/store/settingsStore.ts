/**
 * CryptoPulse - Settings Store
 * Estado global para configurações do usuário
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { AlertConfig, AlertSeverity } from '@/types';

// =========================================
// Types
// =========================================

type Theme = 'dark' | 'light' | 'system';
type RefreshInterval = 15000 | 30000 | 60000 | 300000;

interface SettingsState {
  // Theme
  theme: Theme;
  
  // Dashboard Settings
  refreshInterval: RefreshInterval;
  autoRefresh: boolean;
  showPriceChange: boolean;
  showVolume: boolean;
  compactMode: boolean;
  
  // Alert Settings
  alertConfig: AlertConfig;
  
  // Notification Settings
  soundEnabled: boolean;
  browserNotifications: boolean;
  
  // Display Settings
  currency: 'USD' | 'BRL' | 'EUR';
  locale: string;
  
  // Actions
  setTheme: (theme: Theme) => void;
  setRefreshInterval: (interval: RefreshInterval) => void;
  setAutoRefresh: (enabled: boolean) => void;
  setShowPriceChange: (show: boolean) => void;
  setShowVolume: (show: boolean) => void;
  setCompactMode: (compact: boolean) => void;
  setAlertConfig: (config: Partial<AlertConfig>) => void;
  setSoundEnabled: (enabled: boolean) => void;
  setBrowserNotifications: (enabled: boolean) => void;
  setCurrency: (currency: 'USD' | 'BRL' | 'EUR') => void;
  resetSettings: () => void;
}

// =========================================
// Initial State
// =========================================

const initialAlertConfig: AlertConfig = {
  scoreThreshold: 70,
  enablePush: true,
  enableEmail: false,
  enableSound: true,
  severityFilter: ['warning', 'critical'],
};

const initialState = {
  theme: 'dark' as Theme,
  refreshInterval: 30000 as RefreshInterval,
  autoRefresh: true,
  showPriceChange: true,
  showVolume: true,
  compactMode: false,
  alertConfig: initialAlertConfig,
  soundEnabled: true,
  browserNotifications: false,
  currency: 'USD' as const,
  locale: 'pt-BR',
};

// =========================================
// Store
// =========================================

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        // =========================================
        // Actions
        // =========================================

        setTheme: (theme: Theme) => {
          set({ theme });
          
          // Apply theme to document
          if (typeof window !== 'undefined') {
            const root = window.document.documentElement;
            root.classList.remove('light', 'dark');
            
            if (theme === 'system') {
              const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light';
              root.classList.add(systemTheme);
            } else {
              root.classList.add(theme);
            }
          }
        },

        setRefreshInterval: (interval: RefreshInterval) => {
          set({ refreshInterval: interval });
        },

        setAutoRefresh: (enabled: boolean) => {
          set({ autoRefresh: enabled });
        },

        setShowPriceChange: (show: boolean) => {
          set({ showPriceChange: show });
        },

        setShowVolume: (show: boolean) => {
          set({ showVolume: show });
        },

        setCompactMode: (compact: boolean) => {
          set({ compactMode: compact });
        },

        setAlertConfig: (config: Partial<AlertConfig>) => {
          set((state) => ({
            alertConfig: { ...state.alertConfig, ...config },
          }));
        },

        setSoundEnabled: (enabled: boolean) => {
          set({ soundEnabled: enabled });
        },

        setBrowserNotifications: async (enabled: boolean) => {
          if (enabled && typeof window !== 'undefined' && 'Notification' in window) {
            const permission = await Notification.requestPermission();
            set({ browserNotifications: permission === 'granted' });
          } else {
            set({ browserNotifications: false });
          }
        },

        setCurrency: (currency: 'USD' | 'BRL' | 'EUR') => {
          set({ currency });
        },

        resetSettings: () => {
          set(initialState);
        },
      }),
      {
        name: 'cryptopulse-settings',
        partialize: (state) => ({
          theme: state.theme,
          refreshInterval: state.refreshInterval,
          autoRefresh: state.autoRefresh,
          showPriceChange: state.showPriceChange,
          showVolume: state.showVolume,
          compactMode: state.compactMode,
          alertConfig: state.alertConfig,
          soundEnabled: state.soundEnabled,
          browserNotifications: state.browserNotifications,
          currency: state.currency,
          locale: state.locale,
        }),
      }
    ),
    { name: 'settings-store' }
  )
);

// =========================================
// Selectors
// =========================================

export const selectTheme = (state: SettingsState): Theme => state.theme;

export const selectRefreshInterval = (state: SettingsState): RefreshInterval =>
  state.refreshInterval;

export const selectAlertConfig = (state: SettingsState): AlertConfig =>
  state.alertConfig;

// =========================================
// Export
// =========================================

export default useSettingsStore;
