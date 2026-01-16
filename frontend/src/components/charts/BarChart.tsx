/**
 * CryptoPulse - BarChart Component
 * Gráfico de barras para comparações
 */

'use client';

import * as React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from 'recharts';
import { cn } from '@/lib/utils';
import { CHART_COLORS } from '@/lib/constants';

interface DataPoint {
  name: string;
  value: number;
  color?: string;
  [key: string]: string | number | undefined;
}

interface BarChartProps {
  data: DataPoint[];
  dataKey?: string;
  xAxisKey?: string;
  color?: string;
  height?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  horizontal?: boolean;
  colorByValue?: boolean;
  className?: string;
}

export function BarChart({
  data,
  dataKey = 'value',
  xAxisKey = 'name',
  color = CHART_COLORS.primary,
  height = 300,
  showGrid = true,
  showLegend = false,
  horizontal = false,
  colorByValue = false,
  className,
}: BarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className={cn('flex items-center justify-center bg-crypto-card rounded-lg', className)} style={{ height }}>
        <span className="text-crypto-muted">Sem dados disponíveis</span>
      </div>
    );
  }

  // Get color based on value (for score breakdown)
  const getBarColor = (value: number) => {
    if (!colorByValue) return color;
    if (value >= 70) return CHART_COLORS.primary;
    if (value >= 40) return CHART_COLORS.quaternary;
    return CHART_COLORS.negative;
  };

  return (
    <div className={cn('w-full', className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart
          data={data}
          layout={horizontal ? 'vertical' : 'horizontal'}
          margin={{ top: 10, right: 10, left: horizontal ? 80 : 0, bottom: 0 }}
        >
          {/* Grid */}
          {showGrid && (
            <CartesianGrid
              strokeDasharray="3 3"
              stroke={CHART_COLORS.grid}
              horizontal={!horizontal}
              vertical={horizontal}
            />
          )}

          {/* Axes */}
          {horizontal ? (
            <>
              <XAxis type="number" stroke={CHART_COLORS.neutral} tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey={xAxisKey}
                stroke={CHART_COLORS.neutral}
                tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
                width={70}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey={xAxisKey}
                stroke={CHART_COLORS.neutral}
                tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke={CHART_COLORS.neutral}
                tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                width={40}
              />
            </>
          )}

          {/* Tooltip */}
          <Tooltip
            contentStyle={{
              backgroundColor: CHART_COLORS.background,
              border: `1px solid ${CHART_COLORS.grid}`,
              borderRadius: '8px',
              padding: '8px 12px',
            }}
            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
          />

          {/* Legend */}
          {showLegend && <Legend />}

          {/* Bars */}
          <Bar dataKey={dataKey} radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || getBarColor(entry[dataKey] as number)}
              />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Score breakdown bar chart
interface ScoreBreakdownChartProps {
  scores: {
    name: string;
    value: number;
    icon?: string;
  }[];
  height?: number;
  className?: string;
}

export function ScoreBreakdownChart({ scores, height = 200, className }: ScoreBreakdownChartProps) {
  const data = scores.map((s) => ({
    name: s.name,
    value: s.value,
    color:
      s.value >= 70
        ? CHART_COLORS.primary
        : s.value >= 40
        ? CHART_COLORS.quaternary
        : CHART_COLORS.negative,
  }));

  return <BarChart data={data} horizontal height={height} colorByValue className={className} />;
}

export default BarChart;
