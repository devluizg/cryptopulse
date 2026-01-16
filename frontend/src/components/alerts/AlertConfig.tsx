/**
 * CryptoPulse - AlertConfig Component
 * Configurações de alertas
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { AlertConfig as AlertConfigType, AlertSeverity } from '@/types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface AlertConfigProps {
  config: AlertConfigType;
  onConfigChange: (config: Partial<AlertConfigType>) => void;
  onSave?: () => void;
  className?: string;
}

export function AlertConfigPanel({
  config,
  onConfigChange,
  onSave,
  className,
}: AlertConfigProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Score Threshold */}
      <Card>
        <CardHeader>
          <CardTitle>Limite de Score</CardTitle>
          <CardDescription>
            Receber alertas quando um ativo atingir este score
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-crypto-muted">Score mínimo para alerta</span>
              <span className="text-2xl font-bold text-score-high">
                {config.scoreThreshold}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={config.scoreThreshold}
              onChange={(e) =>
                onConfigChange({ scoreThreshold: parseInt(e.target.value) })
              }
              className="w-full h-2 bg-crypto-border rounded-lg appearance-none cursor-pointer accent-score-high"
            />
            <div className="flex justify-between text-xs text-crypto-muted">
              <span>0</span>
              <span>50</span>
              <span>100</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Channels */}
      <Card>
        <CardHeader>
          <CardTitle>Canais de Notificação</CardTitle>
          <CardDescription>
            Como você deseja receber os alertas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ToggleOption
            label="Notificações Push"
            description="Receber no navegador"
            enabled={config.enablePush}
            onChange={(enabled) => onConfigChange({ enablePush: enabled })}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            }
          />
          
          <ToggleOption
            label="Email"
            description="Receber por email"
            enabled={config.enableEmail}
            onChange={(enabled) => onConfigChange({ enableEmail: enabled })}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            }
          />

          <ToggleOption
            label="Som"
            description="Tocar som ao receber alerta"
            enabled={config.enableSound}
            onChange={(enabled) => onConfigChange({ enableSound: enabled })}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            }
          />
        </CardContent>
      </Card>

      {/* Severity Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Filtro de Severidade</CardTitle>
          <CardDescription>
            Quais níveis de alerta você deseja receber
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <SeverityCheckbox
              severity="critical"
              label="Crítico"
              description="Alertas de alta prioridade"
              checked={config.severityFilter.includes('critical')}
              onChange={(checked) => {
                const newFilter = checked
                  ? [...config.severityFilter, 'critical']
                  : config.severityFilter.filter((s) => s !== 'critical');
                onConfigChange({ severityFilter: newFilter as AlertSeverity[] });
              }}
              color="text-red-400"
            />
            <SeverityCheckbox
              severity="warning"
              label="Atenção"
              description="Alertas importantes"
              checked={config.severityFilter.includes('warning')}
              onChange={(checked) => {
                const newFilter = checked
                  ? [...config.severityFilter, 'warning']
                  : config.severityFilter.filter((s) => s !== 'warning');
                onConfigChange({ severityFilter: newFilter as AlertSeverity[] });
              }}
              color="text-yellow-400"
            />
            <SeverityCheckbox
              severity="info"
              label="Informativo"
              description="Atualizações gerais"
              checked={config.severityFilter.includes('info')}
              onChange={(checked) => {
                const newFilter = checked
                  ? [...config.severityFilter, 'info']
                  : config.severityFilter.filter((s) => s !== 'info');
                onConfigChange({ severityFilter: newFilter as AlertSeverity[] });
              }}
              color="text-blue-400"
            />
          </div>
        </CardContent>
      </Card>

      {/* Save button */}
      {onSave && (
        <Button variant="primary" onClick={onSave} className="w-full">
          Salvar Configurações
        </Button>
      )}
    </div>
  );
}

// Toggle option component
interface ToggleOptionProps {
  label: string;
  description: string;
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  icon?: React.ReactNode;
}

function ToggleOption({ label, description, enabled, onChange, icon }: ToggleOptionProps) {
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-darker rounded-lg">
      <div className="flex items-center gap-3">
        {icon && <span className="text-crypto-muted">{icon}</span>}
        <div>
          <div className="font-medium text-crypto-text">{label}</div>
          <div className="text-xs text-crypto-muted">{description}</div>
        </div>
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={cn(
          'relative w-12 h-6 rounded-full transition-colors',
          enabled ? 'bg-score-high' : 'bg-crypto-border'
        )}
      >
        <span
          className={cn(
            'absolute top-1 w-4 h-4 bg-white rounded-full transition-transform',
            enabled ? 'left-7' : 'left-1'
          )}
        />
      </button>
    </div>
  );
}

// Severity checkbox component
interface SeverityCheckboxProps {
  severity: AlertSeverity;
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  color: string;
}

function SeverityCheckbox({
  label,
  description,
  checked,
  onChange,
  color,
}: SeverityCheckboxProps) {
  return (
    <label className="flex items-center gap-3 p-3 bg-crypto-darker rounded-lg cursor-pointer hover:bg-crypto-card transition-colors">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="w-4 h-4 rounded border-crypto-border bg-crypto-dark text-score-high focus:ring-score-high focus:ring-offset-crypto-dark"
      />
      <div className="flex-1">
        <div className={cn('font-medium', color)}>{label}</div>
        <div className="text-xs text-crypto-muted">{description}</div>
      </div>
    </label>
  );
}

export default AlertConfigPanel;
