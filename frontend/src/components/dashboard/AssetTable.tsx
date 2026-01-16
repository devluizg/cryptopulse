/**
 * CryptoPulse - AssetTable Component
 * Tabela principal de ativos do dashboard
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScoreWithAsset } from '@/types';
import { Table, TableHeader, TableBody, TableHead, TableRow } from '@/components/ui/table';
import { AssetRow, AssetCard } from './AssetRow';
import { NoDataState, NoResultsState } from '@/components/common/EmptyState';
import { SkeletonTable } from '@/components/ui/skeleton';

interface AssetTableProps {
  assets: ScoreWithAsset[];
  isLoading?: boolean;
  showVolume?: boolean;
  compact?: boolean;
  onAssetSelect?: (asset: ScoreWithAsset) => void;
  emptyMessage?: string;
  className?: string;
}

export function AssetTable({
  assets,
  isLoading,
  showVolume = true,
  compact = false,
  onAssetSelect,
  emptyMessage,
  className,
}: AssetTableProps) {
  // Loading state
  if (isLoading) {
    return <SkeletonTable rows={8} />;
  }

  // Empty state
  if (assets.length === 0) {
    if (emptyMessage) {
      return <NoResultsState />;
    }
    return <NoDataState />;
  }

  return (
    <div className={cn('rounded-lg border border-crypto-border overflow-hidden', className)}>
      <Table>
        <TableHeader>
          <TableRow className="bg-crypto-card hover:bg-crypto-card">
            <TableHead className="w-[200px]">Ativo</TableHead>
            <TableHead className="w-[80px]">Score</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            {!compact && <TableHead className="text-right w-[120px]">Preço</TableHead>}
            <TableHead className="text-right w-[100px]">24h</TableHead>
            {showVolume && !compact && (
              <TableHead className="text-right w-[120px]">Volume</TableHead>
            )}
            {!compact && <TableHead className="w-[200px]">Principal Driver</TableHead>}
            <TableHead className="text-right w-[100px]">Atualizado</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {assets.map((asset) => (
            <AssetRow
              key={asset.asset_id}
              asset={asset}
              showVolume={showVolume}
              compact={compact}
              onSelect={onAssetSelect}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

// Grid de cards para mobile
interface AssetGridProps {
  assets: ScoreWithAsset[];
  isLoading?: boolean;
  onAssetSelect?: (asset: ScoreWithAsset) => void;
  className?: string;
}

export function AssetGrid({ assets, isLoading, onAssetSelect, className }: AssetGridProps) {
  if (isLoading) {
    return (
      <div className={cn('grid grid-cols-1 sm:grid-cols-2 gap-4', className)}>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-crypto-card animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (assets.length === 0) {
    return <NoDataState />;
  }

  return (
    <div className={cn('grid grid-cols-1 sm:grid-cols-2 gap-4', className)}>
      {assets.map((asset) => (
        <AssetCard key={asset.asset_id} asset={asset} onSelect={onAssetSelect} />
      ))}
    </div>
  );
}

// Highlight row for top movers
interface TopMoversProps {
  assets: ScoreWithAsset[];
  limit?: number;
  className?: string;
}

export function TopMovers({ assets, limit = 3, className }: TopMoversProps) {
  const topAssets = assets
    .filter((a) => a.status === 'high')
    .slice(0, limit);

  if (topAssets.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-2', className)}>
      <h3 className="text-sm font-medium text-crypto-muted flex items-center gap-2">
        <span className="w-2 h-2 bg-score-high rounded-full animate-pulse" />
        Zona de Explosão
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {topAssets.map((asset) => (
          <AssetCard key={asset.asset_id} asset={asset} />
        ))}
      </div>
    </div>
  );
}

export default AssetTable;
