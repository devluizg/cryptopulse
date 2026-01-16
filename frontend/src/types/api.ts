/**
 * CryptoPulse - API Types
 * Tipos relacionados a requisições e respostas da API
 */

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: ApiError;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  version: string;
  database: 'connected' | 'disconnected';
  redis: 'connected' | 'disconnected';
  uptime: number;
}

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface RequestConfig {
  method: HttpMethod;
  url: string;
  params?: Record<string, string | number | boolean>;
  data?: unknown;
  headers?: Record<string, string>;
}

export interface WebSocketMessage<T = unknown> {
  type: 'score_update' | 'alert' | 'price_update' | 'connection';
  payload: T;
  timestamp: string;
}

export interface ScoreUpdatePayload {
  asset_id: number;
  symbol: string;
  old_score: number;
  new_score: number;
  status: string;
}

export interface PriceUpdatePayload {
  asset_id: number;
  symbol: string;
  price: number;
  change_24h: number;
}
