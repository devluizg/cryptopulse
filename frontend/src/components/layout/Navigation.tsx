'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAlertStore } from '@/store';

export function MobileNavigation() {
  const pathname = usePathname();
  const unreadCount = useAlertStore((state) => state.unreadCount);

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/alerts', label: 'Alertas', icon: '🔔', badge: unreadCount > 0 ? unreadCount : undefined },
    { href: '/settings', label: 'Config', icon: '⚙️' },
  ];

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-crypto-dark/95 backdrop-blur border-t border-crypto-border">
      <div className="flex items-center justify-around h-16">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href} className={cn(
            'flex flex-col items-center justify-center gap-1 px-4 py-2 relative',
            pathname === item.href ? 'text-score-high' : 'text-crypto-muted'
          )}>
            <span className="relative text-xl">
              {item.icon}
              {item.badge && (
                <span className="absolute -top-1 -right-2 min-w-[16px] h-4 flex items-center justify-center text-[10px] font-bold bg-red-500 text-white rounded-full">
                  {item.badge > 99 ? '99+' : item.badge}
                </span>
              )}
            </span>
            <span className="text-xs font-medium">{item.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}

export default MobileNavigation;
