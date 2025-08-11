import React, { useEffect, useState } from 'react';
import { Container, Typography, Grid, Card, CardContent, MenuItem, Select, FormControl, InputLabel, Stack } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useWebSocket } from '../contexts/WebSocketContext';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const [data, setData] = useState<any>(null);
  const [priceSeries, setPriceSeries] = useState<Array<{ time: string; price: number }>>([]);
  const [timeframe, setTimeframe] = useState<'M1' | 'M5' | 'M15' | 'M30' | 'H1' | 'H4' | 'D1'>('M15');
  const { lastTick } = useWebSocket();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${apiBase}/dashboard/`, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (e) {
        // noop
      }
    };
    fetchData();
  }, []);

  const loadPrice = async (tf: string) => {
    try {
      const res = await fetch(`${apiBase}/dashboard/price?symbol=XAUUSD&timeframe=${tf}&count=200`, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
      if (res.ok) {
        const json = await res.json();
        const series = (json.candles || []).map((c: any) => ({ time: c.time, price: c.close }));
        setPriceSeries(series);
      }
    } catch {}
  };

  useEffect(() => {
    const fetchPrice = async () => {
      await loadPrice(timeframe);
    };
    fetchPrice();
  }, [timeframe]);

  useEffect(() => {
    if (lastTick?.time && typeof lastTick.ask === 'number') {
      setPriceSeries(prev => {
        const next = [...prev, { time: lastTick.time!, price: lastTick.ask! }];
        // keep last 300 points
        return next.slice(Math.max(0, next.length - 300));
      });
    }
  }, [lastTick]);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        {t('dashboard.title')}
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Account Balance</Typography>
              <Typography variant="h4" color="primary">${data?.account_balance?.toFixed?.(2) || '0.00'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Trading Status</Typography>
              <Typography variant="h4" color="success.main">{data ? 'Online' : 'Offline'}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                <Typography variant="h6">Live XAUUSD Price</Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel id="tf-label">Timeframe</InputLabel>
                  <Select labelId="tf-label" label="Timeframe" value={timeframe} onChange={(e) => setTimeframe(e.target.value as any)}>
                    <MenuItem value="M1">M1</MenuItem>
                    <MenuItem value="M5">M5</MenuItem>
                    <MenuItem value="M15">M15</MenuItem>
                    <MenuItem value="M30">M30</MenuItem>
                    <MenuItem value="H1">H1</MenuItem>
                    <MenuItem value="H4">H4</MenuItem>
                    <MenuItem value="D1">D1</MenuItem>
                  </Select>
                </FormControl>
              </Stack>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={priceSeries} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" hide tick={false} />
                  <YAxis domain={['auto', 'auto']} />
                  <Tooltip formatter={(v: number) => v.toFixed(2)} labelFormatter={(label) => new Date(label).toLocaleString()} />
                  <Line type="monotone" dataKey="price" stroke="#1976d2" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6">Recent Trades</Typography>
              <Typography>No recent trades</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;