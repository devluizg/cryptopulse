/**
 * CryptoPulse - AlertCard Component
 * Card individual de alerta
 */

'use client';

import * as React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { AlertWithAsset, AlertSeverity } from '@/types';
import { formatRelativeTime, formatCurrency } from '@/lib/formatters';
import { ALERT_SEVERITY_COLORS, CRYPTO_ICONS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { SeverityBadge } from '@/components/ui/badge';

interface AlertCardProps {
  alert: AlertWithAsset;
  onMarkRead?: (id: number) => void;
  onDismiss?: (id: number) => void;
  compact?: boolean;
  className?: string;
}

export function AlertCard({
  alert,
  onMarkRead,
  onDismiss,
  compact = false,
  className,
}: AlertCardProps) {
  const severityColors = ALERT_SEVERITY_COLORS[alert.severity];
  const cryptoIcon = CRYPTO_ICONS[alert.symbol] || '●';

  const alertIcons: Record<string, string> = {
    score_threshold: '🎯',
    score_change: '📊',
    whale_activity: '🐋',
    volume_spike: '📈',
    price_change: '💰',
  };

  return (
    <div
      className={cn(
        'p-4 rounded-lg border transition-all',
        severityColors.bg,
        severityColors.border,
        !alert.is_read && 'ring-1 ring-offset-1 ring-offset-crypto-dark',
        !alert.is_read && alert.severity === 'critical' && 'ring-red-500/50',
        !alert.is_read && alert.severity === 'warning' && 'ring-yellow-500/50',
        alert.is_read && 'opacity-60',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{alertIcons[alert.alert_type] || '⚡'}</span>
          <div>
            <h4 className={cn('font-semibold', severityColors.text)}>
              {alert.title}
            </h4>
            <div className="flex items-center gap-2 text-xs text-crypto-muted">
              <span>{formatRelativeTime(alert.created_at)}</span>
              {!alert.is_read && (
                <span className="w-2 h-2 bg-score-high rounded-full animate-pulse" />
              )}
            </div>
          </div>
        </div>
        <SeverityBadge severity={alert.severity} size="sm" />
      </div>

      {/* Asset info */}
      <Link
        href={`/asset/${alert.symbol}`}
        className="flex items-center gap-2 mb-3 hover:opacity-80 transition-opacity"
      >
        <div className="w-6 h-6 rounded-full bg-crypto-border flex items-center justify-center text-sm">
          {cryptoIcon}
        </div>
        <span className="font-medium text-crypto-text">{alert.symbol}</span>
        <span className="text-crypto-muted text-sm">{alert.asset_name}</span>
      </Link>

      {/* Message */}
      {!compact && (
        <p className="text-sm text-crypto-muted mb-3">{alert.message}</p>
      )}

      {/* Details */}
      {!compact && (alert.score_at_trigger || alert.price_at_trigger) && (
        <div className="flex items-center gap-4 text-xs text-crypto-muted mb-3">
          {alert.score_at_trigger && (
            <span>Score: <strong className="text-crypto-text">{alert.score_at_trigger.toFixed(1)}</strong></span>
          )}
          {alert.price_at_trigger && (
            <span>Preço: <strong className="text-crypto-text">{formatCurrency(alert.price_at_trigger)}</strong></span>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        {!alert.is_read && onMarkRead && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onMarkRead(alert.id)}
          >
            Marcar como lido
          </Button>
        )}
        {onDismiss && !alert.is_dismissed && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDismiss(alert.id)}
            className="text-crypto-muted hover:text-score-low"
          >
            Dispensar
          </Button>
        )}
        <Link href={`/asset/${alert.symbol}`} className="ml-auto">
          <Button variant="outline" size="sm">
            Ver ativo
          </Button>
        </Link>
      </div>
    </div>
  );
}

// Versão mini para notificações/dropdown
interface MiniAlertCardProps {
  alert: AlertWithAsset;
  onClick?: () => void;
}

export function MiniAlertCard({ alert, onClick }: MiniAlertCardProps) {
  const severityColors = ALERT_SEVERITY_COLORS[alert.severity];
  const cryptoIcon = CRYPTO_ICONS[alert.symbol] || '●';

  return (
    <div
      className={cn(
        'p-3 rounded-lg cursor-pointer transition-colors hover:bg-crypto-card',
        !alert.is_read && 'bg-crypto-card/50'
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-sm',
            severityColors.bg
          )}
        >
          {cryptoIcon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn('font-medium text-sm', severityColors.text)}>
              {alert.symbol}
            </span>
            {!alert.is_read && (
              <span className="w-1.5 h-1.5 bg-score-high rounded-full" />
            )}
          </div>
          <p className="text-xs text-crypto-muted truncate">{alert.title}</p>
          <span className="text-xs text-crypto-muted">
            {formatRelativeTime(alert.created_at)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default AlertCard;
