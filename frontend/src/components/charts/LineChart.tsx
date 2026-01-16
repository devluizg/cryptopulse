/**
 * CryptoPulse - LineChart Component
 * Gráfico de linha para histórico de scores/preços
 */

'use client';

import * as React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { cn } from '@/lib/utils';
import { CHART_COLORS } from '@/lib/constants';
import { formatDate } from '@/lib/formatters';

interface DataPoint {
  timestamp: string;
  value?: number;
  [key: string]: string | number | undefined;
}

interface LineChartProps {
  data: DataPoint[];
  dataKey?: string;
  xAxisKey?: string;
  color?: string;
  height?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  strokeWidth?: number;
  gradientFill?: boolean;
  className?: string;
}

export function LineChart({
  data,
  dataKey = 'value',
  xAxisKey = 'timestamp',
  color = CHART_COLORS.primary,
  height = 300,
  showGrid = true,
  showLegend = false,
  showTooltip = true,
  strokeWidth = 2,
  gradientFill = true,
  className,
}: LineChartProps) {
  const gradientId = React.useId();

  if (!data || data.length === 0) {
    return (
      <div className={cn('flex items-center justify-center bg-crypto-card rounded-lg', className)} style={{ height }}>
        <span className="text-crypto-muted">Sem dados disponíveis</span>
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          {gradientFill && (
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
          )}
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />}
          <XAxis
            dataKey={xAxisKey}
            stroke={CHART_COLORS.neutral}
            tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => formatDate(value, 'HH:mm')}
          />
          <YAxis
            stroke={CHART_COLORS.neutral}
            tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={40}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{
                backgroundColor: CHART_COLORS.background,
                border: `1px solid ${CHART_COLORS.grid}`,
                borderRadius: '8px',
                padding: '8px 12px',
              }}
              labelStyle={{ color: CHART_COLORS.neutral }}
              itemStyle={{ color }}
              labelFormatter={(value) => formatDate(value as string, 'dd/MM HH:mm')}
            />
          )}
          {showLegend && <Legend />}
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={strokeWidth}
            dot={false}
            activeDot={{ r: 4, fill: color }}
            fill={gradientFill ? `url(#${gradientId})` : 'none'}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}

interface MultiLineDataPoint {
  timestamp: string;
  [key: string]: string | number | undefined;
}

interface MultiLineChartProps {
  data: MultiLineDataPoint[];
  lines: { dataKey: string; color: string; name: string }[];
  xAxisKey?: string;
  height?: number;
  className?: string;
}

export function MultiLineChart({
  data,
  lines,
  xAxisKey = 'timestamp',
  height = 300,
  className,
}: MultiLineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className={cn('flex items-center justify-center bg-crypto-card rounded-lg', className)} style={{ height }}>
        <span className="text-crypto-muted">Sem dados disponíveis</span>
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
          <XAxis
            dataKey={xAxisKey}
            stroke={CHART_COLORS.neutral}
            tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => formatDate(value, 'HH:mm')}
          />
          <YAxis
            stroke={CHART_COLORS.neutral}
            tick={{ fill: CHART_COLORS.neutral, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={40}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: CHART_COLORS.background,
              border: `1px solid ${CHART_COLORS.grid}`,
              borderRadius: '8px',
            }}
          />
          <Legend />
          {lines.map((line) => (
            <Line key={line.dataKey} type="monotone" dataKey={line.dataKey} stroke={line.color} strokeWidth={2} dot={false} name={line.name} />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default LineChart;
