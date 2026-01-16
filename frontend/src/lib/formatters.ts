import { formatDistanceToNow, format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return 'Data inválida';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true, locale: ptBR });
  } catch { return 'Data inválida'; }
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return 'Data inválida';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, "dd/MM/yyyy 'às' HH:mm", { locale: ptBR });
  } catch { return 'Data inválida'; }
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return 'Data inválida';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'dd/MM/yyyy', { locale: ptBR });
  } catch { return 'Data inválida'; }
}

export function formatCurrency(value: number | null | undefined, currency: string = 'USD'): string {
  if (value === null || value === undefined) return '$0.00';
  try {
    return new Intl.NumberFormat(currency === 'BRL' ? 'pt-BR' : 'en-US', {
      style: 'currency', currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: value < 1 ? 6 : 2,
    }).format(value);
  } catch { return `${currency} ${(value ?? 0).toFixed(2)}`; }
}

export function formatCompactNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0';
  return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(value);
}

export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return '0';
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(value);
}

export function formatPercentage(value: number | null | undefined, showSign = true): string {
  if (value === null || value === undefined) return '0.00%';
  const formatted = Math.abs(value).toFixed(2);
  if (showSign) {
    const sign = value > 0 ? '+' : value < 0 ? '-' : '';
    return `${sign}${formatted}%`;
  }
  return `${formatted}%`;
}

// Alias para compatibilidade
export function formatPercent(value: number | null | undefined, showSign = true): string {
  return formatPercentage(value, showSign);
}

export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0.0';
  return value.toFixed(1);
}

export function formatVolume(value: number | null | undefined): string {
  if (value === null || value === undefined) return '$0.00';
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(2)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(2)}K`;
  return `$${value.toFixed(2)}`;
}

export default { 
  formatRelativeTime, 
  formatDateTime, 
  formatDate, 
  formatCurrency, 
  formatCompactNumber, 
  formatNumber, 
  formatPercentage, 
  formatPercent, 
  formatScore, 
  formatVolume 
};
