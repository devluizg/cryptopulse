/**
 * CryptoPulse - GaugeChart Component
 * Gráfico de medidor para scores
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScoreStatus } from '@/types';
import { SCORE_STATUS_LABELS } from '@/lib/constants';

interface GaugeChartProps {
  value: number;
  min?: number;
  max?: number;
  status?: ScoreStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  showValue?: boolean;
  animated?: boolean;
  className?: string;
}

export function GaugeChart({
  value,
  min = 0,
  max = 100,
  status,
  size = 'md',
  showLabel = true,
  showValue = true,
  animated = true,
  className,
}: GaugeChartProps) {
  const normalizedValue = Math.min(Math.max(value, min), max);
  const percentage = ((normalizedValue - min) / (max - min)) * 100;
  
  // Calculate rotation (from -90deg to 90deg)
  const rotation = -90 + (percentage * 180) / 100;

  const sizes = {
    sm: { width: 80, strokeWidth: 6, fontSize: 'text-lg' },
    md: { width: 120, strokeWidth: 8, fontSize: 'text-2xl' },
    lg: { width: 160, strokeWidth: 10, fontSize: 'text-3xl' },
  };

  const config = sizes[size];
  const radius = (config.width - config.strokeWidth) / 2;
  const circumference = radius * Math.PI; // Half circle

  // Determine color based on value or status
  const getColor = () => {
    if (status === 'high' || percentage >= 70) return '#22c55e';
    if (status === 'attention' || percentage >= 40) return '#eab308';
    return '#ef4444';
  };

  const color = getColor();
  const dashOffset = circumference - (percentage / 100) * circumference;

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className="relative" style={{ width: config.width, height: config.width / 2 + 20 }}>
        <svg
          width={config.width}
          height={config.width / 2 + 10}
          viewBox={`0 0 ${config.width} ${config.width / 2 + 10}`}
        >
          {/* Background arc */}
          <path
            d={describeArc(config.width / 2, config.width / 2, radius, -180, 0)}
            fill="none"
            stroke="#30363d"
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
          />
          
          {/* Value arc */}
          <path
            d={describeArc(config.width / 2, config.width / 2, radius, -180, -180 + (percentage * 180) / 100)}
            fill="none"
            stroke={color}
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            className={animated ? 'transition-all duration-1000 ease-out' : ''}
            style={{
              filter: `drop-shadow(0 0 6px ${color}40)`,
            }}
          />

          {/* Center dot */}
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={4}
            fill={color}
          />

          {/* Needle */}
          <line
            x1={config.width / 2}
            y1={config.width / 2}
            x2={config.width / 2}
            y2={config.strokeWidth + 10}
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
            transform={`rotate(${rotation}, ${config.width / 2}, ${config.width / 2})`}
            className={animated ? 'transition-transform duration-1000 ease-out' : ''}
          />
        </svg>

        {/* Value display */}
        {showValue && (
          <div
            className="absolute left-1/2 -translate-x-1/2"
            style={{ bottom: 0 }}
          >
            <span className={cn('font-bold', config.fontSize)} style={{ color }}>
              {Math.round(value)}
            </span>
          </div>
        )}
      </div>

      {/* Label */}
      {showLabel && status && (
        <span
          className="text-sm font-medium mt-1"
          style={{ color }}
        >
          {SCORE_STATUS_LABELS[status]}
        </span>
      )}
    </div>
  );
}

// Helper function to describe an arc path
function describeArc(x: number, y: number, radius: number, startAngle: number, endAngle: number): string {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';

  return [
    'M', start.x, start.y,
    'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y,
  ].join(' ');
}

function polarToCartesian(centerX: number, centerY: number, radius: number, angleInDegrees: number) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

// Simple progress gauge (horizontal)
interface ProgressGaugeProps {
  value: number;
  max?: number;
  label?: string;
  showValue?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function ProgressGauge({
  value,
  max = 100,
  label,
  showValue = true,
  size = 'md',
  className,
}: ProgressGaugeProps) {
  const percentage = Math.min((value / max) * 100, 100);
  
  const getColor = () => {
    if (percentage >= 70) return 'bg-score-high';
    if (percentage >= 40) return 'bg-score-attention';
    return 'bg-score-low';
  };

  const heights = {
    sm: 'h-1.5',
    md: 'h-2',
  };

  return (
    <div className={cn('w-full', className)}>
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-xs text-crypto-muted">{label}</span>}
          {showValue && (
            <span className="text-xs font-mono text-crypto-text">{value.toFixed(1)}</span>
          )}
        </div>
      )}
      <div className={cn('w-full bg-crypto-border rounded-full overflow-hidden', heights[size])}>
        <div
          className={cn('h-full rounded-full transition-all duration-500', getColor())}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default GaugeChart;
