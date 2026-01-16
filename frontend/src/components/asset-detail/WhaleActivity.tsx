/**
 * CryptoPulse - WhaleActivity Component
 * Exibe atividade de baleias
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { formatCurrency, formatRelativeTime, formatAddress } from '@/lib/formatters';

interface WhaleTransaction {
  id: string;
  type: 'in' | 'out';
  amount: number;
  amountUsd: number;
  fromAddress?: string;
  toAddress?: string;
  timestamp: string;
  exchange?: string;
}

interface WhaleActivityProps {
  transactions: WhaleTransaction[];
  isLoading?: boolean;
  className?: string;
}

export function WhaleActivity({ transactions, isLoading, className }: WhaleActivityProps) {
  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>🐋</span> Atividade de Baleias
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-crypto-border animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>🐋</span> Atividade de Baleias
          </div>
          <span className="text-sm font-normal text-crypto-muted">
            {transactions.length} transações
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <div className="text-center py-8 text-crypto-muted">
            Nenhuma transação de baleia recente
          </div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {transactions.map((tx) => (
              <WhaleTransactionItem key={tx.id} transaction={tx} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Individual transaction item
interface WhaleTransactionItemProps {
  transaction: WhaleTransaction;
}

function WhaleTransactionItem({ transaction }: WhaleTransactionItemProps) {
  const isInflow = transaction.type === 'in';

  return (
    <div
      className={cn(
        'p-3 rounded-lg border',
        isInflow
          ? 'bg-score-low/5 border-score-low/20'
          : 'bg-score-high/5 border-score-high/20'
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className={cn('text-lg', isInflow ? 'text-score-low' : 'text-score-high')}>
            {isInflow ? '📥' : '📤'}
          </span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-crypto-text">
                {formatCurrency(transaction.amountUsd, { compact: true })}
              </span>
              <span className={cn('text-xs', isInflow ? 'text-score-low' : 'text-score-high')}>
                {isInflow ? 'Entrada em Exchange' : 'Saída de Exchange'}
              </span>
            </div>
            <div className="text-xs text-crypto-muted mt-0.5">
              {transaction.amount.toLocaleString()} tokens
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-crypto-muted">
            {formatRelativeTime(transaction.timestamp)}
          </div>
          {transaction.exchange && (
            <div className="text-xs text-crypto-muted">{transaction.exchange}</div>
          )}
        </div>
      </div>

      {/* Addresses */}
      {(transaction.fromAddress || transaction.toAddress) && (
        <div className="mt-2 pt-2 border-t border-crypto-border/50 text-xs text-crypto-muted font-mono">
          {transaction.fromAddress && (
            <div>De: {formatAddress(transaction.fromAddress)}</div>
          )}
          {transaction.toAddress && (
            <div>Para: {formatAddress(transaction.toAddress)}</div>
          )}
        </div>
      )}
    </div>
  );
}

// Summary card
interface WhaleSummaryProps {
  inflow24h: number;
  outflow24h: number;
  netflow24h: number;
  className?: string;
}

export function WhaleSummary({ inflow24h, outflow24h, netflow24h, className }: WhaleSummaryProps) {
  const netflowColor = netflow24h >= 0 ? 'text-score-low' : 'text-score-high';
  const netflowLabel = netflow24h >= 0 ? 'Pressão de Venda' : 'Acumulação';

  return (
    <div className={cn('grid grid-cols-3 gap-4', className)}>
      <div className="text-center p-3 bg-crypto-card rounded-lg">
        <div className="text-score-low text-lg mb-1">📥</div>
        <div className="text-sm text-crypto-muted">Entrada</div>
        <div className="font-bold text-crypto-text">
          {formatCurrency(inflow24h, { compact: true })}
        </div>
      </div>
      <div className="text-center p-3 bg-crypto-card rounded-lg">
        <div className="text-score-high text-lg mb-1">📤</div>
        <div className="text-sm text-crypto-muted">Saída</div>
        <div className="font-bold text-crypto-text">
          {formatCurrency(outflow24h, { compact: true })}
        </div>
      </div>
      <div className="text-center p-3 bg-crypto-card rounded-lg">
        <div className={cn('text-lg mb-1', netflowColor)}>
          {netflow24h >= 0 ? '⚠️' : '✅'}
        </div>
        <div className="text-sm text-crypto-muted">Netflow</div>
        <div className={cn('font-bold', netflowColor)}>
          {formatCurrency(Math.abs(netflow24h), { compact: true })}
        </div>
        <div className={cn('text-xs', netflowColor)}>{netflowLabel}</div>
      </div>
    </div>
  );
}

export default WhaleActivity;
