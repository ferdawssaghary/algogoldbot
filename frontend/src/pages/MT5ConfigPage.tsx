import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Stack, Paper } from '@mui/material';
import { toast } from 'react-toastify';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const MT5ConfigPage: React.FC = () => {
  const [server, setServer] = useState('LiteFinance-MT5-Demo');
  const [login, setLogin] = useState('90650537');
  const [password, setPassword] = useState('aaBB@123');
  const [botToken, setBotToken] = useState('');
  const [chatId, setChatId] = useState('');
  const [saving, setSaving] = useState(false);

  const saveMt5 = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${apiBase}/mt5/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ account_login: login, account_password: password, server_name: server })
      });
      if (!res.ok) throw new Error('Failed to save MT5 config');
      toast.success('MT5 configuration saved');
    } catch (e: any) {
      toast.error(e.message || 'MT5 save failed');
    } finally {
      setSaving(false);
    }
  };

  const connectMt5 = async () => {
    try {
      const r = await fetch(`${apiBase}/mt5/connect`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
      if (!r.ok) throw new Error('Failed to connect MT5');
      toast.success('MT5 connected');
    } catch (e: any) {
      toast.error(e.message || 'MT5 connect failed');
    }
  };

  const saveTelegram = async () => {
    try {
      const r = await fetch(`${apiBase}/telegram/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ bot_token: botToken, chat_id: chatId })
      });
      if (!r.ok) throw new Error('Failed to save Telegram settings');
      toast.success('Telegram settings saved');
    } catch (e: any) {
      toast.error(e.message || 'Telegram save failed');
    }
  };

  const testTelegram = async () => {
    try {
      const r = await fetch(`${apiBase}/telegram/test`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
      if (!r.ok) throw new Error('Failed to send test');
      toast.success('Test signal sent');
    } catch (e: any) {
      toast.error(e.message || 'Test signal failed');
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Configuration</Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>MT5 Credentials</Typography>
        <Stack spacing={2} direction="column">
          <TextField label="Server" value={server} onChange={e => setServer(e.target.value)} />
          <TextField label="Account Login" value={login} onChange={e => setLogin(e.target.value)} />
          <TextField label="Account Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          <Stack direction="row" spacing={2}>
            <Button variant="contained" onClick={saveMt5} disabled={saving}>Save</Button>
            <Button variant="outlined" onClick={connectMt5}>Connect</Button>
          </Stack>
        </Stack>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Telegram</Typography>
        <Stack spacing={2} direction="column">
          <TextField label="Bot Token" value={botToken} onChange={e => setBotToken(e.target.value)} />
          <TextField label="Chat ID" value={chatId} onChange={e => setChatId(e.target.value)} />
          <Stack direction="row" spacing={2}>
            <Button variant="contained" onClick={saveTelegram}>Save</Button>
            <Button variant="outlined" onClick={testTelegram}>Send Test Signal</Button>
          </Stack>
        </Stack>
      </Paper>
    </Container>
  );
};

export default MT5ConfigPage;