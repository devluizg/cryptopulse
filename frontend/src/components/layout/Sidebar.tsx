/**
 * CryptoPulse - Sidebar Component
 * Barra lateral de navegação
 */

'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAlertStore, useAssetStore } from '@/store';
import { APP_NAME } from '@/lib/constants';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();
  const unreadCount = useAlertStore((state) => state.unreadCount);
  const stats = useAssetStore((state) => state.stats);

  const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: DashboardIcon },
    { name: 'Alertas', href: '/alerts', icon: AlertIcon, badge: unreadCount > 0 ? unreadCount : undefined },
    { name: 'Configurações', href: '/settings', icon: SettingsIcon },
  ];

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onClose} />}
      <aside className={cn(
        'fixed top-0 left-0 z-50 h-full w-64 bg-crypto-dark border-r border-crypto-border transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:z-auto',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex items-center h-16 px-4 border-b border-crypto-border">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-score-high to-emerald-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">⚡</span>
            </div>
            <span className="font-bold text-xl text-crypto-text">{APP_NAME}</span>
          </Link>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className={cn(
              'flex items-center justify-between px-3 py-2.5 rounded-lg transition-colors',
              pathname === item.href ? 'bg-crypto-card text-crypto-text' : 'text-crypto-muted hover:text-crypto-text hover:bg-crypto-card/50'
            )}>
              <div className="flex items-center space-x-3">
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </div>
              {item.badge && <span className="px-2 py-0.5 text-xs font-medium bg-score-low/20 text-score-low rounded-full">{item.badge > 99 ? '99+' : item.badge}</span>}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-crypto-border">
          <div className="text-xs text-crypto-muted mb-2">Resumo</div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-2 bg-crypto-card rounded">
              <div className="text-lg font-bold text-score-high">{stats.highCount}</div>
              <div className="text-xs text-crypto-muted">Alta</div>
            </div>
            <div className="p-2 bg-crypto-card rounded">
              <div className="text-lg font-bold text-score-attention">{stats.attentionCount}</div>
              <div className="text-xs text-crypto-muted">Atenção</div>
            </div>
            <div className="p-2 bg-crypto-card rounded">
              <div className="text-lg font-bold text-score-low">{stats.lowCount}</div>
              <div className="text-xs text-crypto-muted">Baixa</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

function DashboardIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>;
}

function AlertIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>;
}

function SettingsIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>;
}

export default Sidebar;
