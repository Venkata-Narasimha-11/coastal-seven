import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseWebSocketOptions<T> {
  onMessage?: (data: T) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
}

export interface UseWebSocketReturn<T> {
  isConnected: boolean;
  lastMessage: T | null;
  sendMessage: (data: unknown) => boolean;
  reconnectCount: number;
  disconnect: () => void;
}

/**
 * Reusable WebSocket hook with Exponential Backoff reconnection.
 * Handles lifecycle, heartbeats, and message dispatch.
 */
export function useWebSocket<T = any>(
  url: string | null,
  options: UseWebSocketOptions<T> = {}
): UseWebSocketReturn<T> {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    autoReconnect = true,
    maxRetries = 5,
    baseDelay = 1000,
    maxDelay = 10000,
  } = options;

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  const [reconnectCount, setReconnectCount] = useState<number>(0);

  const wsRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef<number>(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isManuallyClosedRef = useRef<boolean>(false);

  // Use refs for callbacks to avoid re-triggering connect effect
  const onMessageRef = useRef(onMessage);
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onMessageRef.current = onMessage;
    onOpenRef.current = onOpen;
    onCloseRef.current = onClose;
    onErrorRef.current = onError;
  }, [onMessage, onOpen, onClose, onError]);

  const connect = useCallback(() => {
    if (!url) return;

    // Reset manual close flag on new connection attempt
    isManuallyClosedRef.current = false;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`[WebSocket] Connected: ${url}`);
        setIsConnected(true);
        retryCountRef.current = 0;
        setReconnectCount(0);
        onOpenRef.current?.();
      };

      ws.onmessage = (event: MessageEvent) => {
        try {
          const parsed = JSON.parse(event.data) as T;
          setLastMessage(parsed);
          onMessageRef.current?.(parsed);
        } catch {
          // If not JSON, pass as string
          setLastMessage(event.data as unknown as T);
          onMessageRef.current?.(event.data as unknown as T);
        }
      };

      ws.onerror = (err: Event) => {
        console.warn(`[WebSocket] Error:`, err);
        onErrorRef.current?.(err);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log(`[WebSocket] Disconnected: ${url}`);
        onCloseRef.current?.();

        // Check if should auto-reconnect
        if (!isManuallyClosedRef.current && autoReconnect && retryCountRef.current < maxRetries) {
          // Exponential backoff: baseDelay * 2^attempt, capped at maxDelay
          const delay = Math.min(
            baseDelay * Math.pow(2, retryCountRef.current),
            maxDelay
          );

          console.log(
            `[WebSocket] Reconnecting in ${delay / 1000}s (Attempt ${retryCountRef.current + 1}/${maxRetries})...`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            retryCountRef.current += 1;
            setReconnectCount(retryCountRef.current);
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('[WebSocket] Connection initialization failed:', err);
    }
  }, [url, autoReconnect, maxRetries, baseDelay, maxDelay]);

  // Send message safely
  const sendMessage = useCallback((data: unknown): boolean => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'string' ? data : JSON.stringify(data);
      wsRef.current.send(payload);
      return true;
    }
    console.warn('[WebSocket] Cannot send message: connection not OPEN');
    return false;
  }, []);

  // Disconnect manually
  const disconnect = useCallback(() => {
    isManuallyClosedRef.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Connect on mount or when url changes, cleanup on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    reconnectCount,
    disconnect,
  };
}

export default useWebSocket;
