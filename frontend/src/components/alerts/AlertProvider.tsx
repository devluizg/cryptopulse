/**
 * CryptoPulse - Alert Provider
 * Provider para gerenciamento de alertas em tempo real
 */

'use client';

import * as React from 'react';
import { createContext, useContext, useEffect, useCallback, useState, useRef } from 'react';
import { useAlertStore } from '@/store';
import { useSettingsStore } from '@/store';
import { AlertWithAsset } from '@/types';
import { playAlertSound } from '@/lib/sounds';
import { useToast } from './Toast';
import { ENABLE_WEBSOCKET, WS_URL } from '@/lib/constants';
import { setWebSocketConnected } from '@/hooks/useWebSocket';

interface AlertContextValue {
  notificationPermission: NotificationPermission;
  requestNotificationPermission: () => Promise<boolean>;
  soundEnabled: boolean;
  toggleSound: () => void;
  isConnected: boolean;
  lastAlert: AlertWithAsset | null;
}

const AlertContext = createContext<AlertContextValue | null>(null);

export function useAlertContext() {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error('useAlertContext must be used within an AlertProvider');
  }
  return context;
}

export function AlertProvider({ children }: { children: React.ReactNode }) {
  const [notificationPermission, setNotificationPermission] = useState<NotificationPermission>('default');
  const [lastAlert, setLastAlert] = useState<AlertWithAsset | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const { addToast } = useToast();
  const addAlertToStore = useAlertStore((state) => state.addAlert);
  const soundEnabled = useSettingsStore((state) => state.soundEnabled);
  const setSoundEnabled = useSettingsStore((state) => state.setSoundEnabled);
  const alertConfig = useSettingsStore((state) => state.alertConfig);

  // Verificar permissão de notificação no mount
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setNotificationPermission(Notification.permission);
    }
  }, []);

  // Handler para mensagens WebSocket
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'alert' && data.payload) {
        const alert = data.payload as AlertWithAsset;
        setLastAlert(alert);
        addAlertToStore(alert);

        // Verificar se deve mostrar baseado nas configurações
        if (alertConfig.severityFilter.includes(alert.severity)) {
          addToast({
            title: alert.title,
            message: alert.message,
            severity: alert.severity,
            symbol: alert.symbol,
            duration: alert.severity === 'critical' ? 10000 : 5000,
          });

          if (soundEnabled && alertConfig.enableSound) {
            playAlertSound(alert.severity);
          }
        }
      }
    } catch (e) {
      // Ignorar erros de parse silenciosamente
    }
  }, [addAlertToStore, addToast, soundEnabled, alertConfig]);

  // Atualizar estado global quando conectar/desconectar
  const updateConnectionState = useCallback((connected: boolean) => {
    setIsConnected(connected);
    setWebSocketConnected(connected); // Notifica o hook global
  }, []);

  // Conectar WebSocket
  const connect = useCallback(() => {
    if (!ENABLE_WEBSOCKET || typeof window === 'undefined') {
      return;
    }

    // Não reconectar se já existe conexão
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        if (mountedRef.current) {
          updateConnectionState(true);
          console.log('[WebSocket] Conectado');
        }
      };

      ws.onclose = () => {
        if (mountedRef.current) {
          updateConnectionState(false);
          console.log('[WebSocket] Desconectado');
          
          // Reconectar após 5 segundos
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }
          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              connect();
            }
          }, 5000);
        }
      };

      ws.onerror = () => {
        console.log('[WebSocket] Erro de conexão');
      };

      ws.onmessage = handleMessage;

      wsRef.current = ws;
    } catch (e) {
      console.error('[WebSocket] Erro ao criar conexão:', e);
    }
  }, [handleMessage, updateConnectionState]);

  // Conectar ao montar
  useEffect(() => {
    mountedRef.current = true;
    
    // Delay inicial para evitar múltiplas conexões durante HMR
    const timer = setTimeout(() => {
      if (mountedRef.current) {
        connect();
      }
    }, 1000);

    return () => {
      mountedRef.current = false;
      
      clearTimeout(timer);
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      
      updateConnectionState(false);
    };
  }, [connect, updateConnectionState]);

  // Solicitar permissão de notificação
  const requestNotificationPermission = useCallback(async (): Promise<boolean> => {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      setNotificationPermission(permission);
      return permission === 'granted';
    } catch {
      return false;
    }
  }, []);

  // Toggle som
  const toggleSound = useCallback(() => {
    setSoundEnabled(!soundEnabled);
  }, [soundEnabled, setSoundEnabled]);

  const value: AlertContextValue = {
    notificationPermission,
    requestNotificationPermission,
    soundEnabled,
    toggleSound,
    isConnected,
    lastAlert,
  };

  return <AlertContext.Provider value={value}>{children}</AlertContext.Provider>;
}

export default AlertProvider;
