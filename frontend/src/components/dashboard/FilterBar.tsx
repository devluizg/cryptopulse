/**
 * CryptoPulse - FilterBar Component
 * Barra de filtros e busca do dashboard
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { AssetFilter, ScoreStatus } from '@/types';

interface FilterBarProps {
  filter: AssetFilter;
  onFilterChange: (filter: Partial<AssetFilter>) => void;
  onReset: () => void;
  totalCount?: number;
  filteredCount?: number;
  className?: string;
}

export function FilterBar({
  filter,
  onFilterChange,
  onReset,
  totalCount = 0,
  filteredCount = 0,
  className,
}: FilterBarProps) {
  const [searchValue, setSearchValue] = React.useState(filter.search || '');

  // Debounce search
  React.useEffect(() => {
    const timeout = setTimeout(() => {
      onFilterChange({ search: searchValue });
    }, 300);
    return () => clearTimeout(timeout);
  }, [searchValue, onFilterChange]);

  const statusOptions: { value: ScoreStatus | 'all'; label: string; color: string }[] = [
    { value: 'all', label: 'Todos', color: 'text-crypto-text' },
    { value: 'high', label: 'Explosão', color: 'text-score-high' },
    { value: 'attention', label: 'Atenção', color: 'text-score-attention' },
    { value: 'low', label: 'Baixo', color: 'text-score-low' },
  ];

  const sortOptions: { value: AssetFilter['sortBy']; label: string }[] = [
    { value: 'score', label: 'Score' },
    { value: 'name', label: 'Nome' },
    { value: 'change', label: 'Variação' },
  ];

  const hasActiveFilters =
    filter.status !== 'all' || filter.search || filter.sortBy !== 'score';

  return (
    <div className={cn('space-y-4', className)}>
      {/* Search and main filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-crypto-muted"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Buscar por símbolo ou nome..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-crypto-card border border-crypto-border rounded-lg text-crypto-text placeholder-crypto-muted focus:outline-none focus:ring-2 focus:ring-score-high/50"
          />
          {searchValue && (
            <button
              onClick={() => setSearchValue('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-crypto-muted hover:text-crypto-text"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Status filter */}
        <div className="flex items-center gap-1 bg-crypto-card border border-crypto-border rounded-lg p-1">
          {statusOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onFilterChange({ status: option.value })}
              className={cn(
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                filter.status === option.value
                  ? 'bg-crypto-border text-crypto-text'
                  : 'text-crypto-muted hover:text-crypto-text'
              )}
            >
              <span className={filter.status === option.value ? option.color : ''}>
                {option.label}
              </span>
            </button>
          ))}
        </div>

        {/* Sort */}
        <select
          value={filter.sortBy}
          onChange={(e) => onFilterChange({ sortBy: e.target.value as AssetFilter['sortBy'] })}
          className="px-3 py-2 bg-crypto-card border border-crypto-border rounded-lg text-crypto-text focus:outline-none focus:ring-2 focus:ring-score-high/50"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              Ordenar por: {option.label}
            </option>
          ))}
        </select>

        {/* Sort order toggle */}
        <Button
          variant="outline"
          size="icon"
          onClick={() =>
            onFilterChange({
              sortOrder: filter.sortOrder === 'desc' ? 'asc' : 'desc',
            })
          }
          title={filter.sortOrder === 'desc' ? 'Decrescente' : 'Crescente'}
        >
          {filter.sortOrder === 'desc' ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          )}
        </Button>
      </div>

      {/* Results count and reset */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-crypto-muted">
          Exibindo {filteredCount} de {totalCount} ativos
        </span>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onReset}>
            Limpar filtros
          </Button>
        )}
      </div>
    </div>
  );
}

export default FilterBar;
