/**
 * CryptoPulse - Settings Page
 * Página de configurações
 */

'use client';

import * as React from 'react';
import { useSettingsStore } from '@/store';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { MobileNavigation } from '@/components/layout/Navigation';
import { AlertConfigPanel } from '@/components/alerts/AlertConfig';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { APP_NAME, APP_VERSION } from '@/lib/constants';

export default function SettingsPage() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        <Header />
        
        <main className="flex-1 container mx-auto px-4 py-6 pb-20 lg:pb-6">
          <SettingsContent />
        </main>
        
        <Footer />
        <MobileNavigation />
      </div>
    </ErrorBoundary>
  );
}

function SettingsContent() {
  const {
    theme,
    setTheme,
    refreshInterval,
    setRefreshInterval,
    autoRefresh,
    setAutoRefresh,
    alertConfig,
    setAlertConfig,
    resetSettings,
  } = useSettingsStore();

  const [saved, setSaved] = React.useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-crypto-text">Configurações</h1>
        <p className="text-sm text-crypto-muted">
          Personalize sua experiência no {APP_NAME}
        </p>
      </div>

      {/* General settings */}
      <Card>
        <CardHeader>
          <CardTitle>Geral</CardTitle>
          <CardDescription>Configurações gerais da aplicação</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Theme */}
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-crypto-text">Tema</div>
              <div className="text-sm text-crypto-muted">Escolha o tema visual</div>
            </div>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value as 'dark' | 'light' | 'system')}
              className="px-3 py-2 bg-crypto-card border border-crypto-border rounded-lg text-crypto-text"
            >
              <option value="dark">Escuro</option>
              <option value="light">Claro</option>
              <option value="system">Sistema</option>
            </select>
          </div>

          {/* Auto refresh */}
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-crypto-text">Atualização automática</div>
              <div className="text-sm text-crypto-muted">Atualizar dados automaticamente</div>
            </div>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                autoRefresh ? 'bg-score-high' : 'bg-crypto-border'
              }`}
            >
              <span
                className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                  autoRefresh ? 'left-7' : 'left-1'
                }`}
              />
            </button>
          </div>

          {/* Refresh interval */}
          {autoRefresh && (
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-crypto-text">Intervalo de atualização</div>
                <div className="text-sm text-crypto-muted">Frequência de atualização dos dados</div>
              </div>
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(parseInt(e.target.value) as 15000 | 30000 | 60000 | 300000)}
                className="px-3 py-2 bg-crypto-card border border-crypto-border rounded-lg text-crypto-text"
              >
                <option value={15000}>15 segundos</option>
                <option value={30000}>30 segundos</option>
                <option value={60000}>1 minuto</option>
                <option value={300000}>5 minutos</option>
              </select>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alert settings */}
      <AlertConfigPanel
        config={alertConfig}
        onConfigChange={setAlertConfig}
      />

      {/* About */}
      <Card>
        <CardHeader>
          <CardTitle>Sobre</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-crypto-muted">Versão</span>
            <span className="text-crypto-text">{APP_VERSION}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-crypto-muted">Ambiente</span>
            <span className="text-crypto-text">{process.env.NODE_ENV}</span>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-crypto-border">
        <Button
          variant="outline"
          onClick={resetSettings}
        >
          Restaurar padrões
        </Button>
        
        <div className="flex items-center gap-3">
          {saved && (
            <span className="text-sm text-score-high">✓ Salvo!</span>
          )}
          <Button variant="primary" onClick={handleSave}>
            Salvar alterações
          </Button>
        </div>
      </div>
    </div>
  );
}
