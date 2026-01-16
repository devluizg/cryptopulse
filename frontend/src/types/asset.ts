/**
 * CryptoPulse - Asset Types
 * Tipos relacionados a ativos/criptomoedas
 */

export interface Asset {
  id: number;
  symbol: string;
  name: string;
  coingecko_id: string | null;
  binance_symbol: string | null;
  is_active: boolean;
  priority: number;
  description: string | null;
  created_at: string;
}

export interface Score {
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
  calculated_at: string;
}

export interface AssetWithScore extends Asset {
  latest_score: Score | null;
}

export type ScoreStatus = 'high' | 'attention' | 'low';

export interface ScoreComponent {
  name: string;
  key: keyof Pick<Score, 
    'whale_accumulation_score' | 
    'exchange_netflow_score' | 
    'volume_anomaly_score' | 
    'oi_pressure_score' | 
    'narrative_momentum_score'
  >;
  value: number;
  description: string;
  icon: string;
}

export interface AssetListResponse {
  items: AssetWithScore[];
  total: number;
}

export interface AssetFilter {
  status?: ScoreStatus | 'all';
  search?: string;
  sortBy?: 'score' | 'name' | 'change';
  sortOrder?: 'asc' | 'desc';
}
