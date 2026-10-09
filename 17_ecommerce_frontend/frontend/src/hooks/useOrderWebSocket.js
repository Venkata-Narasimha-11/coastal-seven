import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook to connect to the backend WebSocket endpoint for live order updates.
 * Route: `/ws/orders/${orderId}`
 */
export const useOrderWebSocket = (orderId, initialStatus = null) => {
  const [currentStatus, setCurrentStatus] = useState(initialStatus);
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!orderId) return;

    // Use current host and protocol for WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host; // will use Vite proxy during development
    const wsUrl = `${protocol}//${host}/ws/orders/${orderId}`;

    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      setError(null);
      console.log(`WebSocket connected for Order #${orderId}`);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket event received:', data);

        setEvents((prev) => [
          {
            ...data,
            receivedAt: new Date().toLocaleTimeString(),
          },
          ...prev,
        ]);

        if (data.status) {
          setCurrentStatus(data.status);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
      setError('Live connection error');
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log(`WebSocket disconnected for Order #${orderId}`);
    };

    // Heartbeat ping interval to keep connection alive
    const pingInterval = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send('ping');
      }
    }, 25000);

    return () => {
      clearInterval(pingInterval);
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close();
      }
    };
  }, [orderId]);

  return {
    currentStatus,
    events,
    isConnected,
    error,
  };
};
