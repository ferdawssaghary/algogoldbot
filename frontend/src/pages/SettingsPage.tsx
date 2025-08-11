import React, { useEffect, useState } from 'react';
import { Container, Typography, TextField, Button, Stack, Paper, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
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
  const [timeframe, setTimeframe] = useState<'M1'|'M5'|'M15'|'M30'|'H1'|'H4'|'D1'>('M15');
  const [enabled, setEnabled] = useState(true);
  const [customTickValue, setCustomTickValue] = useState<number | ''>('' as any);
  const [customPoint, setCustomPoint] = useState<number | ''>('' as any);

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
        setTimeframe(j.timeframe || 'M15');
        setEnabled(j.enable_strategy ?? true);
        setCustomTickValue(j.custom_tick_value ?? '');
        setCustomPoint(j.custom_point ?? '');
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
        body: JSON.stringify({ risk_percentage: risk, max_daily_trades: maxDaily, stop_loss_pips: sl, take_profit_pips: tp, max_spread: maxSpread, timeframe, enable_strategy: enabled, custom_tick_value: customTickValue === '' ? null : Number(customTickValue), custom_point: customPoint === '' ? null : Number(customPoint) })
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
          <FormControl>
            <InputLabel id="tf-select-label">Timeframe</InputLabel>
            <Select labelId="tf-select-label" label="Timeframe" value={timeframe} onChange={e => setTimeframe(e.target.value as any)}>
              {['M1','M5','M15','M30','H1','H4','D1'].map(tf => <MenuItem key={tf} value={tf}>{tf}</MenuItem>)}
            </Select>
          </FormControl>
          <Stack direction="row" spacing={2}>
            <Button variant="outlined" onClick={() => setEnabled(e => !e)}>{enabled ? 'Disable Strategy' : 'Enable Strategy'}</Button>
          </Stack>
          <Typography variant="subtitle1">Broker Calibration (optional)</Typography>
          <TextField label="Custom Tick Value" type="number" value={customTickValue} onChange={e => setCustomTickValue(e.target.value === '' ? '' : Number(e.target.value))} />
          <TextField label="Custom Point Size" type="number" value={customPoint} onChange={e => setCustomPoint(e.target.value === '' ? '' : Number(e.target.value))} />
          <Stack direction="row" spacing={2}>
            <Button variant="contained" onClick={save} disabled={saving}>Save</Button>
          </Stack>
        </Stack>
      </Paper>
    </Container>
  );
};

export default SettingsPage;