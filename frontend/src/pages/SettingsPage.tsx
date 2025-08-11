import React, { useEffect, useState } from 'react';
import { Container, Typography, TextField, Button, Stack, Paper } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const SettingsPage: React.FC = () => {
  const { t } = useLanguage();
  const [risk, setRisk] = useState(2);
  const [maxDaily, setMaxDaily] = useState(10);
  const [sl, setSl] = useState(50);
  const [tp, setTp] = useState(100);
  const [maxSpread, setMaxSpread] = useState(5);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`${apiBase}/trading/settings`, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
      if (res.ok) {
        const j = await res.json();
        setRisk(j.risk_percentage);
        setMaxDaily(j.max_daily_trades);
        setSl(j.stop_loss_pips);
        setTp(j.take_profit_pips);
        setMaxSpread(j.max_spread ?? 5);
      }
    };
    load();
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await fetch(`${apiBase}/trading/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ risk_percentage: risk, max_daily_trades: maxDaily, stop_loss_pips: sl, take_profit_pips: tp, max_spread: maxSpread })
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>{t('settings.title')}</Typography>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Risk Settings</Typography>
        <Stack spacing={2}>
          <TextField label="Risk % per Trade" type="number" value={risk} onChange={e => setRisk(Number(e.target.value))} />
          <TextField label="Max Daily Trades" type="number" value={maxDaily} onChange={e => setMaxDaily(Number(e.target.value))} />
          <TextField label="Stop Loss (pips)" type="number" value={sl} onChange={e => setSl(Number(e.target.value))} />
          <TextField label="Take Profit (pips)" type="number" value={tp} onChange={e => setTp(Number(e.target.value))} />
          <TextField label="Max Spread (pips)" type="number" value={maxSpread} onChange={e => setMaxSpread(Number(e.target.value))} />
          <Stack direction="row" spacing={2}>
            <Button variant="contained" onClick={save} disabled={saving}>Save</Button>
          </Stack>
        </Stack>
      </Paper>
    </Container>
  );
};

export default SettingsPage;