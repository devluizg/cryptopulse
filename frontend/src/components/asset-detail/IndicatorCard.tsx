/**
 * CryptoPulse - IndicatorCard Component
 * Card individual para cada indicador
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from '@/components/ui/card';
import { GaugeChart } from '@/components/charts/GaugeChart';
import { Tooltip, InfoTooltip } from '@/components/ui/tooltip';

interface IndicatorCardProps {
  name: string;
  value: number;
  icon: string;
  description: string;
  details?: {
    label: string;
    value: string | number;
  }[];
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function IndicatorCard({
  name,
  value,
  icon,
  description,
  details,
  trend,
  className,
}: IndicatorCardProps) {
  const getStatusColor = () => {
    if (value >= 70) return 'border-score-high/30';
    if (value >= 40) return 'border-score-attention/30';
    return 'border-crypto-border';
  };

  const getValueColor = () => {
    if (value >= 70) return 'text-score-high';
    if (value >= 40) return 'text-score-attention';
    return 'text-score-low';
  };

  return (
    <Card className={cn('transition-all hover:border-crypto-muted', getStatusColor(), className)}>
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{icon}</span>
            <div>
              <h4 className="font-medium text-crypto-text">{name}</h4>
              <InfoTooltip text={description} />
            </div>
          </div>
          {trend && <TrendIcon trend={trend} />}
        </div>

        {/* Value */}
        <div className="flex items-center justify-center mb-3">
          <div className="text-center">
            <span className={cn('text-3xl font-bold', getValueColor())}>
              {value.toFixed(1)}
            </span>
            <span className="text-crypto-muted text-sm"> / 100</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 bg-crypto-border rounded-full overflow-hidden mb-3">
          <div
            className={cn(
              'h-full rounded-full transition-all duration-500',
              value >= 70 && 'bg-score-high',
              value >= 40 && value < 70 && 'bg-score-attention',
              value < 40 && 'bg-score-low'
            )}
            style={{ width: `${value}%` }}
          />
        </div>

        {/* Details */}
        {details && details.length > 0 && (
          <div className="space-y-1 pt-2 border-t border-crypto-border">
            {details.map((detail, index) => (
              <div key={index} className="flex justify-between text-xs">
                <span className="text-crypto-muted">{detail.label}</span>
                <span className="text-crypto-text font-mono">{detail.value}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Trend icon component
function TrendIcon({ trend }: { trend: 'up' | 'down' | 'neutral' }) {
  if (trend === 'up') {
    return (
      <div className="flex items-center text-score-high">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      </div>
    );
  }
  if (trend === 'down') {
    return (
      <div className="flex items-center text-score-low">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    );
  }
  return (
    <div className="flex items-center text-crypto-muted">
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
      </svg>
    </div>
  );
}

// Grid of indicator cards
interface IndicatorGridProps {
  indicators: {
    name: string;
    value: number;
    icon: string;
    description: string;
    details?: { label: string; value: string | number }[];
  }[];
  className?: string;
}

export function IndicatorGrid({ indicators, className }: IndicatorGridProps) {
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4', className)}>
      {indicators.map((indicator, index) => (
        <IndicatorCard key={index} {...indicator} />
      ))}
    </div>
  );
}

export default IndicatorCard;
