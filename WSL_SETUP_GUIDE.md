# WSL Setup Guide for MT5 Trading Interface

## Prerequisites

### 1. Windows Requirements
- **Docker Desktop for Windows** installed and running
- **WSL 2** enabled and configured
- **Windows 10/11** with latest updates

### 2. WSL Requirements
- **Ubuntu** or **Debian** distribution
- **Git** installed
- **Docker CLI** (will be available when Docker Desktop is running)

## Setup Steps

### Step 1: Start Docker Desktop on Windows
1. Open **Docker Desktop** on Windows
2. Wait for it to fully start (green icon in system tray)
3. Go to **Settings** → **Resources** → **WSL Integration**
4. **Enable** WSL integration for your Ubuntu distribution
5. Click **Apply & Restart**

### Step 2: Verify Docker in WSL
```bash
# In your WSL terminal
docker --version
docker ps
```

If you see "permission denied" errors, Docker Desktop isn't running or WSL integration isn't enabled.

### Step 3: Configure MT5 Credentials
```bash
# Edit the .env file with your real MT5 credentials
cd backend
nano .env
```

Replace the placeholder values:
```bash
MT5_LOGIN=your_actual_login_number
MT5_PASSWORD=your_actual_password
MT5_SERVER=your_broker_server_name
```

### Step 4: Start Services
```bash
# Use the provided startup script
./start_services.sh
```

Or manually:
```bash
# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps
```

### Step 5: Verify Services
```bash
# Check if services are running
curl http://localhost:8000/health
curl http://localhost:3000
```

## Troubleshooting

### Docker Connection Issues
**Problem**: `permission denied while trying to connect to the Docker daemon`

**Solution**:
1. Make sure Docker Desktop is running on Windows
2. Enable WSL integration in Docker Desktop settings
3. Restart your WSL terminal
4. Try `docker ps` again

### Port Access Issues
**Problem**: Can't access localhost:3000 or localhost:8000

**Solution**:
1. Check if containers are running: `docker-compose ps`
2. Check container logs: `docker-compose logs backend`
3. Make sure no other services are using these ports
4. Try accessing from Windows browser: `http://localhost:3000`

### WebSocket Connection Errors
**Problem**: `WebSocket connection to 'ws://localhost:8000/ws/mt5' failed`

**Solution**:
1. Ensure backend is running: `docker-compose logs backend`
2. Check if MT5 credentials are configured in `.env`
3. Verify the secret key matches in the code
4. Check browser console for detailed error messages

### MT5 Connection Issues
**Problem**: Still showing $10,000 balance instead of real balance

**Solution**:
1. Verify MT5 credentials in `backend/.env`
2. Check backend logs: `docker-compose logs backend`
3. Make sure MetaTrader5 Python package is available
4. Restart services: `docker-compose restart backend`

## Common Commands

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

### Development
```bash
# Rebuild containers
docker-compose up --build -d

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend bash

# Check container status
docker-compose ps
```

### Database
```bash
# Access database
docker-compose exec postgres psql -U goldtrader -d gold_trading_bot

# Reset database
docker-compose down -v
docker-compose up -d
```

## Testing the Interface

### 1. Frontend Access
- Open browser: `http://localhost:3000`
- Navigate to Trading page
- Check connection status

### 2. Backend API
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/api/docs`

### 3. WebSocket Test
```bash
# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
     http://localhost:8000/ws/mt5?secret=g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD
```

## Expected Results

### ✅ Working Interface Should Show:
- **Connection Status**: "Connected"
- **Account Balance**: Your real balance (e.g., $500.00)
- **Current Price**: Real XAUUSD prices
- **BUY/SELL buttons**: Enabled and functional

### ❌ Common Issues:
- Connection Status: "Disconnected"
- Account Balance: $10,000 (mock data)
- WebSocket errors in browser console
- Orders not appearing in MT5 terminal

## Support

If you encounter issues:
1. Check Docker Desktop is running on Windows
2. Verify WSL integration is enabled
3. Check service logs: `docker-compose logs`
4. Ensure MT5 credentials are correct
5. Restart services: `docker-compose restart`

## Next Steps

Once everything is working:
1. Test with small lot sizes (0.01)
2. Verify orders appear in your MT5 terminal
3. Monitor the trading logs
4. Configure additional settings as needed