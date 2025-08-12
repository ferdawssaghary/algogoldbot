import React, { createContext, useContext, useEffect, useRef, useState } from 'react';

interface TickPayload {
  symbol?: string | null;
  bid?: number | null;
  ask?: number | null;
  time?: string | null;
}

interface AccountInfo {
  balance?: number;
  equity?: number;
  profit?: number;
  currency?: string;
}

interface WebSocketContextType {
  connected: boolean;
  lastTick: TickPayload | null;
  accountInfo: AccountInfo | null;
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
  const [accountInfo, setAccountInfo] = useState<AccountInfo | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to MT5 WebSocket endpoint with secret
    const wsUrl = `ws://localhost:8000/ws/mt5?secret=g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to MT5 WebSocket');
      setConnected(true);
      
      // Request initial account balance
      ws.send(JSON.stringify({ type: 'get_balance' }));
      
      // Request initial tick data
      ws.send(JSON.stringify({ type: 'get_tick', symbol: 'XAUUSD' }));
    };
    
    ws.onclose = () => {
      console.log('Disconnected from MT5 WebSocket');
      setConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        console.log('Received MT5 data:', data);
        
        if (data?.type === 'account_status') {
          if (data?.tick) {
            setLastTick({
              symbol: data.tick.symbol ?? undefined,
              bid: data.tick.bid ?? undefined,
              ask: data.tick.ask ?? undefined,
              time: data.tick.time ?? undefined,
            });
          }
          
          if (data?.balance !== undefined) {
            setAccountInfo({
              balance: data.balance,
              equity: data.equity,
              profit: data.profit,
              currency: data.currency
            });
          }
        } else if (data?.type === 'order_result') {
          // Handle order results - could be used for notifications
          console.log('Order result received:', data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const value = { connected, lastTick, accountInfo };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};