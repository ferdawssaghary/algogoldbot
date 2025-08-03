// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Auth endpoints
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  
  // Trading endpoints
  TRADING_STATUS: `${API_BASE_URL}/api/trading/status`,
  START_TRADING: `${API_BASE_URL}/api/trading/start`,
  STOP_TRADING: `${API_BASE_URL}/api/trading/stop`,
  
  // Dashboard endpoints
  DASHBOARD_DATA: `${API_BASE_URL}/api/dashboard`,
  PERFORMANCE_DATA: `${API_BASE_URL}/api/performance`,
  
  // MT5 endpoints
  MT5_CONFIG: `${API_BASE_URL}/api/mt5/config`,
  MT5_CONNECT: `${API_BASE_URL}/api/mt5/connect`,
  
  // WebSocket endpoint
  WEBSOCKET: `${API_BASE_URL.replace('http', 'ws')}/ws`,
};

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

export default API_CONFIG;