/**
 * CryptoPulse - ScoreBreakdown Component
 * Breakdown detalhado do explosion score
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScoreDetail } from '@/types';
import { INDICATOR_LABELS } from '@/lib/constants';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ProgressGauge } from '@/components/charts/GaugeChart';
import { Tooltip } from '@/components/ui/tooltip';

interface ScoreBreakdownProps {
  score: ScoreDetail;
  className?: string;
}

export function ScoreBreakdown({ score, className }: ScoreBreakdownProps) {
  const indicators = [
    {
      key: 'whale_accumulation_score',
      value: score.whale_accumulation_score,
      ...INDICATOR_LABELS.whale_accumulation_score,
    },
    {
      key: 'exchange_netflow_score',
      value: score.exchange_netflow_score,
      ...INDICATOR_LABELS.exchange_netflow_score,
    },
    {
      key: 'volume_anomaly_score',
      value: score.volume_anomaly_score,
      ...INDICATOR_LABELS.volume_anomaly_score,
    },
    {
      key: 'oi_pressure_score',
      value: score.oi_pressure_score,
      ...INDICATOR_LABELS.oi_pressure_score,
    },
    {
      key: 'narrative_momentum_score',
      value: score.narrative_momentum_score,
      ...INDICATOR_LABELS.narrative_momentum_score,
    },
  ];

  // Find top drivers
  const sortedIndicators = [...indicators].sort((a, b) => b.value - a.value);
  const topDrivers = sortedIndicators.slice(0, 2);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Breakdown do Score</span>
          <span className="text-2xl font-bold text-score-high">
            {score.explosion_score.toFixed(1)}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Indicator bars */}
        {indicators.map((indicator) => (
          <div key={indicator.key} className="space-y-1">
            <div className="flex items-center justify-between">
              <Tooltip content={indicator.description}>
                <div className="flex items-center gap-2 cursor-help">
                  <span className="text-lg">{indicator.icon}</span>
                  <span className="text-sm text-crypto-text">{indicator.name}</span>
                </div>
              </Tooltip>
              <span className="text-sm font-mono text-crypto-muted">
                {indicator.value.toFixed(1)}
              </span>
            </div>
            <ProgressGauge value={indicator.value} size="sm" showValue={false} />
          </div>
        ))}

        {/* Main drivers */}
        {topDrivers.length > 0 && (
          <div className="pt-4 border-t border-crypto-border">
            <p className="text-xs text-crypto-muted mb-2">Principais drivers:</p>
            <div className="flex flex-wrap gap-2">
              {topDrivers.map((driver) => (
                <span
                  key={driver.key}
                  className="px-2 py-1 text-xs bg-score-high/10 text-score-high rounded-full"
                >
                  {driver.icon} {driver.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Custom main drivers from API */}
        {score.main_drivers && (
          <p className="text-sm text-crypto-muted italic">
            "{score.main_drivers}"
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// Compact version for sidebar
interface CompactScoreBreakdownProps {
  score: ScoreDetail;
  className?: string;
}

export function CompactScoreBreakdown({ score, className }: CompactScoreBreakdownProps) {
  const indicators = [
    { label: '🐋', value: score.whale_accumulation_score },
    { label: '📊', value: score.exchange_netflow_score },
    { label: '📈', value: score.volume_anomaly_score },
    { label: '⚡', value: score.oi_pressure_score },
    { label: '📰', value: score.narrative_momentum_score },
  ];

  return (
    <div className={cn('grid grid-cols-5 gap-2', className)}>
      {indicators.map((ind, i) => (
        <div key={i} className="text-center">
          <div className="text-lg mb-1">{ind.label}</div>
          <div
            className={cn(
              'text-xs font-mono',
              ind.value >= 70 && 'text-score-high',
              ind.value >= 40 && ind.value < 70 && 'text-score-attention',
              ind.value < 40 && 'text-score-low'
            )}
          >
            {ind.value.toFixed(0)}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ScoreBreakdown;
