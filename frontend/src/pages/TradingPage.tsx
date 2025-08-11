import React, { useState } from 'react';
import { Container, Typography, Button, Stack, TextField, Paper } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';
import { toast } from 'react-toastify';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const TradingPage: React.FC = () => {
  const { t } = useLanguage();
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
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/trading/test-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ side, lot_size: lot, sl_pips: sl, tp_pips: tp })
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.detail || 'Order failed');
      toast.success(`${side} order placed`);
    } catch (e: any) {
      toast.error(e.message || 'Order placement failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Trading Control</Typography>
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
          <Button variant="contained" color="success" onClick={() => testOrder('BUY')} disabled={loading}>BUY</Button>
          <Button variant="contained" color="error" onClick={() => testOrder('SELL')} disabled={loading}>SELL</Button>
        </Stack>
      </Paper>
    </Container>
  );
};

export default TradingPage;