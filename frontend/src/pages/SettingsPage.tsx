import React from 'react';
import { Container, Typography } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const SettingsPage: React.FC = () => {
  const { t } = useLanguage();

  return (
    <Container>
      <Typography variant="h4">{t('settings.title')}</Typography>
      <Typography>Settings interface coming soon...</Typography>
    </Container>
  );
};

export default SettingsPage;