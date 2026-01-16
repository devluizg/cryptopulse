/**
 * CryptoPulse - useWebSocket Hook
 * Hook para conexão WebSocket em tempo real
 */

import { useEffect, useCallback, useState, useRef } from 'react';
import { useAssetStore } from '@/store';
import { useAlertStore } from '@/store';
import { ScoreUpdatePayload, PriceUpdatePayload, AlertWithAsset } from '@/types';
import { ENABLE_WEBSOCKET, WS_URL } from '@/lib/constants';
import { getScoreStatus } from '@/lib/utils';

// Estado global para compartilhar entre hooks
let globalIsConnected = false;
const listeners: Set<(connected: boolean) => void> = new Set();

function notifyListeners(connected: boolean) {
  globalIsConnected = connected;
  listeners.forEach(listener => listener(connected));
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  lastMessage: unknown | null;
  error: string | null;
}

interface UseWebSocketOptions {
  autoConnect?: boolean;
  onScoreUpdate?: (payload: ScoreUpdatePayload) => void;
  onPriceUpdate?: (payload: PriceUpdatePayload) => void;
  onAlert?: (alert: AlertWithAsset) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const { autoConnect = false } = options; // Desabilitado por padrão, AlertProvider gerencia

  const [isConnected, setIsConnected] = useState(globalIsConnected);
  const [lastMessage, setLastMessage] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  
  // Store actions
  const updateAssetScore = useAssetStore((state) => state.updateAssetScore);
  const addAlert = useAlertStore((state) => state.addAlert);

  // Sincronizar com estado global
  useEffect(() => {
    const listener = (connected: boolean) => setIsConnected(connected);
    listeners.add(listener);
    setIsConnected(globalIsConnected);
    return () => { listeners.delete(listener); };
  }, []);

  // Handler de mensagens
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      setLastMessage(data);

      if (data.type === 'score_update' && data.payload) {
        const payload = data.payload as ScoreUpdatePayload;
        const status = getScoreStatus(payload.new_score);
        updateAssetScore(payload.asset_id, payload.new_score, status);
        options.onScoreUpdate?.(payload);
      }

      if (data.type === 'price_update' && data.payload) {
        options.onPriceUpdate?.(data.payload);
      }

      if (data.type === 'alert' && data.payload) {
        addAlert(data.payload as AlertWithAsset);
        options.onAlert?.(data.payload as AlertWithAsset);
      }
    } catch (e) {
      // Ignorar erros de parse
    }
  }, [updateAssetScore, addAlert, options]);

  const connect = useCallback(() => {
    if (!ENABLE_WEBSOCKET || typeof window === 'undefined') return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        notifyListeners(true);
        setError(null);
      };

      ws.onclose = () => {
        notifyListeners(false);
      };

      ws.onerror = () => {
        setError('Erro de conexão WebSocket');
      };

      ws.onmessage = handleMessage;
      wsRef.current = ws;
    } catch (e) {
      setError('Falha ao conectar WebSocket');
    }
  }, [handleMessage]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return { isConnected, connect, disconnect, lastMessage, error };
}

/**
 * Hook simplificado para status de conexão
 */
export function useWebSocketStatus(): boolean {
  const [isConnected, setIsConnected] = useState(globalIsConnected);

  useEffect(() => {
    const listener = (connected: boolean) => setIsConnected(connected);
    listeners.add(listener);
    setIsConnected(globalIsConnected);
    return () => { listeners.delete(listener); };
  }, []);

  return isConnected;
}

// Função para notificar de fora (usado pelo AlertProvider)
export function setWebSocketConnected(connected: boolean) {
  notifyListeners(connected);
}

export default useWebSocket;
