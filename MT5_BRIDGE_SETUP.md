# MT5 Bridge Setup Guide

## Overview

This guide explains how to set up the bridge architecture that allows MetaTrader 5 (running on Windows) to communicate with the trading bot backend (running in Docker/WSL).

## Architecture

```
Windows MT5 EA → signals.json → Docker/WSL Backend
```

The bridge works by having the MT5 Expert Advisor write trading data to a JSON file that is mounted into the Docker container.

## Setup Instructions

### 1. Windows MT5 Side

#### Create Bridge Directory
```cmd
mkdir C:\MT5Bridge
```

#### Configure EA Bridge Settings
In your MT5 EA (`GoldTradingBot.mq5`), set the bridge file path:
```mql5
// Add this line in your EA inputs or as a constant
string BridgeFilePath = "C:\\MT5Bridge\\signals.json";
```

#### EA Bridge Code (Add to your EA)
```mql5
void WriteBridgeFile()
{
    string json = StringFormat(
        "{\n"
        "  \"timestamp\": \"%s\",\n"
        "  \"account\": {\n"
        "    \"login\": \"%d\",\n"
        "    \"server\": \"%s\",\n"
        "    \"name\": \"%s\",\n"
        "    \"balance\": %.2f,\n"
        "    \"equity\": %.2f,\n"
        "    \"margin\": %.2f,\n"
        "    \"free_margin\": %.2f,\n"
        "    \"margin_level\": %.2f,\n"
        "    \"profit\": %.2f,\n"
        "    \"currency\": \"%s\",\n"
        "    \"leverage\": %d\n"
        "  },\n"
        "  \"tick\": {\n"
        "    \"symbol\": \"%s\",\n"
        "    \"bid\": %.5f,\n"
        "    \"ask\": %.5f,\n"
        "    \"volume\": %d,\n"
        "    \"time\": \"%s\"\n"
        "  }\n"
        "}",
        TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
        AccountInfoInteger(ACCOUNT_LOGIN),
        AccountInfoString(ACCOUNT_SERVER),
        AccountInfoString(ACCOUNT_NAME),
        AccountInfoDouble(ACCOUNT_BALANCE),
        AccountInfoDouble(ACCOUNT_EQUITY),
        AccountInfoDouble(ACCOUNT_MARGIN),
        AccountInfoDouble(ACCOUNT_MARGIN_FREE),
        AccountInfoDouble(ACCOUNT_MARGIN_LEVEL),
        AccountInfoDouble(ACCOUNT_PROFIT),
        AccountInfoString(ACCOUNT_CURRENCY),
        (int)AccountInfoInteger(ACCOUNT_LEVERAGE),
        Symbol(),
        SymbolInfoDouble(Symbol(), SYMBOL_BID),
        SymbolInfoDouble(Symbol(), SYMBOL_ASK),
        0,
        TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS)
    );
    
    int file = FileOpen(BridgeFilePath, FILE_WRITE|FILE_TXT);
    if(file != INVALID_HANDLE)
    {
        FileWriteString(file, json);
        FileClose(file);
    }
}

// Call this function every second in OnTick() or OnTimer()
```

### 2. WSL/Docker Side

#### Update docker-compose.yml
```yaml
services:
  backend:
    # ... other config ...
    volumes:
      - /mnt/c/MT5Bridge:/app/mt5_data  # Mount Windows bridge directory
```

#### Verify Mount Path
From WSL, check if the bridge file is accessible:
```bash
ls -la /mnt/c/MT5Bridge/
cat /mnt/c/MT5Bridge/signals.json
```

### 3. Backend Configuration

The backend is already configured to:
- Check for `/app/mt5_data/signals.json`
- Consider MT5 "connected" if file exists and is fresh (< 30 seconds old)
- Return mock data if bridge is not available
- Handle missing/invalid data gracefully

#### Environment Variables
```bash
MT5_BRIDGE_FILE=/app/mt5_data/signals.json
MT5_BRIDGE_MAX_AGE_SECONDS=30
```

## Testing the Bridge

### 1. Test Bridge File Creation
From Windows, manually create the bridge file:
```json
{
  "timestamp": "2024-08-15T07:20:00.000Z",
  "account": {
    "login": "90650537",
    "balance": 10000.00,
    "equity": 10050.25,
    "currency": "USD"
  },
  "tick": {
    "symbol": "XAUUSD",
    "bid": 2385.45,
    "ask": 2386.25,
    "time": "2024-08-15T07:20:00.000Z"
  }
}
```

### 2. Verify Backend Detection
Check backend logs for:
```
INFO - MT5 bridge is active (signals.json is fresh)
```

### 3. Test API Endpoints
```bash
# Check account info
curl http://localhost:8000/api/status

# Check market data via WebSocket
# Connect to ws://localhost:8000/ws/1
```

## Troubleshooting

### Bridge File Not Found
1. Check Windows path: `C:\MT5Bridge\signals.json`
2. Check WSL mount: `/mnt/c/MT5Bridge/signals.json`
3. Check Docker mount: `/app/mt5_data/signals.json`

### Bridge File Stale
- File must be updated within 30 seconds
- EA should write to file every second
- Check file timestamps

### Permission Issues
```bash
# Fix permissions if needed
sudo chmod 644 /mnt/c/MT5Bridge/signals.json
```

### JSON Format Issues
- Validate JSON format
- Check for proper escaping
- Use JSON validator tools

## Sample Bridge Update Script

For testing without MT5, use the provided script:
```bash
./update_bridge_file.sh
```

## Production Considerations

1. **File Locking**: Ensure atomic writes from EA
2. **Error Handling**: Handle file corruption gracefully
3. **Monitoring**: Monitor bridge file freshness
4. **Backup**: Consider backup bridge files
5. **Security**: Restrict file access as needed

## EA Integration Checklist

- [ ] EA writes to correct bridge file path
- [ ] JSON format matches expected structure
- [ ] File updated every 1-2 seconds
- [ ] Proper error handling in EA
- [ ] Bridge file accessible from Docker
- [ ] Backend logs show successful connection
- [ ] API endpoints return real data
- [ ] WebSocket updates working

## Support

For issues with the bridge setup:
1. Check backend logs: `docker-compose logs backend`
2. Verify file permissions and paths
3. Test with manual JSON file creation
4. Use provided update script for testing