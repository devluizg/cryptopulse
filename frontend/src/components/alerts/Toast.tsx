/**
 * CryptoPulse - Toast Notification System
 * Sistema de notificações toast em tempo real
 */

'use client';

import * as React from 'react';
import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { AlertSeverity } from '@/types';
import { ALERT_SEVERITY_COLORS } from '@/lib/constants';

export interface Toast {
  id: string;
  title: string;
  message?: string;
  severity: AlertSeverity;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  symbol?: string;
  onClose?: () => void;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearAll: () => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

interface ToastProviderProps {
  children: React.ReactNode;
  maxToasts?: number;
}

export function ToastProvider({ children, maxToasts = 5 }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>): string => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast: Toast = { ...toast, id };

    setToasts((prev) => {
      const updated = [newToast, ...prev];
      return updated.slice(0, maxToasts);
    });

    return id;
  }, [maxToasts]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearAll }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);
  const colors = ALERT_SEVERITY_COLORS[toast.severity];

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const duration = toast.duration ?? 5000;
    if (duration <= 0) return;

    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [toast.duration]);

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onRemove(toast.id);
      toast.onClose?.();
    }, 300);
  };

  const severityIcons: Record<AlertSeverity, string> = {
    info: 'ℹ️',
    warning: '⚠️',
    critical: '🚨',
  };

  return (
    <div
      className={cn(
        'pointer-events-auto transform transition-all duration-300 ease-out',
        isVisible && !isLeaving
          ? 'translate-x-0 opacity-100'
          : 'translate-x-full opacity-0'
      )}
    >
      <div
        className={cn(
          'p-4 rounded-lg border shadow-lg backdrop-blur-sm',
          'bg-crypto-dark/95',
          colors.border
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-lg">{severityIcons[toast.severity]}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h4 className={cn('font-semibold text-sm', colors.text)}>
                  {toast.title}
                </h4>
                {toast.symbol && (
                  <span className="px-1.5 py-0.5 text-xs bg-crypto-card rounded">
                    {toast.symbol}
                  </span>
                )}
              </div>
              {toast.message && (
                <p className="text-xs text-crypto-muted mt-1">{toast.message}</p>
              )}
            </div>
          </div>
          
          <button
            onClick={handleClose}
            className="text-crypto-muted hover:text-crypto-text transition-colors p-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {toast.action && (
          <div className="mt-3 flex justify-end">
            <button
              onClick={() => {
                toast.action?.onClick();
                handleClose();
              }}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded transition-colors',
                colors.bg,
                colors.text,
                'hover:opacity-80'
              )}
            >
              {toast.action.label}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export function useAlertToast() {
  const { addToast } = useToast();

  const showAlert = useCallback(
    (title: string, options?: {
      message?: string;
      severity?: AlertSeverity;
      symbol?: string;
      duration?: number;
      action?: Toast['action'];
    }) => {
      return addToast({
        title,
        message: options?.message,
        severity: options?.severity || 'info',
        symbol: options?.symbol,
        duration: options?.duration,
        action: options?.action,
      });
    },
    [addToast]
  );

  const showCritical = useCallback(
    (title: string, message?: string, symbol?: string) => {
      return addToast({ title, message, severity: 'critical', symbol, duration: 10000 });
    },
    [addToast]
  );

  const showWarning = useCallback(
    (title: string, message?: string, symbol?: string) => {
      return addToast({ title, message, severity: 'warning', symbol, duration: 7000 });
    },
    [addToast]
  );

  const showInfo = useCallback(
    (title: string, message?: string) => {
      return addToast({ title, message, severity: 'info', duration: 5000 });
    },
    [addToast]
  );

  return { showAlert, showCritical, showWarning, showInfo };
}

export default ToastProvider;
