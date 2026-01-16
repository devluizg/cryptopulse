/**
 * CryptoPulse - Badge Component
 * Componente de badge/tag reutilizável
 */

import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScoreStatus, AlertSeverity } from '@/types';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'outline' | 'high' | 'attention' | 'low' | 'info' | 'warning' | 'critical';
  size?: 'sm' | 'md' | 'lg';
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center font-medium rounded-full';

    const variants = {
      default: 'bg-crypto-border text-crypto-text',
      outline: 'border border-crypto-border text-crypto-text bg-transparent',
      high: 'bg-score-high/10 text-score-high border border-score-high/30',
      attention: 'bg-score-attention/10 text-score-attention border border-score-attention/30',
      low: 'bg-score-low/10 text-score-low border border-score-low/30',
      info: 'bg-blue-500/10 text-blue-400 border border-blue-500/30',
      warning: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30',
      critical: 'bg-red-500/10 text-red-400 border border-red-500/30',
    };

    const sizes = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-0.5 text-sm',
      lg: 'px-3 py-1 text-base',
    };

    return (
      <span
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

// Helper component for score status
interface StatusBadgeProps {
  status: ScoreStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const statusLabels: Record<ScoreStatus, string> = {
  high: 'Explosão',
  attention: 'Atenção',
  low: 'Baixo',
};

export function StatusBadge({ status, size = 'md', showLabel = true, className }: StatusBadgeProps) {
  return (
    <Badge variant={status} size={size} className={className}>
      {showLabel && statusLabels[status]}
    </Badge>
  );
}

// Helper component for alert severity
interface SeverityBadgeProps {
  severity: AlertSeverity;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const severityLabels: Record<AlertSeverity, string> = {
  info: 'Info',
  warning: 'Atenção',
  critical: 'Crítico',
};

export function SeverityBadge({ severity, size = 'md', className }: SeverityBadgeProps) {
  return (
    <Badge variant={severity} size={size} className={className}>
      {severityLabels[severity]}
    </Badge>
  );
}

export { Badge };
export default Badge;
