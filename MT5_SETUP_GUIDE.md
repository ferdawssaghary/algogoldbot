# MT5 Trading Interface Setup Guide

## Issues Fixed

1. ✅ **WebSocket Connection Error** - Fixed connection to use MT5-specific endpoint
2. ✅ **Fake Balance Display** - Updated to show real account balance
3. ✅ **No Real Trading** - Implemented real order placement through WebSocket
4. ✅ **Fake Chart Data** - Connected to real MT5 price feeds

## Step 1: Configure Your MT5 Credentials

### Option A: Using Environment Variables

1. Edit the `backend/.env` file:
```bash
# Replace with your actual MT5 account credentials
MT5_LOGIN=your_mt5_login_here
MT5_PASSWORD=your_mt5_password_here
MT5_SERVER=your_mt5_server_here

# Example for LiteFinance:
# MT5_LOGIN=12345678
# MT5_PASSWORD=your_password
# MT5_SERVER=LiteFinance-Demo
```

### Option B: Using Docker Environment Variables

If you're using Docker, add these to your `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - MT5_LOGIN=your_mt5_login_here
      - MT5_PASSWORD=your_mt5_password_here
      - MT5_SERVER=your_mt5_server_here
```

## Step 2: Install MetaTrader 5 Python Package

The system needs the MetaTrader5 Python package to connect to your real account.

### For Ubuntu/Debian:
```bash
# Download MT5 package (you need to get this from MetaQuotes)
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
# Or download manually from: https://www.metatrader5.com/en/download

# Install the Python package
pip install MetaTrader5-5.0.45.0.tar.gz
```

### For Docker:
Add this to your Dockerfile:
```dockerfile
# Install MT5 Python package
RUN pip install MetaTrader5-5.0.45.0.tar.gz
```

## Step 3: Restart the Services

```bash
# Stop the current services
docker-compose down

# Start with new configuration
docker-compose up -d
```

## Step 4: Verify Connection

1. Open your browser and go to `http://localhost:3000`
2. Navigate to the Trading page
3. Check the "Connection Status" - it should show "Connected"
4. The "Account Balance" should show your real balance (e.g., $500.00)
5. The "Current Price" should show real XAUUSD prices

## Step 5: Test Real Trading

1. On the Trading page, you should see:
   - Connection Status: Connected
   - Account Balance: Your real balance
   - Current Price: Real XAUUSD price

2. To place a test order:
   - Set Lot Size (e.g., 0.01)
   - Set SL (Stop Loss) in pips (e.g., 50)
   - Set TP (Take Profit) in pips (e.g., 100)
   - Click BUY or SELL

3. Check your MT5 terminal to see if the order appears

## Troubleshooting

### If you still see $10,000 balance:
- Check that MT5_LOGIN and MT5_PASSWORD are set correctly
- Verify that the MetaTrader5 Python package is installed
- Check the backend logs: `docker-compose logs backend`

### If WebSocket connection fails:
- Verify the secret key matches: `g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD`
- Check that the backend is running on port 8000
- Check browser console for connection errors

### If orders don't appear in MT5:
- Verify your MT5 credentials are correct
- Check that your MT5 terminal is running
- Ensure you have sufficient margin for the order size

## Common MT5 Server Names

- **LiteFinance**: `LiteFinance-Demo` (demo) or `LiteFinance-Live` (live)
- **IC Markets**: `ICMarkets-Demo` or `ICMarkets-Live`
- **Pepperstone**: `Pepperstone-Demo` or `Pepperstone-Live`
- **FXTM**: `FXTM-Demo` or `FXTM-Live`

## Security Notes

- Never commit your real MT5 credentials to version control
- Use environment variables or secure configuration management
- Consider using a demo account for testing
- The secret key in the WebSocket URL should be changed in production

## Next Steps

Once everything is working:
1. Test with small lot sizes first
2. Verify all orders appear in your MT5 terminal
3. Check that the chart shows real-time prices
4. Monitor the trading logs for any issues

## Support

If you encounter issues:
1. Check the backend logs: `docker-compose logs backend`
2. Check the frontend console for JavaScript errors
3. Verify your MT5 terminal is running and connected
4. Ensure your account has sufficient margin for trading