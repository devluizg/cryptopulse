/**
 * CryptoPulse - Signal Types
 * Tipos relacionados a sinais e scores
 */

import { ScoreStatus } from './asset';

export interface ScoreDetail {
  id: number;
  asset_id: number;
  explosion_score: number;
  status: ScoreStatus;
  whale_accumulation_score: number;
  exchange_netflow_score: number;
  volume_anomaly_score: number;
  oi_pressure_score: number;
  narrative_momentum_score: number;
  price_usd: number | null;
  price_change_24h: number | null;
  volume_24h: number | null;
  calculation_details: Record<string, unknown> | null;
  main_drivers: string | null;
  calculated_at: string;
}

export interface ScoreWithAsset extends ScoreDetail {
  symbol: string;
  asset_name: string;
}

export interface ScoreHistoryResponse {
  symbol: string;
  scores: ScoreDetail[];
  count: number;
}

export interface DashboardResponse {
  total_assets: number;
  high_count: number;
  attention_count: number;
  low_count: number;
  assets: ScoreWithAsset[];
  updated_at: string;
}

export interface DashboardStats {
  totalAssets: number;
  highCount: number;
  attentionCount: number;
  lowCount: number;
}

export interface SignalFilter {
  minScore?: number;
  maxScore?: number;
  status?: ScoreStatus | 'all';
}

export interface ScoreHistoryPoint {
  timestamp: string;
  score: number;
  status: ScoreStatus;
}

export interface IndicatorBreakdown {
  whale: number;
  netflow: number;
  volume: number;
  openInterest: number;
  narrative: number;
}
