/**
 * CryptoPulse - AssetRow Component
 * Linha individual da tabela de ativos
 */

'use client';

import * as React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { ScoreWithAsset } from '@/types';
import { formatCurrency, formatPercent, formatRelativeTime, formatVolume } from '@/lib/formatters';
import { CRYPTO_ICONS } from '@/lib/constants';
import { MiniScoreBadge } from './ScoreBadge';
import { StatusIndicator } from './StatusIndicator';
import { TableRow, TableCell } from '@/components/ui/table';

interface AssetRowProps {
  asset: ScoreWithAsset;
  showVolume?: boolean;
  compact?: boolean;
  onSelect?: (asset: ScoreWithAsset) => void;
}

export function AssetRow({ asset, showVolume = true, compact = false, onSelect }: AssetRowProps) {
  const priceChangeColor =
    asset.price_change_24h !== null && asset.price_change_24h >= 0
      ? 'text-score-high'
      : 'text-score-low';

  const cryptoIcon = CRYPTO_ICONS[asset.symbol] || '●';

  return (
    <TableRow
      className={cn(
        'cursor-pointer hover:bg-crypto-card/50 transition-colors',
        asset.status === 'high' && 'bg-score-high/5'
      )}
      onClick={() => onSelect?.(asset)}
    >
      {/* Asset Info */}
      <TableCell>
        <Link
          href={`/asset/${asset.symbol}`}
          className="flex items-center gap-3"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="w-10 h-10 rounded-full bg-crypto-border flex items-center justify-center text-lg">
            {cryptoIcon}
          </div>
          <div>
            <div className="font-semibold text-crypto-text">{asset.symbol}</div>
            <div className="text-xs text-crypto-muted">{asset.asset_name}</div>
          </div>
        </Link>
      </TableCell>

      {/* Score */}
      <TableCell>
        <MiniScoreBadge score={asset.explosion_score} status={asset.status} />
      </TableCell>

      {/* Status */}
      <TableCell>
        <StatusIndicator
          status={asset.status}
          size="sm"
          pulse={asset.status === 'high'}
        />
      </TableCell>

      {/* Price */}
      {!compact && (
        <TableCell className="text-right">
          <div className="font-mono text-crypto-text">
            {formatCurrency(asset.price_usd)}
          </div>
        </TableCell>
      )}

      {/* 24h Change */}
      <TableCell className="text-right">
        <span className={cn('font-mono', priceChangeColor)}>
          {formatPercent(asset.price_change_24h)}
        </span>
      </TableCell>

      {/* Volume */}
      {showVolume && !compact && (
        <TableCell className="text-right text-crypto-muted font-mono">
          {formatVolume(asset.volume_24h)}
        </TableCell>
      )}

      {/* Main Driver */}
      {!compact && (
        <TableCell className="max-w-[200px]">
          <span className="text-xs text-crypto-muted truncate block">
            {asset.main_drivers || 'Volume elevado'}
          </span>
        </TableCell>
      )}

      {/* Updated */}
      <TableCell className="text-right text-xs text-crypto-muted">
        {formatRelativeTime(asset.calculated_at)}
      </TableCell>
    </TableRow>
  );
}

// Versão card para mobile
interface AssetCardProps {
  asset: ScoreWithAsset;
  onSelect?: (asset: ScoreWithAsset) => void;
}

export function AssetCard({ asset, onSelect }: AssetCardProps) {
  const priceChangeColor =
    asset.price_change_24h !== null && asset.price_change_24h >= 0
      ? 'text-score-high'
      : 'text-score-low';

  const cryptoIcon = CRYPTO_ICONS[asset.symbol] || '●';

  return (
    <div
      className={cn(
        'p-4 bg-crypto-card border border-crypto-border rounded-lg cursor-pointer hover:border-crypto-muted transition-colors',
        asset.status === 'high' && 'border-score-high/30'
      )}
      onClick={() => onSelect?.(asset)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-crypto-border flex items-center justify-center text-lg">
            {cryptoIcon}
          </div>
          <div>
            <div className="font-semibold text-crypto-text">{asset.symbol}</div>
            <div className="text-xs text-crypto-muted">{asset.asset_name}</div>
          </div>
        </div>
        <MiniScoreBadge score={asset.explosion_score} status={asset.status} />
      </div>

      <div className="flex items-center justify-between">
        <div>
          <div className="font-mono text-crypto-text">
            {formatCurrency(asset.price_usd)}
          </div>
          <span className={cn('text-sm font-mono', priceChangeColor)}>
            {formatPercent(asset.price_change_24h)}
          </span>
        </div>
        <StatusIndicator status={asset.status} size="sm" showLabel={false} pulse={asset.status === 'high'} />
      </div>
    </div>
  );
}

export default AssetRow;
