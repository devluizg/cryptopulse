import * as React from 'react';
import { APP_NAME, APP_VERSION } from '@/lib/constants';

export function Footer() {
  return (
    <footer className="hidden lg:block border-t border-crypto-border bg-crypto-dark">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-score-high to-emerald-600 flex items-center justify-center">
              <span className="text-white text-xs font-bold">⚡</span>
            </div>
            <span className="text-sm text-crypto-muted">{APP_NAME} v{APP_VERSION}</span>
          </div>
          <p className="text-xs text-crypto-muted">Este produto não fornece aconselhamento financeiro.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
