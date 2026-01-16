/**
 * CryptoPulse - PriceChart Component
 * Gráfico de preço do ativo
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { LineChart } from '@/components/charts/LineChart';
import { Button } from '@/components/ui/button';
import { formatCurrency, formatPercent } from '@/lib/formatters';

interface PriceDataPoint {
  timestamp: string;
  price: number;
  volume?: number;
}

interface PriceChartProps {
  symbol: string;
  currentPrice: number | null;
  priceChange24h: number | null;
  data: PriceDataPoint[];
  isLoading?: boolean;
  className?: string;
}

export function PriceChart({
  symbol,
  currentPrice,
  priceChange24h,
  data,
  isLoading,
  className,
}: PriceChartProps) {
  const [timeRange, setTimeRange] = React.useState<'24h' | '7d' | '30d'>('24h');

  const priceChangeColor =
    priceChange24h !== null && priceChange24h >= 0
      ? 'text-score-high'
      : 'text-score-low';

  // Transform data for chart
  const chartData = data.map((d) => ({
    timestamp: d.timestamp,
    value: d.price,
  }));

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Preço {symbol}</CardTitle>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-2xl font-bold text-crypto-text">
                {formatCurrency(currentPrice)}
              </span>
              <span className={cn('text-sm font-medium', priceChangeColor)}>
                {formatPercent(priceChange24h)} (24h)
              </span>
            </div>
          </div>

          {/* Time range selector */}
          <div className="flex items-center gap-1 bg-crypto-darker rounded-lg p-1">
            {(['24h', '7d', '30d'] as const).map((range) => (
              <Button
                key={range}
                variant={timeRange === range ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setTimeRange(range)}
              >
                {range}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-2 border-score-high border-t-transparent rounded-full" />
          </div>
        ) : (
          <LineChart
            data={chartData}
            height={256}
            color={priceChange24h !== null && priceChange24h >= 0 ? '#22c55e' : '#ef4444'}
            gradientFill
          />
        )}
      </CardContent>
    </Card>
  );
}

// Mini price display for headers
interface MiniPriceDisplayProps {
  price: number | null;
  change: number | null;
  className?: string;
}

export function MiniPriceDisplay({ price, change, className }: MiniPriceDisplayProps) {
  const changeColor = change !== null && change >= 0 ? 'text-score-high' : 'text-score-low';

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className="font-mono text-crypto-text">{formatCurrency(price)}</span>
      <span className={cn('text-sm font-mono', changeColor)}>
        {formatPercent(change)}
      </span>
    </div>
  );
}

export default PriceChart;
