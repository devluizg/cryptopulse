/**
 * CryptoPulse - AlertList Component
 * Lista de alertas com filtros
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { AlertWithAsset, AlertFilter, AlertSeverity } from '@/types';
import { AlertCard, MiniAlertCard } from './AlertCard';
import { NoAlertsState } from '@/components/common/EmptyState';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

interface AlertListProps {
  alerts: AlertWithAsset[];
  isLoading?: boolean;
  filter?: AlertFilter;
  onFilterChange?: (filter: Partial<AlertFilter>) => void;
  onMarkRead?: (id: number) => void;
  onMarkAllRead?: () => void;
  onDismiss?: (id: number) => void;
  compact?: boolean;
  showFilters?: boolean;
  className?: string;
}

export function AlertList({
  alerts,
  isLoading,
  filter,
  onFilterChange,
  onMarkRead,
  onMarkAllRead,
  onDismiss,
  compact = false,
  showFilters = true,
  className,
}: AlertListProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className={cn('space-y-3', className)}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-4 bg-crypto-card rounded-lg">
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-3 w-1/2 mb-3" />
            <Skeleton className="h-10 w-full" />
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (alerts.length === 0) {
    return <NoAlertsState />;
  }

  const unreadCount = alerts.filter((a) => !a.is_read).length;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header with filters */}
      {showFilters && (
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          {/* Filter buttons */}
          <div className="flex items-center gap-2">
            <FilterButton
              active={!filter?.unreadOnly}
              onClick={() => onFilterChange?.({ unreadOnly: false })}
            >
              Todos ({alerts.length})
            </FilterButton>
            <FilterButton
              active={filter?.unreadOnly}
              onClick={() => onFilterChange?.({ unreadOnly: true })}
            >
              Não lidos ({unreadCount})
            </FilterButton>
          </div>

          {/* Severity filter */}
          <div className="flex items-center gap-2">
            <SeverityFilter
              value={filter?.severity || 'all'}
              onChange={(severity) => onFilterChange?.({ severity })}
            />
            
            {unreadCount > 0 && onMarkAllRead && (
              <Button variant="outline" size="sm" onClick={onMarkAllRead}>
                Marcar todos como lido
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Alert list */}
      <div className="space-y-3">
        {alerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onMarkRead={onMarkRead}
            onDismiss={onDismiss}
            compact={compact}
          />
        ))}
      </div>
    </div>
  );
}

// Filter button component
interface FilterButtonProps {
  active?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

function FilterButton({ active, onClick, children }: FilterButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
        active
          ? 'bg-crypto-card text-crypto-text'
          : 'text-crypto-muted hover:text-crypto-text hover:bg-crypto-card/50'
      )}
    >
      {children}
    </button>
  );
}

// Severity filter dropdown
interface SeverityFilterProps {
  value: AlertSeverity | 'all';
  onChange: (value: AlertSeverity | 'all') => void;
}

function SeverityFilter({ value, onChange }: SeverityFilterProps) {
  const options: { value: AlertSeverity | 'all'; label: string }[] = [
    { value: 'all', label: 'Todas severidades' },
    { value: 'critical', label: '🔴 Crítico' },
    { value: 'warning', label: '🟡 Atenção' },
    { value: 'info', label: '🔵 Info' },
  ];

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as AlertSeverity | 'all')}
      className="px-3 py-1.5 text-sm bg-crypto-card border border-crypto-border rounded-lg text-crypto-text focus:outline-none focus:ring-2 focus:ring-score-high/50"
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

// Dropdown de alertas para o header
interface AlertDropdownProps {
  alerts: AlertWithAsset[];
  unreadCount: number;
  onMarkRead?: (id: number) => void;
  onViewAll?: () => void;
}

export function AlertDropdown({
  alerts,
  unreadCount,
  onMarkRead,
  onViewAll,
}: AlertDropdownProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const recentAlerts = alerts.slice(0, 5);

  return (
    <div className="relative">
      {/* Trigger button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-crypto-muted hover:text-crypto-text transition-colors"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center text-xs font-bold bg-score-low text-white rounded-full">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-crypto-dark border border-crypto-border rounded-lg shadow-xl z-50">
            <div className="p-3 border-b border-crypto-border">
              <h3 className="font-semibold text-crypto-text">Alertas</h3>
              <p className="text-xs text-crypto-muted">
                {unreadCount} não lido{unreadCount !== 1 ? 's' : ''}
              </p>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {recentAlerts.length > 0 ? (
                recentAlerts.map((alert) => (
                  <MiniAlertCard
                    key={alert.id}
                    alert={alert}
                    onClick={() => {
                      onMarkRead?.(alert.id);
                      setIsOpen(false);
                    }}
                  />
                ))
              ) : (
                <div className="p-4 text-center text-crypto-muted text-sm">
                  Nenhum alerta recente
                </div>
              )}
            </div>

            {alerts.length > 0 && (
              <div className="p-2 border-t border-crypto-border">
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => {
                    onViewAll?.();
                    setIsOpen(false);
                  }}
                >
                  Ver todos os alertas
                </Button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default AlertList;
