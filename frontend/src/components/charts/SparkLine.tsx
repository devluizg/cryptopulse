/**
 * CryptoPulse - SparkLine Component
 * Mini gráfico de linha para tendências
 */

'use client';

import * as React from 'react';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';
import { cn } from '@/lib/utils';
import { CHART_COLORS } from '@/lib/constants';

interface SparkLineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
  showTrend?: boolean;
  className?: string;
}

export function SparkLine({
  data,
  color,
  width = 100,
  height = 32,
  showTrend = true,
  className,
}: SparkLineProps) {
  if (!data || data.length < 2) {
    return (
      <div
        className={cn('flex items-center justify-center', className)}
        style={{ width, height }}
      >
        <span className="text-xs text-crypto-muted">—</span>
      </div>
    );
  }

  // Determine trend color
  const firstValue = data[0];
  const lastValue = data[data.length - 1];
  const trend = lastValue - firstValue;
  const trendColor =
    color || (trend >= 0 ? CHART_COLORS.primary : CHART_COLORS.negative);

  // Transform data for recharts
  const chartData = data.map((value, index) => ({ index, value }));

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div style={{ width, height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <YAxis domain={['dataMin', 'dataMax']} hide />
            <Line
              type="monotone"
              dataKey="value"
              stroke={trendColor}
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {showTrend && (
        <TrendIndicator value={trend} percentage={(trend / firstValue) * 100} />
      )}
    </div>
  );
}

// Trend indicator component
interface TrendIndicatorProps {
  value: number;
  percentage?: number;
  size?: 'sm' | 'md';
}

export function TrendIndicator({ value, percentage, size = 'sm' }: TrendIndicatorProps) {
  const isPositive = value >= 0;
  const color = isPositive ? 'text-score-high' : 'text-score-low';
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';

  return (
    <div className={cn('flex items-center gap-0.5', color)}>
      {isPositive ? (
        <svg className={iconSize} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      ) : (
        <svg className={iconSize} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      )}
      {percentage !== undefined && (
        <span className={cn('font-mono', size === 'sm' ? 'text-xs' : 'text-sm')}>
          {isPositive ? '+' : ''}{percentage.toFixed(1)}%
        </span>
      )}
    </div>
  );
}

// Mini sparkline for tables
interface MiniSparkLineProps {
  data: number[];
  className?: string;
}

export function MiniSparkLine({ data, className }: MiniSparkLineProps) {
  return <SparkLine data={data} width={60} height={24} showTrend={false} className={className} />;
}

export default SparkLine;
