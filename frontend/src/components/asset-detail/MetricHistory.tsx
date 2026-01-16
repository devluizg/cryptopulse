/**
 * CryptoPulse - MetricHistory Component
 * Histórico de métricas do ativo
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { LineChart, MultiLineChart } from '@/components/charts/LineChart';
import { Button } from '@/components/ui/button';
import { ScoreDetail } from '@/types';
import { CHART_COLORS } from '@/lib/constants';

interface MetricHistoryProps {
  history: ScoreDetail[];
  isLoading?: boolean;
  className?: string;
}

export function MetricHistory({ history, isLoading, className }: MetricHistoryProps) {
  const [selectedMetric, setSelectedMetric] = React.useState<'all' | 'score' | 'indicators'>('score');

  const chartData = history.map((h) => ({
    timestamp: h.calculated_at,
    score: h.explosion_score,
    whale: h.whale_accumulation_score,
    netflow: h.exchange_netflow_score,
    volume: h.volume_anomaly_score,
    oi: h.oi_pressure_score,
    narrative: h.narrative_momentum_score,
  }));

  const scoreChartData = history.map((h) => ({
    timestamp: h.calculated_at,
    value: h.explosion_score,
  }));

  const indicatorLines = [
    { dataKey: 'whale', color: CHART_COLORS.primary, name: 'Whale' },
    { dataKey: 'netflow', color: CHART_COLORS.secondary, name: 'Netflow' },
    { dataKey: 'volume', color: CHART_COLORS.tertiary, name: 'Volume' },
    { dataKey: 'oi', color: CHART_COLORS.quaternary, name: 'OI' },
    { dataKey: 'narrative', color: '#ec4899', name: 'Narrative' },
  ];

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader><CardTitle>Histórico de Métricas</CardTitle></CardHeader>
        <CardContent><div className="h-64 bg-crypto-border animate-pulse rounded-lg" /></CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Histórico de Métricas</CardTitle>
          <div className="flex items-center gap-1 bg-crypto-darker rounded-lg p-1">
            <Button variant={selectedMetric === 'score' ? 'secondary' : 'ghost'} size="sm" onClick={() => setSelectedMetric('score')}>Score</Button>
            <Button variant={selectedMetric === 'indicators' ? 'secondary' : 'ghost'} size="sm" onClick={() => setSelectedMetric('indicators')}>Indicadores</Button>
            <Button variant={selectedMetric === 'all' ? 'secondary' : 'ghost'} size="sm" onClick={() => setSelectedMetric('all')}>Todos</Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <div className="h-64 flex items-center justify-center text-crypto-muted">Sem histórico disponível</div>
        ) : (
          <>
            {selectedMetric === 'score' && <LineChart data={scoreChartData} height={256} color={CHART_COLORS.primary} gradientFill />}
            {selectedMetric === 'indicators' && <MultiLineChart data={chartData} lines={indicatorLines} height={256} />}
            {selectedMetric === 'all' && <MultiLineChart data={chartData} lines={[{ dataKey: 'score', color: '#ffffff', name: 'Score Total' }, ...indicatorLines]} height={300} />}
          </>
        )}
        {(selectedMetric === 'indicators' || selectedMetric === 'all') && (
          <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-crypto-border">
            {indicatorLines.map((line) => (
              <div key={line.dataKey} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: line.color }} />
                <span className="text-xs text-crypto-muted">{line.name}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default MetricHistory;
