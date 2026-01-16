'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useWebSocketStatus } from '@/hooks/useWebSocket';
import { APP_NAME } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { AlertBell } from '@/components/alerts/AlertBell';

export function Header() {
  const pathname = usePathname();
  const isConnected = useWebSocketStatus();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-crypto-border bg-crypto-dark/95 backdrop-blur">
      <div className="container flex h-16 items-center px-4">
        <Link href="/" className="flex items-center space-x-2 mr-8">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-score-high to-emerald-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">⚡</span>
          </div>
          <span className="font-bold text-xl text-crypto-text hidden sm:inline-block">{APP_NAME}</span>
        </Link>

        <nav className="flex items-center space-x-1 flex-1">
          <NavLink href="/dashboard" active={pathname === '/dashboard'}>Dashboard</NavLink>
          <NavLink href="/alerts" active={pathname === '/alerts'}>Alertas</NavLink>
          <NavLink href="/settings" active={pathname === '/settings'}>Config</NavLink>
        </nav>

        <div className="flex items-center space-x-2">
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-crypto-card/50">
            <span className={cn('w-2 h-2 rounded-full', isConnected ? 'bg-score-high animate-pulse' : 'bg-crypto-muted')} />
            <span className="text-xs text-crypto-muted">{isConnected ? 'Live' : 'Offline'}</span>
          </div>
          <AlertBell />
        </div>
      </div>
    </header>
  );
}

function NavLink({ href, active, children }: { href: string; active?: boolean; children: React.ReactNode }) {
  return (
    <Link href={href} className={cn(
      'hidden lg:flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
      active ? 'bg-crypto-card text-crypto-text' : 'text-crypto-muted hover:text-crypto-text hover:bg-crypto-card/50'
    )}>
      {children}
    </Link>
  );
}

export default Header;
