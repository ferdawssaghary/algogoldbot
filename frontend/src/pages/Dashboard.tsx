import React from 'react';
import { Container, Typography, Grid, Card, CardContent } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const Dashboard: React.FC = () => {
  const { t } = useLanguage();

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
              <Typography variant="h4" color="primary">$10,000.00</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Trading Status</Typography>
              <Typography variant="h4" color="success.main">Active</Typography>
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