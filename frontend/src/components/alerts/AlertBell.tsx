/**
 * CryptoPulse - Alert Bell Component
 * Sino de notificações com dropdown
 */

'use client';

import * as React from 'react';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAlerts } from '@/hooks/useAlerts';
import { AlertWithAsset } from '@/types';
import { formatRelativeTime } from '@/lib/formatters';
import { ALERT_SEVERITY_COLORS, CRYPTO_ICONS } from '@/lib/constants';
import { Button } from '@/components/ui/button';

interface AlertBellProps {
  className?: string;
}

export function AlertBell({ className }: AlertBellProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const {
    alerts,
    unreadCount,
    criticalAlerts,
    isLoading,
    markAsRead,
    markAllAsRead,
  } = useAlerts({ autoRefresh: true });

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsOpen(false);
    }
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const recentAlerts = alerts.slice(0, 5);
  const hasCritical = criticalAlerts.length > 0;

  const handleAlertClick = async (alert: AlertWithAsset) => {
    if (!alert.is_read) await markAsRead([alert.id]);
    setIsOpen(false);
    router.push(`/asset/${alert.symbol}`);
  };

  return (
    <div className={cn('relative', className)} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'relative p-2 rounded-lg transition-colors',
          'text-crypto-muted hover:text-crypto-text hover:bg-crypto-card/50',
          isOpen && 'bg-crypto-card text-crypto-text',
          hasCritical && 'animate-pulse'
        )}
        aria-label={`${unreadCount} alertas não lidos`}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unreadCount > 0 && (
          <span className={cn(
            'absolute -top-1 -right-1 flex items-center justify-center',
            'min-w-[20px] h-5 px-1 text-xs font-bold rounded-full',
            hasCritical ? 'bg-red-500 text-white' : 'bg-score-attention text-crypto-dark'
          )}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className={cn(
          'absolute right-0 mt-2 w-96 max-w-[calc(100vw-2rem)]',
          'bg-crypto-dark border border-crypto-border rounded-xl shadow-2xl',
          'animate-in fade-in-0 zoom-in-95 duration-200'
        )}>
          <div className="flex items-center justify-between p-4 border-b border-crypto-border">
            <div>
              <h3 className="font-semibold text-crypto-text">Alertas</h3>
              <p className="text-xs text-crypto-muted">
                {unreadCount > 0 ? `${unreadCount} não lido${unreadCount !== 1 ? 's' : ''}` : 'Todos lidos'}
              </p>
            </div>
            {unreadCount > 0 && (
              <button onClick={markAllAsRead} className="text-xs text-score-high hover:underline">
                Marcar todos como lido
              </button>
            )}
          </div>

          <div className="max-h-[400px] overflow-y-auto">
            {isLoading && recentAlerts.length === 0 ? (
              <div className="p-8 text-center">
                <div className="w-6 h-6 border-2 border-score-high border-t-transparent rounded-full animate-spin mx-auto" />
              </div>
            ) : recentAlerts.length > 0 ? (
              <div className="divide-y divide-crypto-border">
                {recentAlerts.map((alert) => (
                  <AlertDropdownItem key={alert.id} alert={alert} onClick={() => handleAlertClick(alert)} />
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <p className="text-sm text-crypto-muted">Nenhum alerta recente</p>
              </div>
            )}
          </div>

          {alerts.length > 0 && (
            <div className="p-3 border-t border-crypto-border">
              <Button variant="ghost" className="w-full justify-center" onClick={() => { setIsOpen(false); router.push('/alerts'); }}>
                Ver todos os alertas
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AlertDropdownItem({ alert, onClick }: { alert: AlertWithAsset; onClick: () => void }) {
  const colors = ALERT_SEVERITY_COLORS[alert.severity];
  const cryptoIcon = CRYPTO_ICONS[alert.symbol] || '●';

  return (
    <button onClick={onClick} className={cn('w-full p-4 text-left transition-colors hover:bg-crypto-card/50', !alert.is_read && 'bg-crypto-card/30')}>
      <div className="flex items-start gap-3">
        <div className={cn('flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center', colors.bg)}>
          {cryptoIcon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn('font-medium text-sm', colors.text)}>{alert.title}</span>
            {!alert.is_read && <span className="w-2 h-2 bg-score-high rounded-full" />}
          </div>
          <p className="text-xs text-crypto-muted line-clamp-2">{alert.message}</p>
          <span className="text-xs text-crypto-muted">{formatRelativeTime(alert.created_at)}</span>
        </div>
      </div>
    </button>
  );
}

export default AlertBell;
