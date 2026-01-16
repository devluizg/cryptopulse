export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertType = 'score_threshold' | 'score_change' | 'whale_activity' | 'volume_spike' | 'price_change';

export interface Alert {
  id: number;
  asset_id: number;
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  score_at_trigger: number | null;
  price_at_trigger: number | null;
  is_read: boolean;
  read_at: string | null;
  is_dismissed: boolean;
  dismissed_at: string | null;
  created_at: string;
}

export interface AlertWithAsset extends Alert {
  symbol: string;
  asset_name: string;
}

export interface AlertListResponse {
  items: AlertWithAsset[];
  total: number;
  unread_count: number;
}

export interface AlertStats {
  total: number;
  unread: number;
  today_count: number;
  by_severity: { info: number; warning: number; critical: number };
  by_type: Record<AlertType, number>;
}

export interface AlertFilter {
  unreadOnly: boolean;
  severity: AlertSeverity | 'all';
  type: AlertType | 'all';
  assetId?: number;
}

export interface AlertConfig {
  scoreThreshold: number;
  enablePush: boolean;
  enableEmail: boolean;
  enableSound: boolean;
  severityFilter: AlertSeverity[];
}

export interface MarkReadRequest {
  alert_ids: number[];
}
