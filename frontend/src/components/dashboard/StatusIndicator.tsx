/**
 * CryptoPulse - StatusIndicator Component
 * Indicador visual de status do ativo
 */

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScoreStatus } from '@/types';
import { SCORE_STATUS_LABELS } from '@/lib/constants';

interface StatusIndicatorProps {
  status: ScoreStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  pulse?: boolean;
  className?: string;
}

export function StatusIndicator({
  status,
  size = 'md',
  showLabel = true,
  pulse = false,
  className,
}: StatusIndicatorProps) {
  const dotSizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const colors = {
    high: 'bg-score-high',
    attention: 'bg-score-attention',
    low: 'bg-score-low',
  };

  const textColors = {
    high: 'text-score-high',
    attention: 'text-score-attention',
    low: 'text-score-low',
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className="relative flex">
        <span
          className={cn(
            'rounded-full',
            dotSizes[size],
            colors[status],
            pulse && status === 'high' && 'animate-ping absolute inline-flex h-full w-full opacity-75'
          )}
        />
        <span
          className={cn('relative inline-flex rounded-full', dotSizes[size], colors[status])}
        />
      </span>
      {showLabel && (
        <span className={cn('text-sm font-medium', textColors[status])}>
          {SCORE_STATUS_LABELS[status]}
        </span>
      )}
    </div>
  );
}

// Barra de status com múltiplos indicadores
interface StatusBarProps {
  highCount: number;
  attentionCount: number;
  lowCount: number;
  className?: string;
}

export function StatusBar({ highCount, attentionCount, lowCount, className }: StatusBarProps) {
  const total = highCount + attentionCount + lowCount;
  if (total === 0) return null;

  const highPercent = (highCount / total) * 100;
  const attentionPercent = (attentionCount / total) * 100;
  const lowPercent = (lowCount / total) * 100;

  return (
    <div className={cn('w-full', className)}>
      <div className="flex h-2 rounded-full overflow-hidden bg-crypto-border">
        {highPercent > 0 && (
          <div
            className="bg-score-high transition-all duration-500"
            style={{ width: `${highPercent}%` }}
          />
        )}
        {attentionPercent > 0 && (
          <div
            className="bg-score-attention transition-all duration-500"
            style={{ width: `${attentionPercent}%` }}
          />
        )}
        {lowPercent > 0 && (
          <div
            className="bg-score-low transition-all duration-500"
            style={{ width: `${lowPercent}%` }}
          />
        )}
      </div>
      <div className="flex justify-between mt-1 text-xs text-crypto-muted">
        <span>{highCount} alta</span>
        <span>{attentionCount} atenção</span>
        <span>{lowCount} baixa</span>
      </div>
    </div>
  );
}

export default StatusIndicator;
