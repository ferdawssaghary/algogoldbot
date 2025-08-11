import React, { createContext, useContext, useEffect, useRef, useState } from 'react';

interface TickPayload {
  symbol?: string | null;
  bid?: number | null;
  ask?: number | null;
  time?: string | null;
}

interface WebSocketContextType {
  connected: boolean;
  lastTick: TickPayload | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [connected, setConnected] = useState(false);
  const [lastTick, setLastTick] = useState<TickPayload | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const userId = 1; // replace with real user id when auth is wired
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/${userId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data?.type === 'account_status' && data?.tick) {
          setLastTick({
            symbol: data.tick.symbol ?? undefined,
            bid: data.tick.bid ?? undefined,
            ask: data.tick.ask ?? undefined,
            time: data.tick.time ?? undefined,
          });
        }
      } catch {
        // ignore non-JSON
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const value = { connected, lastTick };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};