import React, { useState } from 'react';
import { Container, Typography, Button, Stack } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const TradingPage: React.FC = () => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>('');

  const startTrading = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/trading/start`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
      const json = await res.json().catch(() => ({}));
      setStatus(json?.message || 'Started');
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Trading Control</Typography>
      <Stack direction="row" spacing={2}>
        <Button variant="contained" onClick={startTrading} disabled={loading}>Start Trading</Button>
        <Button variant="outlined" color="error" onClick={stopTrading} disabled={loading}>Stop Trading</Button>
      </Stack>
      {status && (
        <Typography sx={{ mt: 2 }} color="text.secondary">{status}</Typography>
      )}
    </Container>
  );
};

export default TradingPage;