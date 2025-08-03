# MetaTrader 5 Setup Guide

## Overview

The Gold Trading Bot uses MetaTrader 5 (MT5) for trading operations. The MT5 Python package is not available on PyPI and requires manual installation.

## Development Mode (Default)

The application runs in **mock mode** by default, which means:
- No real trading occurs
- Mock data is provided for testing
- All MT5 functions return realistic but simulated data
- Perfect for development and testing

## Production Setup

To use real MT5 trading in production, follow these steps:

### 1. Install MetaTrader 5 Terminal

Download and install MetaTrader 5 terminal from the official website:
- **Windows**: https://www.metatrader5.com/en/download
- **Linux**: Use Wine to run the Windows version

### 2. Install MT5 Python Package

The MetaTrader5 Python package is not available on PyPI. You need to:

1. Download the package from MetaQuotes:
   ```
   wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
   ```

2. Extract the Python package from the installer or download it separately

3. Install manually:
   ```bash
   pip install MetaTrader5-5.0.45.0.tar.gz
   ```

### 3. Configure MT5 Settings

In your environment variables or `.env` file:

```env
MT5_SERVER=your_broker_server
MT5_PATH=/path/to/mt5/terminal.exe
MT5_TIMEOUT=60000
```

### 4. Docker Setup (Optional)

If running in Docker, you'll need to:

1. Mount the MT5 terminal directory
2. Install Wine for Linux containers
3. Configure display for GUI applications

Example Dockerfile addition:
```dockerfile
# Install Wine for MT5
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y wine32 && \
    rm -rf /var/lib/apt/lists/*

# Copy MT5 terminal
COPY mt5_terminal/ /opt/mt5/
```

## Mock Mode Features

When MT5 is not available, the service provides:

- **Mock Account Info**: Simulated account balance, equity, margin
- **Mock Market Data**: Realistic price data for XAUUSD
- **Mock Order Placement**: Simulated order execution
- **Mock Position Management**: Simulated position tracking
- **Mock Trade History**: Empty trade history
- **Mock Price Data**: Generated historical price data

## Testing

The mock mode allows you to:
- Test the trading bot logic
- Develop the frontend interface
- Test order management
- Validate trading algorithms
- Debug without real money

## Production Deployment

For production deployment:

1. **Install MT5 Terminal**: Set up MT5 terminal on your server
2. **Install Python Package**: Manually install the MT5 Python package
3. **Configure Broker**: Set up your broker credentials
4. **Test Connection**: Verify MT5 connection works
5. **Deploy**: Deploy with real MT5 integration

## Troubleshooting

### Common Issues

1. **MT5 not initializing**: Check if MT5 terminal is running
2. **Connection failed**: Verify broker credentials and server
3. **Package not found**: Ensure MT5 Python package is installed
4. **Permission errors**: Check file permissions for MT5 terminal

### Logs

Check the application logs for MT5-related messages:
- `MT5 initialized successfully` - Real MT5 mode
- `MetaTrader5 package not available. Running in mock mode.` - Mock mode
- `Error initializing MT5` - MT5 initialization failed

## Security Notes

- Never commit real MT5 credentials to version control
- Use environment variables for sensitive data
- Encrypt passwords using the built-in encryption
- Test thoroughly in mock mode before live trading