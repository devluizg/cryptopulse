/**
 * CryptoPulse - Asset Detail Page
 * Página de detalhes de um ativo específico
 */

'use client';

import * as React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useSignalDetail, useSignalHistory } from '@/hooks/useSignals';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { MobileNavigation, Breadcrumb } from '@/components/layout/Navigation';
import { IndicatorGrid } from '@/components/asset-detail/IndicatorCard';
import { MetricHistory } from '@/components/asset-detail/MetricHistory';
import { ScoreBadge } from '@/components/dashboard/ScoreBadge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ErrorBoundary, ErrorFallback } from '@/components/common/ErrorBoundary';
import { PageLoading } from '@/components/common/LoadingSpinner';
import { INDICATOR_LABELS, CRYPTO_ICONS } from '@/lib/constants';
import { formatCurrency, formatPercent, formatRelativeTime } from '@/lib/formatters';
import { cn } from '@/lib/utils';

export default function AssetDetailPage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-6 pb-20 lg:pb-6">
          <AssetDetailContent />
        </main>
        <Footer />
        <MobileNavigation />
      </div>
    </ErrorBoundary>
  );
}

function AssetDetailContent() {
  const params = useParams();
  const router = useRouter();
  const symbol = (params.symbol as string)?.toUpperCase() || '';
  
  // Evita hydration mismatch
  const [isMounted, setIsMounted] = React.useState(false);
  
  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const { signal, isLoading, error, refresh } = useSignalDetail(symbol);
  const { history, isLoading: historyLoading } = useSignalHistory(symbol, 24);

  // Mostra loading enquanto não montado ou carregando
  if (!isMounted || isLoading) {
    return <PageLoading message={`Carregando ${symbol}...`} />;
  }

  if (error) {
    return (
      <ErrorFallback
        error={new Error(error)}
        onReset={refresh}
        title={`Erro ao carregar ${symbol}`}
      />
    );
  }

  if (!signal) {
    return (
      <ErrorFallback
        error={new Error('Ativo não encontrado')}
        onReset={refresh}
        title={`${symbol} não encontrado`}
      />
    );
  }

  const cryptoIcon = CRYPTO_ICONS[symbol] || '●';
  const priceChangeColor =
    signal.price_change_24h !== null && signal.price_change_24h >= 0
      ? 'text-score-high'
      : 'text-score-low';

  const indicators = [
    {
      name: INDICATOR_LABELS.whale_accumulation_score.name,
      value: signal.whale_accumulation_score,
      icon: INDICATOR_LABELS.whale_accumulation_score.icon,
      description: INDICATOR_LABELS.whale_accumulation_score.description,
    },
    {
      name: INDICATOR_LABELS.exchange_netflow_score.name,
      value: signal.exchange_netflow_score,
      icon: INDICATOR_LABELS.exchange_netflow_score.icon,
      description: INDICATOR_LABELS.exchange_netflow_score.description,
    },
    {
      name: INDICATOR_LABELS.volume_anomaly_score.name,
      value: signal.volume_anomaly_score,
      icon: INDICATOR_LABELS.volume_anomaly_score.icon,
      description: INDICATOR_LABELS.volume_anomaly_score.description,
    },
    {
      name: INDICATOR_LABELS.oi_pressure_score.name,
      value: signal.oi_pressure_score,
      icon: INDICATOR_LABELS.oi_pressure_score.icon,
      description: INDICATOR_LABELS.oi_pressure_score.description,
    },
    {
      name: INDICATOR_LABELS.narrative_momentum_score.name,
      value: signal.narrative_momentum_score,
      icon: INDICATOR_LABELS.narrative_momentum_score.icon,
      description: INDICATOR_LABELS.narrative_momentum_score.description,
    },
  ];

  return (
    <div className="space-y-6">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: symbol },
        ]}
      />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-crypto-card border border-crypto-border flex items-center justify-center text-3xl">
            {cryptoIcon}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-crypto-text">{symbol}</h1>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xl font-mono text-crypto-text">
                {formatCurrency(signal.price_usd)}
              </span>
              <span className={cn('font-mono', priceChangeColor)}>
                {formatPercent(signal.price_change_24h)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <ScoreBadge
            score={signal.explosion_score}
            status={signal.status}
            size="lg"
            showLabel
            animated={signal.status === 'high'}
          />
          <Button variant="outline" onClick={refresh}>
            Atualizar
          </Button>
        </div>
      </div>

      <p className="text-sm text-crypto-muted">
        Última atualização: {formatRelativeTime(signal.calculated_at)}
      </p>

      {signal.main_drivers && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">💡</span>
              <div>
                <h3 className="font-medium text-crypto-text">Principal Driver</h3>
                <p className="text-crypto-muted">{signal.main_drivers}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="text-lg font-semibold text-crypto-text mb-4">
          Breakdown dos Indicadores
        </h2>
        <IndicatorGrid indicators={indicators} />
      </div>

      <MetricHistory history={history} isLoading={historyLoading} />

      <div className="pt-4">
        <Button variant="outline" onClick={() => router.back()}>
          ← Voltar
        </Button>
      </div>
    </div>
  );
}
