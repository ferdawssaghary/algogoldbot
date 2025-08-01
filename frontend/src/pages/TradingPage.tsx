import React from 'react';
import { Container, Typography } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const TradingPage: React.FC = () => {
  const { t } = useLanguage();

  return (
    <Container>
      <Typography variant="h4">{t('trading.title')}</Typography>
      <Typography>Trading interface coming soon...</Typography>
    </Container>
  );
};

export default TradingPage;