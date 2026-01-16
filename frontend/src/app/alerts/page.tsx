'use client';

import * as React from 'react';
import { useState } from 'react';
import { useAlerts } from '@/hooks/useAlerts';
import { useNotifications } from '@/hooks/useNotifications';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { MobileNavigation } from '@/components/layout/Navigation';
import { AlertList } from '@/components/alerts/AlertList';
import { AlertDetailModal } from '@/components/alerts/AlertDetailModal';
import { AlertConfigPanel } from '@/components/alerts/AlertConfig';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ErrorBoundary, ErrorFallback } from '@/components/common/ErrorBoundary';
import { formatRelativeTime } from '@/lib/formatters';
import { AlertWithAsset } from '@/types';
import { useSettingsStore } from '@/store';
import { cn } from '@/lib/utils';

export default function AlertsPage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col bg-crypto-darker">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-6 pb-20 lg:pb-6">
          <AlertsContent />
        </main>
        <Footer />
        <MobileNavigation />
      </div>
    </ErrorBoundary>
  );
}

function AlertsContent() {
  const [activeTab, setActiveTab] = useState<'list' | 'settings'>('list');
  const [selectedAlert, setSelectedAlert] = useState<AlertWithAsset | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { filteredAlerts, stats, unreadCount, isLoading, error, lastUpdated, filter, setFilter, markAsRead, markAllAsRead, dismiss, refresh } = useAlerts({ autoFetch: true, autoRefresh: true });
  const { permission, isSupported, requestPermission, soundEnabled, toggleSound, testSound } = useNotifications();
  const alertConfig = useSettingsStore((state) => state.alertConfig);
  const setAlertConfig = useSettingsStore((state) => state.setAlertConfig);

  if (error) return <ErrorFallback error={new Error(error)} onReset={refresh} title="Erro ao carregar alertas" />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-crypto-text flex items-center gap-3">
            <span className="text-3xl">🔔</span> Alertas
          </h1>
          <p className="text-sm text-crypto-muted mt-1">
            {unreadCount > 0 ? `${unreadCount} alerta${unreadCount > 1 ? 's' : ''} não lido${unreadCount > 1 ? 's' : ''}` : 'Todos os alertas foram lidos'}
            {lastUpdated && <span className="ml-2">• Atualizado {formatRelativeTime(lastUpdated)}</span>}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex bg-crypto-card rounded-lg p-1">
            <button onClick={() => setActiveTab('list')} className={cn('px-4 py-2 text-sm font-medium rounded-md transition-colors', activeTab === 'list' ? 'bg-crypto-border text-crypto-text' : 'text-crypto-muted')}>Lista</button>
            <button onClick={() => setActiveTab('settings')} className={cn('px-4 py-2 text-sm font-medium rounded-md transition-colors', activeTab === 'settings' ? 'bg-crypto-border text-crypto-text' : 'text-crypto-muted')}>Configurações</button>
          </div>
          <Button variant="outline" onClick={refresh} disabled={isLoading}>Atualizar</Button>
        </div>
      </div>

      {stats && activeTab === 'list' && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard label="Total" value={stats.total} icon="📊" />
          <StatCard label="Não lidos" value={stats.unread} icon="🔔" highlight={stats.unread > 0} color="text-score-high" />
          <StatCard label="Críticos" value={stats.by_severity?.critical || 0} icon="🚨" color="text-red-400" />
          <StatCard label="Atenção" value={stats.by_severity?.warning || 0} icon="⚠️" color="text-yellow-400" />
          <StatCard label="Hoje" value={stats.today_count} icon="📅" />
        </div>
      )}

      {activeTab === 'list' && isSupported && permission === 'default' && (
        <div className="flex items-center justify-between p-4 bg-score-attention/10 border border-score-attention/30 rounded-lg">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔔</span>
            <div>
              <p className="font-medium text-crypto-text">Ative as notificações</p>
              <p className="text-sm text-crypto-muted">Receba alertas importantes mesmo com o navegador minimizado</p>
            </div>
          </div>
          <Button variant="primary" size="sm" onClick={requestPermission}>Ativar</Button>
        </div>
      )}

      {activeTab === 'list' ? (
        <AlertList alerts={filteredAlerts} isLoading={isLoading} filter={filter} onFilterChange={setFilter} onMarkRead={(id) => markAsRead([id])} onMarkAllRead={markAllAsRead} onDismiss={dismiss} showFilters={true} />
      ) : (
        <div className="grid lg:grid-cols-2 gap-6">
          <AlertConfigPanel config={alertConfig} onConfigChange={setAlertConfig} />
          <Card>
            <CardHeader><CardTitle>Notificações do Sistema</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-crypto-darker rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-xl">🌐</span>
                  <div>
                    <p className="font-medium text-crypto-text">Notificações do Browser</p>
                    <p className="text-xs text-crypto-muted">{permission === 'granted' ? 'Ativadas' : permission === 'denied' ? 'Bloqueadas' : 'Não configuradas'}</p>
                  </div>
                </div>
                {permission !== 'granted' && permission !== 'denied' && <Button variant="outline" size="sm" onClick={requestPermission}>Ativar</Button>}
              </div>
              <div className="flex items-center justify-between p-4 bg-crypto-darker rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{soundEnabled ? '🔊' : '🔇'}</span>
                  <div>
                    <p className="font-medium text-crypto-text">Som de Alerta</p>
                    <p className="text-xs text-crypto-muted">{soundEnabled ? 'Ativado' : 'Desativado'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={testSound}>Testar</Button>
                  <button onClick={toggleSound} className={cn('relative w-12 h-6 rounded-full transition-colors', soundEnabled ? 'bg-score-high' : 'bg-crypto-border')}>
                    <span className={cn('absolute top-1 w-4 h-4 bg-white rounded-full transition-transform', soundEnabled ? 'left-7' : 'left-1')} />
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <AlertDetailModal alert={selectedAlert} isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); setSelectedAlert(null); }} onMarkRead={(id) => markAsRead([id])} onDismiss={dismiss} />
    </div>
  );
}

function StatCard({ label, value, icon, color, highlight }: { label: string; value: number; icon: string; color?: string; highlight?: boolean }) {
  return (
    <Card className={cn(highlight && 'ring-1 ring-score-high/50')}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-crypto-muted">{label}</p>
            <p className={cn('text-2xl font-bold', color || 'text-crypto-text')}>{value}</p>
          </div>
          <span className="text-2xl">{icon}</span>
        </div>
      </CardContent>
    </Card>
  );
}
