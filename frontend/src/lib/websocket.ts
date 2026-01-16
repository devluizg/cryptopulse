/**
 * CryptoPulse - WebSocket Client
 * Cliente WebSocket para atualizações em tempo real
 */

import { WS_URL, ENABLE_WEBSOCKET } from './constants';
import { WebSocketMessage, ScoreUpdatePayload, PriceUpdatePayload } from '@/types';

// =========================================
// Types
// =========================================

type MessageHandler<T = unknown> = (payload: T) => void;

interface WebSocketHandlers {
  onScoreUpdate?: MessageHandler<ScoreUpdatePayload>;
  onPriceUpdate?: MessageHandler<PriceUpdatePayload>;
  onAlert?: MessageHandler<unknown>;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

interface WebSocketClientOptions {
  url?: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

// =========================================
// WebSocket Client Class
// =========================================

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: WebSocketHandlers = {};
  private reconnect: boolean;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private reconnectAttempts: number = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private isIntentionallyClosed: boolean = false;

  constructor(options: WebSocketClientOptions = {}) {
    this.url = options.url || WS_URL;
    this.reconnect = options.reconnect ?? true;
    this.reconnectInterval = options.reconnectInterval ?? 5000;
    this.maxReconnectAttempts = options.maxReconnectAttempts ?? 10;
  }

  /**
   * Conecta ao WebSocket
   */
  connect(handlers?: WebSocketHandlers): void {
    if (!ENABLE_WEBSOCKET) {
      console.warn('[WebSocket] WebSocket está desabilitado');
      return;
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      console.warn('[WebSocket] Já conectado');
      return;
    }

    if (handlers) {
      this.handlers = { ...this.handlers, ...handlers };
    }

    this.isIntentionallyClosed = false;

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventListeners();
    } catch (error) {
      console.error('[WebSocket] Erro ao criar conexão:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Configura event listeners
   */
  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('[WebSocket] Conectado');
      this.reconnectAttempts = 0;
      this.handlers.onConnect?.();
    };

    this.ws.onclose = (event) => {
      console.log('[WebSocket] Desconectado', event.code, event.reason);
      this.handlers.onDisconnect?.();

      if (!this.isIntentionallyClosed && this.reconnect) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] Erro:', error);
      this.handlers.onError?.(error);
    };

    this.ws.onmessage = (event) => {
      this.handleMessage(event);
    };
  }

  /**
   * Processa mensagens recebidas
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'score_update':
          this.handlers.onScoreUpdate?.(message.payload as ScoreUpdatePayload);
          break;
        case 'price_update':
          this.handlers.onPriceUpdate?.(message.payload as PriceUpdatePayload);
          break;
        case 'alert':
          this.handlers.onAlert?.(message.payload);
          break;
        case 'connection':
          console.log('[WebSocket] Mensagem de conexão:', message.payload);
          break;
        default:
          console.warn('[WebSocket] Tipo de mensagem desconhecido:', message.type);
      }
    } catch (error) {
      console.error('[WebSocket] Erro ao processar mensagem:', error);
    }
  }

  /**
   * Agenda reconexão
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Máximo de tentativas de reconexão atingido');
      return;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectAttempts++;
    console.log(
      `[WebSocket] Reconectando em ${this.reconnectInterval}ms (tentativa ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
    );

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  /**
   * Envia mensagem
   */
  send(type: string, payload: unknown): void {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Não conectado, não é possível enviar');
      return;
    }

    const message: WebSocketMessage = {
      type: type as WebSocketMessage['type'],
      payload,
      timestamp: new Date().toISOString(),
    };

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Desconecta do WebSocket
   */
  disconnect(): void {
    this.isIntentionallyClosed = true;

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    console.log('[WebSocket] Desconectado intencionalmente');
  }

  /**
   * Verifica se está conectado
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Retorna o estado atual
   */
  getState(): number | null {
    return this.ws?.readyState ?? null;
  }

  /**
   * Atualiza handlers
   */
  setHandlers(handlers: WebSocketHandlers): void {
    this.handlers = { ...this.handlers, ...handlers };
  }

  /**
   * Remove um handler específico
   */
  removeHandler(key: keyof WebSocketHandlers): void {
    delete this.handlers[key];
  }
}

// =========================================
// Singleton instance
// =========================================

let wsClient: WebSocketClient | null = null;

export function getWebSocketClient(): WebSocketClient {
  if (!wsClient) {
    wsClient = new WebSocketClient();
  }
  return wsClient;
}

export function createWebSocketClient(options?: WebSocketClientOptions): WebSocketClient {
  return new WebSocketClient(options);
}

// =========================================
// Exports
// =========================================

export { WebSocketClient };
export type { WebSocketHandlers, WebSocketClientOptions };
export default getWebSocketClient;
