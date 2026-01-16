/**
 * CryptoPulse - Constants
 * Constantes globais da aplicação
 */

// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const API_PREFIX = process.env.NEXT_PUBLIC_API_PREFIX || '/api/v1';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

// App Info
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'CryptoPulse';
export const APP_VERSION = process.env.NEXT_PUBLIC_APP_VERSION || '0.1.0';

// Feature Flags
export const ENABLE_WEBSOCKET = process.env.NEXT_PUBLIC_ENABLE_WEBSOCKET === 'true';
export const ENABLE_NOTIFICATIONS = process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS === 'true';

// Refresh Intervals (ms)
export const DASHBOARD_REFRESH_INTERVAL = parseInt(
  process.env.NEXT_PUBLIC_DASHBOARD_REFRESH_INTERVAL || '30000'
);
export const ALERTS_REFRESH_INTERVAL = parseInt(
  process.env.NEXT_PUBLIC_ALERTS_REFRESH_INTERVAL || '15000'
);

// Score Thresholds
export const SCORE_THRESHOLDS = {
  HIGH: 70,
  ATTENTION: 40,
} as const;

// Score Status Labels
export const SCORE_STATUS_LABELS = {
  high: 'Zona de Explosão',
  attention: 'Atenção',
  low: 'Baixo Potencial',
} as const;

// Score Status Colors (Tailwind classes)
export const SCORE_STATUS_COLORS = {
  high: {
    bg: 'bg-score-high/10',
    border: 'border-score-high/30',
    text: 'text-score-high',
    glow: 'shadow-score-high/20',
  },
  attention: {
    bg: 'bg-score-attention/10',
    border: 'border-score-attention/30',
    text: 'text-score-attention',
    glow: 'shadow-score-attention/20',
  },
  low: {
    bg: 'bg-score-low/10',
    border: 'border-score-low/30',
    text: 'text-score-low',
    glow: 'shadow-score-low/20',
  },
} as const;

// Alert Severity Colors
export const ALERT_SEVERITY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
  },
  low: {
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    text: 'text-green-400',
  },
  medium: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
  },
  warning: {
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    text: 'text-orange-400',
  },
  high: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
  },
  critical: {
    bg: 'bg-red-600/10',
    border: 'border-red-600/30',
    text: 'text-red-500',
  },
};

// Indicator Labels
export const INDICATOR_LABELS = {
  whale_accumulation_score: {
    name: 'Whale Activity',
    description: 'Atividade de grandes investidores',
    icon: '🐋',
  },
  exchange_netflow_score: {
    name: 'Exchange Netflow',
    description: 'Fluxo líquido para exchanges',
    icon: '📊',
  },
  volume_anomaly_score: {
    name: 'Volume Anomaly',
    description: 'Anomalias no volume de negociação',
    icon: '📈',
  },
  oi_pressure_score: {
    name: 'Open Interest',
    description: 'Pressão de contratos em aberto',
    icon: '⚡',
  },
  narrative_momentum_score: {
    name: 'Narrative',
    description: 'Momentum de notícias e eventos',
    icon: '📰',
  },
} as const;

// Crypto Icons (símbolos conhecidos)
export const CRYPTO_ICONS: Record<string, string> = {
  BTC: '₿',
  ETH: 'Ξ',
  SOL: '◎',
  BNB: '🔶',
  XRP: '✕',
  ADA: '₳',
  AVAX: '🔺',
  MATIC: '⬡',
  DOT: '●',
  LINK: '⬡',
};

// Default pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Chart colors
export const CHART_COLORS = {
  primary: '#22c55e',
  secondary: '#3b82f6',
  tertiary: '#8b5cf6',
  quaternary: '#f59e0b',
  negative: '#ef4444',
  neutral: '#6b7280',
  grid: '#30363d',
  background: '#161b22',
};

// Time formats
export const TIME_FORMATS = {
  full: 'dd/MM/yyyy HH:mm:ss',
  date: 'dd/MM/yyyy',
  time: 'HH:mm:ss',
  short: 'dd/MM HH:mm',
  relative: 'relative',
} as const;
