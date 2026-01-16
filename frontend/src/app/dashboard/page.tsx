/**
 * CryptoPulse - Dashboard Page
 * Página principal do dashboard
 */

'use client';

import * as React from 'react';
import { useAssets } from '@/hooks/useAssets';
import { useAlerts } from '@/hooks/useAlerts';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { MobileNavigation } from '@/components/layout/Navigation';
import { QuickStats } from '@/components/dashboard/QuickStats';
import { FilterBar } from '@/components/dashboard/FilterBar';
import { AssetTable, TopMovers } from '@/components/dashboard/AssetTable';
import { Disclaimer } from '@/components/common/Disclaimer';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatRelativeTime } from '@/lib/formatters';

export default function DashboardPage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-6 pb-20 lg:pb-6">
          <DashboardContent />
        </main>
        <Footer />
        <MobileNavigation />
      </div>
    </ErrorBoundary>
  );
}

function DashboardContent() {
  const {
    filteredAssets,
    stats,
    isLoading,
    error,
    lastUpdated,
    filter,
    setFilter,
    resetFilter,
    refresh,
  } = useAssets({ autoFetch: true, autoRefresh: false });

  const { unreadCount } = useAlerts({ autoFetch: false });

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-crypto-text">Dashboard</h1>
          <p className="text-sm text-crypto-muted">
            Monitoramento de sinais em tempo real
            {lastUpdated && (
              <span className="ml-2">
                • Atualizado {formatRelativeTime(lastUpdated)}
              </span>
            )}
          </p>
        </div>
        
        <Button onClick={refresh} disabled={isLoading} variant="outline">
          <svg
            className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Atualizar
        </Button>
      </div>

      {/* Disclaimer */}
      <Disclaimer variant="inline" />

      {/* Error state - Backend offline */}
      {error && (
        <Card className="border-yellow-500/30 bg-yellow-500/5">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="text-3xl">⚠️</div>
              <div className="flex-1">
                <h3 className="font-semibold text-yellow-400 mb-2">
                  Backend não disponível
                </h3>
                <p className="text-sm text-crypto-muted mb-4">
                  Não foi possível conectar ao servidor. Verifique se o backend está rodando em{' '}
                  <code className="px-1 py-0.5 bg-crypto-card rounded text-xs">
                    http://localhost:8000
                  </code>
                </p>
                <div className="text-xs text-crypto-muted space-y-1">
                  <p>Para iniciar o backend:</p>
                  <code className="block px-2 py-1 bg-crypto-darker rounded">
                    cd ~/cryptopulse/backend && uvicorn src.main:app --reload
                  </code>
                </div>
                <Button onClick={refresh} variant="primary" className="mt-4">
                  Tentar novamente
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick stats */}
      <QuickStats stats={stats} isLoading={isLoading} />

      {/* Show content only if no error or has data */}
      {!error && (
        <>
          {/* Top movers (high score assets) */}
          <TopMovers assets={filteredAssets} limit={3} />

          {/* Filters */}
          <FilterBar
            filter={filter}
            onFilterChange={setFilter}
            onReset={resetFilter}
            totalCount={stats.totalAssets}
            filteredCount={filteredAssets.length}
          />

          {/* Asset table */}
          <AssetTable
            assets={filteredAssets}
            isLoading={isLoading}
            showVolume={true}
          />
        </>
      )}

      {/* Empty state when no error but no data */}
      {!error && !isLoading && filteredAssets.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="font-semibold text-crypto-text mb-2">
              Nenhum dado disponível
            </h3>
            <p className="text-sm text-crypto-muted mb-4">
              O sistema ainda não tem dados de ativos. Execute os coletores ou aguarde a próxima coleta.
            </p>
            <Button onClick={refresh} variant="outline">
              Verificar novamente
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
