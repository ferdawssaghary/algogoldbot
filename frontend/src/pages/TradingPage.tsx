import React, { useState, useRef } from 'react';
import { Container, Typography, Button, Stack, TextField, Paper, Grid, Card, CardContent } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';
import { useWebSocket } from '../contexts/WebSocketContext';
import { toast } from 'react-toastify';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const TradingPage: React.FC = () => {
  const { t } = useLanguage();
  const { connected, lastTick, accountInfo } = useWebSocket();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [lot, setLot] = useState(0.01);
  const [sl, setSl] = useState(50);
  const [tp, setTp] = useState(100);

  const startTrading = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/trading/start`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
      const json = await res.json().catch(() => ({}));
      setStatus(json?.message || 'Started');
      toast.success('Trading started');
    } catch (e: any) {
      toast.error(e.message || 'Failed to start');
    } finally {
      setLoading(false);
    }
  };

  const stopTrading = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/trading/stop`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
      const json = await res.json().catch(() => ({}));
      setStatus(json?.message || 'Stopped');
      toast.success('Trading stopped');
    } catch (e: any) {
      toast.error(e.message || 'Failed to stop');
    } finally {
      setLoading(false);
    }
  };

  const testOrder = async (side: 'BUY' | 'SELL') => {
    if (!connected) {
      toast.error('WebSocket not connected');
      return;
    }
    
    setLoading(true);
    
    // Calculate SL and TP based on current price
    const currentPrice = lastTick?.ask || 2000; // fallback price
    const slPrice = side === 'BUY' ? currentPrice - (sl * 0.1) : currentPrice + (sl * 0.1);
    const tpPrice = side === 'BUY' ? currentPrice + (tp * 0.1) : currentPrice - (tp * 0.1);
    
    const orderMessage = {
      type: 'place_order',
      symbol: 'XAUUSD',
      order_type: side,
      volume: lot,
      price: currentPrice,
      sl: slPrice,
      tp: tpPrice,
      comment: `Manual ${side} order`
    };
    
    // Send order through the WebSocket context
    // Note: We need to access the WebSocket instance from the context
    // For now, we'll use a simple approach by making a direct API call
    try {
      const response = await fetch('/api/trading/place-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeader()
        },
        body: JSON.stringify({
          symbol: 'XAUUSD',
          order_type: side,
          volume: lot,
          price: currentPrice,
          sl: slPrice,
          tp: tpPrice,
          comment: `Manual ${side} order`
        })
      });
      
      const result = await response.json();
      if (result.success) {
        toast.success(`Order placed successfully! Ticket: ${result.ticket}`);
      } else {
        toast.error(`Order failed: ${result.message}`);
      }
    } catch (error) {
      toast.error('Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Trading Control</Typography>
      
      {/* Connection Status */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Connection Status</Typography>
              <Typography variant="h4" color={connected ? 'success.main' : 'error.main'}>
                {connected ? 'Connected' : 'Disconnected'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Account Balance</Typography>
              <Typography variant="h4" color="primary">
                ${accountInfo?.balance?.toFixed(2) || '0.00'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Current Price (XAUUSD)</Typography>
              <Typography variant="h4" color="primary">
                ${lastTick?.ask?.toFixed(2) || '0.00'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Bid: ${lastTick?.bid?.toFixed(2) || '0.00'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <Button variant="contained" onClick={startTrading} disabled={loading}>Start Trading</Button>
        <Button variant="outlined" color="error" onClick={stopTrading} disabled={loading}>Stop Trading</Button>
      </Stack>
      {status && (
        <Typography sx={{ mb: 2 }} color="text.secondary">{status}</Typography>
      )}

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>Instant Test Order (XAUUSD)</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <TextField label="Lot Size" type="number" value={lot} onChange={e => setLot(Number(e.target.value))} />
          <TextField label="SL (pips)" type="number" value={sl} onChange={e => setSl(Number(e.target.value))} />
          <TextField label="TP (pips)" type="number" value={tp} onChange={e => setTp(Number(e.target.value))} />
          <Button 
            variant="contained" 
            color="success" 
            onClick={() => testOrder('BUY')} 
            disabled={loading || !connected}
          >
            BUY
          </Button>
          <Button 
            variant="contained" 
            color="error" 
            onClick={() => testOrder('SELL')} 
            disabled={loading || !connected}
          >
            SELL
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
};

export default TradingPage;