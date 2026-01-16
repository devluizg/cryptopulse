/**
 * CryptoPulse - TimelineEvents Component
 * Timeline de eventos do ativo
 */

'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { formatRelativeTime, formatDate } from '@/lib/formatters';

interface TimelineEvent {
  id: string;
  type: 'score_change' | 'whale' | 'news' | 'price' | 'alert';
  title: string;
  description?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

interface TimelineEventsProps {
  events: TimelineEvent[];
  isLoading?: boolean;
  maxEvents?: number;
  className?: string;
}

export function TimelineEvents({
  events,
  isLoading,
  maxEvents = 10,
  className,
}: TimelineEventsProps) {
  const displayedEvents = events.slice(0, maxEvents);

  const eventIcons: Record<TimelineEvent['type'], { icon: string; color: string }> = {
    score_change: { icon: '📊', color: 'bg-blue-500' },
    whale: { icon: '🐋', color: 'bg-purple-500' },
    news: { icon: '📰', color: 'bg-yellow-500' },
    price: { icon: '💰', color: 'bg-green-500' },
    alert: { icon: '🔔', color: 'bg-red-500' },
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Timeline de Eventos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex gap-3">
                <div className="w-8 h-8 bg-crypto-border animate-pulse rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-crypto-border animate-pulse rounded w-3/4" />
                  <div className="h-3 bg-crypto-border animate-pulse rounded w-1/2" />
                </div>
              </div>
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
          <span>Timeline de Eventos</span>
          <span className="text-sm font-normal text-crypto-muted">
            {events.length} eventos
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {displayedEvents.length === 0 ? (
          <div className="text-center py-8 text-crypto-muted">
            Nenhum evento recente
          </div>
        ) : (
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-4 top-0 bottom-0 w-px bg-crypto-border" />

            {/* Events */}
            <div className="space-y-4">
              {displayedEvents.map((event, index) => {
                const { icon, color } = eventIcons[event.type];
                return (
                  <div key={event.id} className="relative flex gap-4 pl-2">
                    {/* Icon */}
                    <div
                      className={cn(
                        'relative z-10 w-8 h-8 rounded-full flex items-center justify-center text-sm',
                        color
                      )}
                    >
                      {icon}
                    </div>

                    {/* Content */}
                    <div className="flex-1 pb-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-crypto-text">
                            {event.title}
                          </h4>
                          {event.description && (
                            <p className="text-sm text-crypto-muted mt-0.5">
                              {event.description}
                            </p>
                          )}
                        </div>
                        <time className="text-xs text-crypto-muted whitespace-nowrap ml-2">
                          {formatRelativeTime(event.timestamp)}
                        </time>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {events.length > maxEvents && (
          <div className="text-center pt-4 border-t border-crypto-border">
            <button className="text-sm text-score-high hover:underline">
              Ver todos os {events.length} eventos
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Compact timeline for sidebar
interface CompactTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

export function CompactTimeline({ events, className }: CompactTimelineProps) {
  const recentEvents = events.slice(0, 5);

  return (
    <div className={cn('space-y-2', className)}>
      {recentEvents.map((event) => (
        <div
          key={event.id}
          className="flex items-center gap-2 text-sm p-2 bg-crypto-card rounded"
        >
          <span>{event.type === 'whale' ? '🐋' : event.type === 'news' ? '📰' : '📊'}</span>
          <span className="text-crypto-text truncate flex-1">{event.title}</span>
          <span className="text-xs text-crypto-muted">
            {formatRelativeTime(event.timestamp)}
          </span>
        </div>
      ))}
    </div>
  );
}

export default TimelineEvents;
