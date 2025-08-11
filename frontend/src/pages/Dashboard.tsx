import React, { useEffect, useState } from 'react';
import { Container, Typography, Grid, Card, CardContent } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const [data, setData] = useState<any>(null);

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