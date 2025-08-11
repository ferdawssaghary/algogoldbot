import React from 'react';
import { Outlet, Link as RouterLink } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Button, Stack } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

const Layout: React.FC = () => {
  const { logout } = useAuth();
  const { t, language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'fa' : 'en');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {t('app.title')}
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mr: 2 }}>
            <Button color="inherit" component={RouterLink} to="/dashboard">Dashboard</Button>
            <Button color="inherit" component={RouterLink} to="/trading">Trading</Button>
            <Button color="inherit" component={RouterLink} to="/mt5-config">MT5 Config</Button>
            <Button color="inherit" component={RouterLink} to="/settings">Settings</Button>
          </Stack>
          <Button color="inherit" onClick={toggleLanguage}>
            {language === 'en' ? 'فارسی' : 'English'}
          </Button>
          <Button color="inherit" onClick={logout}>
            {t('nav.logout')}
          </Button>
        </Toolbar>
      </AppBar>
      
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;