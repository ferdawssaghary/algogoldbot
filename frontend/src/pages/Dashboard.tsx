import React, { useEffect, useRef, useState } from 'react';
import { Container, Typography, Grid, Card, CardContent, MenuItem, Select, FormControl, InputLabel, Stack, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';
import { createChart, IChartApi, Time } from 'lightweight-charts';
import { useWebSocket } from '../contexts/WebSocketContext';
import { toast } from 'react-toastify';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const [data, setData] = useState<any>(null);
  const [candles, setCandles] = useState<Array<{ time: Time; open: number; high: number; low: number; close: number }>>([]);
  const [timeframe, setTimeframe] = useState<'M1' | 'M5' | 'M15' | 'M30' | 'H1' | 'H4' | 'D1'>('M15');
  const { lastTick, accountInfo } = useWebSocket();
  const [recentTrades, setRecentTrades] = useState<any[]>([]);
  const chartRef = useRef<HTMLDivElement | null>(null);
  const chartApiRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${apiBase}/dashboard/`, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
        const tr = await fetch(`${apiBase}/dashboard/recent-trades`, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
        if (tr.ok) {
          const tjson = await tr.json();
          setRecentTrades(tjson.trades || []);
        }
      } catch (e: any) {
        toast.error(e.message || 'Failed to load dashboard');
      }
    };
    fetchData();
  }, []);

  const loadPrice = async (tf: string) => {
    try {
      const res = await fetch(`${apiBase}/dashboard/price?symbol=XAUUSD&timeframe=${tf}&count=200`, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
      if (res.ok) {
        const json = await res.json();
        const mapped = (json.candles || []).map((c: any) => ({ time: (new Date(c.time).getTime() / 1000) as Time, open: c.open, high: c.high, low: c.low, close: c.close }));
        setCandles(mapped);
        if (seriesRef.current) {
          seriesRef.current.setData(mapped);
        }
      }
    } catch {}
  };

  useEffect(() => {
    const fetchPrice = async () => {
      await loadPrice(timeframe);
    };
    fetchPrice().catch(() => toast.error('Failed to load price data'));
  }, [timeframe]);

  const tfToSeconds = (tf: string) => {
    switch (tf) {
      case 'M1': return 60;
      case 'M5': return 300;
      case 'M15': return 900;
      case 'M30': return 1800;
      case 'H1': return 3600;
      case 'H4': return 14400;
      case 'D1': return 86400;
      default: return 900;
    }
  };

  useEffect(() => {
    if (lastTick?.time && typeof lastTick.ask === 'number' && seriesRef.current) {
      const tSec = Math.floor(new Date(lastTick.time).getTime() / 1000);
      const bucket = Math.floor(tSec / tfToSeconds(timeframe)) * tfToSeconds(timeframe);
      const last = candles[candles.length - 1];
      if (!last || (last.time as number) < bucket) {
        const c = { time: bucket as Time, open: lastTick.ask, high: lastTick.ask, low: lastTick.ask, close: lastTick.ask };
        setCandles(prev => [...prev, c]);
        seriesRef.current.update(c);
      } else {
        const updated = { ...last, high: Math.max(last.high, lastTick.ask), low: Math.min(last.low, lastTick.ask), close: lastTick.ask };
        setCandles(prev => [...prev.slice(0, -1), updated]);
        seriesRef.current.update(updated);
      }
    }
  }, [lastTick, timeframe, candles]);

  useEffect(() => {
    if (!chartRef.current) return;
    const chart = createChart(chartRef.current, { height: 300, layout: { background: { color: '#ffffff' }, textColor: '#333' }, grid: { vertLines: { color: '#eee' }, horzLines: { color: '#eee' } } });
    chartApiRef.current = chart;
    const candleSeries = chart.addCandlestickSeries();
    seriesRef.current = candleSeries;
    if (candles.length) candleSeries.setData(candles);
    const handleResize = () => chart.applyOptions({ width: chartRef.current?.clientWidth || 600 });
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

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
              <Typography variant="h4" color="primary">
                ${accountInfo?.balance?.toFixed(2) || data?.account_balance?.toFixed(2) || '0.00'}
              </Typography>
              {accountInfo?.equity && (
                <Typography variant="body2" color="text.secondary">
                  Equity: ${accountInfo.equity.toFixed(2)} | Profit: ${accountInfo.profit?.toFixed(2) || '0.00'}
                </Typography>
              )}
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
              <div ref={chartRef} style={{ width: '100%', height: 300 }} />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6">Recent Trades</Typography>
              {recentTrades.length === 0 ? (
                <Typography>No recent trades</Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Time</TableCell>
                      <TableCell>Ticket</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">Volume</TableCell>
                      <TableCell align="right">P/L</TableCell>
                      <TableCell>Comment</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentTrades.map((r, idx) => (
                      <TableRow key={idx}>
                        <TableCell>{new Date(r.time).toLocaleString()}</TableCell>
                        <TableCell>{r.ticket}</TableCell>
                        <TableCell>{r.type}</TableCell>
                        <TableCell align="right">{Number(r.price).toFixed(2)}</TableCell>
                        <TableCell align="right">{Number(r.volume).toFixed(2)}</TableCell>
                        <TableCell align="right" style={{ color: Number(r.profit) >= 0 ? '#2e7d32' : '#d32f2f' }}>{Number(r.profit).toFixed(2)}</TableCell>
                        <TableCell>{r.comment}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;