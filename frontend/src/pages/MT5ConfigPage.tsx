import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Stack, Paper } from '@mui/material';

const apiBase = '/api';
const authHeader = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` });

const MT5ConfigPage: React.FC = () => {
  const [server, setServer] = useState('LiteFinance-Demo');
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [botToken, setBotToken] = useState('');
  const [chatId, setChatId] = useState('');
  const [saving, setSaving] = useState(false);

  const saveMt5 = async () => {
    setSaving(true);
    try {
      await fetch(`${apiBase}/mt5/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ account_login: login, account_password: password, server_name: server })
      });
    } finally {
      setSaving(false);
    }
  };

  const connectMt5 = async () => {
    await fetch(`${apiBase}/mt5/connect`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
  };

  const saveTelegram = async () => {
    await fetch(`${apiBase}/telegram/configure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ bot_token: botToken, chat_id: chatId })
    });
  };

  const testTelegram = async () => {
    await fetch(`${apiBase}/telegram/test`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeader() } });
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