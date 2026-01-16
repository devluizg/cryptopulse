/**
 * CryptoPulse - API Client
 * Cliente para comunicação com o backend
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import {
  AssetListResponse,
  AssetWithScore,
  DashboardResponse,
  ScoreDetail,
  ScoreHistoryResponse,
  AlertListResponse,
  AlertStats,
  HealthCheck,
  ApiError,
} from '@/types';
import { API_BASE_URL, API_PREFIX } from './constants';

// =========================================
// Configuração do Axios
// =========================================

const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para logs de desenvolvimento
apiClient.interceptors.request.use(
  (config) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de erros
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'Erro desconhecido',
      code: error.code,
      details: error.response?.data?.details,
    };

    if (process.env.NODE_ENV === 'development') {
      console.error('[API Error]', apiError);
    }

    return Promise.reject(apiError);
  }
);

// =========================================
// Health Check
// =========================================

export async function checkHealth(): Promise<HealthCheck> {
  const response = await axios.get<HealthCheck>(`${API_BASE_URL}/health`);
  return response.data;
}

// =========================================
// Assets API
// =========================================

export async function getAssets(activeOnly: boolean = true): Promise<AssetListResponse> {
  const response = await apiClient.get<AssetListResponse>('/assets', {
    params: { active_only: activeOnly },
  });
  return response.data;
}

export async function getAsset(symbol: string): Promise<AssetWithScore> {
  const response = await apiClient.get<AssetWithScore>(`/assets/${symbol}`);
  return response.data;
}

export async function getAssetScores(
  symbol: string,
  hours: number = 24
): Promise<ScoreDetail[]> {
  const response = await apiClient.get<ScoreDetail[]>(`/assets/${symbol}/scores`, {
    params: { hours },
  });
  return response.data;
}

export async function activateAsset(symbol: string): Promise<void> {
  await apiClient.post(`/assets/${symbol}/activate`);
}

export async function deactivateAsset(symbol: string): Promise<void> {
  await apiClient.post(`/assets/${symbol}/deactivate`);
}

// =========================================
// Signals API
// =========================================

export async function getDashboard(): Promise<DashboardResponse> {
  const response = await apiClient.get<DashboardResponse>('/signals/dashboard');
  return response.data;
}

export async function getHighSignals(threshold: number = 70): Promise<DashboardResponse['assets']> {
  const response = await apiClient.get<DashboardResponse['assets']>('/signals/high', {
    params: { threshold },
  });
  return response.data;
}

export async function getSignalDetail(symbol: string): Promise<ScoreDetail> {
  const response = await apiClient.get<ScoreDetail>(`/signals/${symbol}`);
  return response.data;
}

export async function getSignalHistory(
  symbol: string,
  hours: number = 24
): Promise<ScoreHistoryResponse> {
  const response = await apiClient.get<ScoreHistoryResponse>(`/signals/${symbol}/history`, {
    params: { hours },
  });
  return response.data;
}

// =========================================
// Alerts API
// =========================================

export async function getAlerts(options?: {
  unreadOnly?: boolean;
  severity?: string;
  limit?: number;
}): Promise<AlertListResponse> {
  const response = await apiClient.get<AlertListResponse>('/alerts', {
    params: {
      unread_only: options?.unreadOnly,
      severity: options?.severity,
      limit: options?.limit || 50,
    },
  });
  return response.data;
}

export async function getAlertStats(): Promise<AlertStats> {
  const response = await apiClient.get<AlertStats>('/alerts/stats');
  return response.data;
}

export async function markAlertsAsRead(alertIds: number[]): Promise<void> {
  // Rota correta do backend: /alerts/read-many
  await apiClient.post('/alerts/read-many', { alert_ids: alertIds });
}

export async function markAllAlertsAsRead(): Promise<void> {
  // Rota para marcar todos como lidos
  await apiClient.post('/alerts/read-all');
}

export async function dismissAlert(alertId: number): Promise<void> {
  // Rota correta: DELETE /alerts/{id}
  await apiClient.delete(`/alerts/${alertId}`);
}

// =========================================
// Generic Request Helper
// =========================================

export async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.request<T>(config);
  return response.data;
}

// =========================================
// Export client for advanced usage
// =========================================

export { apiClient };

// =========================================
// API object for convenience
// =========================================

export const api = {
  // Health
  checkHealth,

  // Assets
  assets: {
    list: getAssets,
    get: getAsset,
    scores: getAssetScores,
    activate: activateAsset,
    deactivate: deactivateAsset,
  },

  // Signals
  signals: {
    dashboard: getDashboard,
    high: getHighSignals,
    detail: getSignalDetail,
    history: getSignalHistory,
  },

  // Alerts
  alerts: {
    list: getAlerts,
    stats: getAlertStats,
    markRead: markAlertsAsRead,
    markAllRead: markAllAlertsAsRead,
    dismiss: dismissAlert,
  },
};

export default api;
