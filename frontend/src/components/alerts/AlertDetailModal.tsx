/**
 * CryptoPulse - Alert Detail Modal
 */

'use client';

import * as React from 'react';
import { useEffect } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { AlertWithAsset } from '@/types';
import { formatRelativeTime, formatCurrency, formatDateTime } from '@/lib/formatters';
import { ALERT_SEVERITY_COLORS, CRYPTO_ICONS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { SeverityBadge } from '@/components/ui/badge';

interface AlertDetailModalProps {
  alert: AlertWithAsset | null;
  isOpen: boolean;
  onClose: () => void;
  onMarkRead?: (id: number) => void;
  onDismiss?: (id: number) => void;
}

export function AlertDetailModal({ alert, isOpen, onClose, onMarkRead, onDismiss }: AlertDetailModalProps) {
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose();
    }
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !alert) return null;

  const colors = ALERT_SEVERITY_COLORS[alert.severity];
  const cryptoIcon = CRYPTO_ICONS[alert.symbol] || '●';

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className={cn('w-full max-w-lg bg-crypto-dark border rounded-xl shadow-2xl', colors.border)} onClick={e => e.stopPropagation()}>
          <div className={cn('p-6 border-b', colors.border)}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center text-2xl', colors.bg)}>⚡</div>
                <div>
                  <h2 className={cn('text-lg font-bold', colors.text)}>{alert.title}</h2>
                  <p className="text-sm text-crypto-muted">{alert.alert_type}</p>
                </div>
              </div>
              <button onClick={onClose} className="p-2 text-crypto-muted hover:text-crypto-text rounded-lg hover:bg-crypto-card">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="p-6 space-y-6">
            <div className="flex items-center gap-4 p-4 bg-crypto-card/50 rounded-lg">
              <div className="w-12 h-12 rounded-full bg-crypto-border flex items-center justify-center text-xl">{cryptoIcon}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-crypto-text">{alert.symbol}</span>
                  <SeverityBadge severity={alert.severity} size="sm" />
                </div>
                <span className="text-sm text-crypto-muted">{alert.asset_name}</span>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-crypto-muted mb-2">Mensagem</h4>
              <p className="text-crypto-text">{alert.message}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {alert.score_at_trigger && (
                <div className="p-3 bg-crypto-darker rounded-lg">
                  <p className="text-xs text-crypto-muted">Score</p>
                  <p className="text-sm font-medium text-crypto-text">{alert.score_at_trigger.toFixed(1)}</p>
                </div>
              )}
              {alert.price_at_trigger && (
                <div className="p-3 bg-crypto-darker rounded-lg">
                  <p className="text-xs text-crypto-muted">Preço</p>
                  <p className="text-sm font-medium text-crypto-text">{formatCurrency(alert.price_at_trigger)}</p>
                </div>
              )}
            </div>

            <p className="text-xs text-crypto-muted">Criado {formatRelativeTime(alert.created_at)}</p>
          </div>

          <div className="p-6 border-t border-crypto-border flex items-center justify-between gap-3">
            <div className="flex gap-2">
              {!alert.is_read && onMarkRead && (
                <Button variant="outline" onClick={() => { onMarkRead(alert.id); onClose(); }}>Marcar como lido</Button>
              )}
            </div>
            <Link href={`/asset/${alert.symbol}`} onClick={onClose}>
              <Button variant="primary">Analisar {alert.symbol}</Button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}

export default AlertDetailModal;
