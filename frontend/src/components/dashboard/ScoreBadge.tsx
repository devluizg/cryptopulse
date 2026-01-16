/**
 * CryptoPulse - ScoreBadge Component
 * Badge visual para exibir o explosion score
 */

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScoreStatus } from '@/types';
import { SCORE_STATUS_LABELS } from '@/lib/constants';
import { Tooltip } from '@/components/ui/tooltip';

interface ScoreBadgeProps {
  score: number;
  status: ScoreStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
  className?: string;
}

export function ScoreBadge({
  score,
  status,
  size = 'md',
  showLabel = false,
  animated = false,
  className,
}: ScoreBadgeProps) {
  const sizes = {
    sm: 'w-10 h-10 text-sm',
    md: 'w-14 h-14 text-lg',
    lg: 'w-20 h-20 text-2xl',
  };

  const colors = {
    high: 'from-score-high to-emerald-600 shadow-score-high/30',
    attention: 'from-score-attention to-amber-600 shadow-score-attention/30',
    low: 'from-score-low to-red-700 shadow-score-low/30',
  };

  const glowColors = {
    high: 'shadow-[0_0_20px_rgba(34,197,94,0.4)]',
    attention: 'shadow-[0_0_20px_rgba(234,179,8,0.3)]',
    low: '',
  };

  return (
    <Tooltip content={`${SCORE_STATUS_LABELS[status]} - Score: ${score.toFixed(1)}`}>
      <div className={cn('flex flex-col items-center gap-1', className)}>
        <div
          className={cn(
            'rounded-full bg-gradient-to-br flex items-center justify-center font-bold text-white shadow-lg',
            sizes[size],
            colors[status],
            animated && status === 'high' && glowColors[status],
            animated && status === 'high' && 'animate-pulse-slow'
          )}
        >
          {Math.round(score)}
        </div>
        {showLabel && (
          <span
            className={cn(
              'text-xs font-medium',
              status === 'high' && 'text-score-high',
              status === 'attention' && 'text-score-attention',
              status === 'low' && 'text-score-low'
            )}
          >
            {SCORE_STATUS_LABELS[status]}
          </span>
        )}
      </div>
    </Tooltip>
  );
}

// Mini version for tables
interface MiniScoreBadgeProps {
  score: number;
  status: ScoreStatus;
  className?: string;
}

export function MiniScoreBadge({ score, status, className }: MiniScoreBadgeProps) {
  const colors = {
    high: 'bg-score-high/20 text-score-high border-score-high/30',
    attention: 'bg-score-attention/20 text-score-attention border-score-attention/30',
    low: 'bg-score-low/20 text-score-low border-score-low/30',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold rounded border',
        colors[status],
        className
      )}
    >
      {Math.round(score)}
    </span>
  );
}

export default ScoreBadge;
