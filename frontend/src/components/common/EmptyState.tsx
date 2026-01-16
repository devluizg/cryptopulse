/**
 * CryptoPulse - EmptyState Component
 * Exibe estado vazio com ilustração e ação
 */

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        className
      )}
    >
      {icon ? (
        <div className="mb-4 text-crypto-muted">{icon}</div>
      ) : (
        <DefaultEmptyIcon className="mb-4" />
      )}
      
      <h3 className="text-lg font-semibold text-crypto-text mb-2">{title}</h3>
      
      {description && (
        <p className="text-sm text-crypto-muted max-w-sm mb-4">{description}</p>
      )}
      
      {action && (
        <Button onClick={action.onClick} variant="primary">
          {action.label}
        </Button>
      )}
    </div>
  );
}

// Ícone padrão
function DefaultEmptyIcon({ className }: { className?: string }) {
  return (
    <svg
      className={cn('w-16 h-16 text-crypto-border', className)}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
      />
    </svg>
  );
}

// Variantes pré-definidas
export function NoDataState({ onRetry }: { onRetry?: () => void }) {
  return (
    <EmptyState
      title="Nenhum dado encontrado"
      description="Não há dados disponíveis para exibir no momento."
      action={onRetry ? { label: 'Tentar novamente', onClick: onRetry } : undefined}
    />
  );
}

export function NoResultsState({ onClear }: { onClear?: () => void }) {
  return (
    <EmptyState
      icon={
        <svg className="w-16 h-16 text-crypto-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      }
      title="Nenhum resultado"
      description="Sua busca não retornou resultados. Tente ajustar os filtros."
      action={onClear ? { label: 'Limpar filtros', onClick: onClear } : undefined}
    />
  );
}

export function NoAlertsState() {
  return (
    <EmptyState
      icon={
        <svg className="w-16 h-16 text-crypto-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      }
      title="Nenhum alerta"
      description="Você não tem alertas no momento. Continue monitorando!"
    />
  );
}

export function NoAssetsState({ onAdd }: { onAdd?: () => void }) {
  return (
    <EmptyState
      icon={
        <svg className="w-16 h-16 text-crypto-border" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      }
      title="Nenhum ativo monitorado"
      description="Adicione ativos para começar a monitorar os sinais."
      action={onAdd ? { label: 'Adicionar ativo', onClick: onAdd } : undefined}
    />
  );
}

export default EmptyState;
