/**
 * CryptoPulse - QuickStats Component
 * Cards de estatísticas rápidas do dashboard
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from '@/components/ui/card';
import { DashboardStats } from '@/types';
import { Skeleton } from '@/components/ui/skeleton';

interface QuickStatsProps {
  stats: DashboardStats;
  isLoading?: boolean;
  className?: string;
}

export function QuickStats({ stats, isLoading, className }: QuickStatsProps) {
  const statCards = [
    {
      label: 'Total de Ativos',
      value: stats.totalAssets,
      icon: '📊',
      color: 'text-crypto-text',
      bgColor: 'bg-crypto-border/50',
    },
    {
      label: 'Zona de Explosão',
      value: stats.highCount,
      icon: '🚀',
      color: 'text-score-high',
      bgColor: 'bg-score-high/10',
      highlight: stats.highCount > 0,
    },
    {
      label: 'Atenção',
      value: stats.attentionCount,
      icon: '⚠️',
      color: 'text-score-attention',
      bgColor: 'bg-score-attention/10',
    },
    {
      label: 'Baixo Potencial',
      value: stats.lowCount,
      icon: '📉',
      color: 'text-score-low',
      bgColor: 'bg-score-low/10',
    },
  ];

  if (isLoading) {
    return (
      <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-4', className)}>
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-20 mb-2" />
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-4', className)}>
      {statCards.map((stat, index) => (
        <Card
          key={index}
          className={cn(
            'transition-all duration-200 hover:scale-[1.02]',
            stat.highlight && 'ring-1 ring-score-high/50'
          )}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-crypto-muted mb-1">{stat.label}</p>
                <p className={cn('text-2xl font-bold', stat.color)}>{stat.value}</p>
              </div>
              <div
                className={cn(
                  'w-12 h-12 rounded-lg flex items-center justify-center text-2xl',
                  stat.bgColor
                )}
              >
                {stat.icon}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Versão compacta para sidebar ou mobile
interface CompactStatsProps {
  stats: DashboardStats;
  className?: string;
}

export function CompactStats({ stats, className }: CompactStatsProps) {
  return (
    <div className={cn('flex items-center gap-4', className)}>
      <StatPill
        value={stats.highCount}
        label="Alta"
        color="bg-score-high/20 text-score-high"
      />
      <StatPill
        value={stats.attentionCount}
        label="Atenção"
        color="bg-score-attention/20 text-score-attention"
      />
      <StatPill
        value={stats.lowCount}
        label="Baixa"
        color="bg-score-low/20 text-score-low"
      />
    </div>
  );
}

interface StatPillProps {
  value: number;
  label: string;
  color: string;
}

function StatPill({ value, label, color }: StatPillProps) {
  return (
    <div className={cn('px-3 py-1 rounded-full text-sm font-medium', color)}>
      {value} {label}
    </div>
  );
}

export default QuickStats;
