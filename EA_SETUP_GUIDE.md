# Expert Advisor (EA) Setup Guide

## Overview

The updated Expert Advisor (EA) integrates with your WebSocket-based trading interface to provide real-time data exchange and remote control capabilities.

## Files

- **`GoldTradingBot.mq5`** - Original EA (basic version)
- **`GoldTradingBot_Updated.mq5`** - Updated EA with WebSocket integration

## Key Features

### ✅ **Real-time Data Exchange**
- Sends account balance, equity, and profit to web interface
- Provides live market data (bid/ask prices)
- Reports trade events (open/close orders)

### ✅ **Remote Control**
- Start/stop trading from web interface
- Update trading parameters remotely
- Monitor EA status in real-time

### ✅ **Enhanced Trading Logic**
- Trend following with RSI confirmation
- Risk management with daily trade limits
- Spread and slippage protection

## Setup Instructions

### Step 1: Install the EA

1. **Copy the EA file** to your MetaTrader 5 directory:
   ```
   C:\Users\[YourUsername]\AppData\Roaming\MetaQuotes\Terminal\[TerminalID]\MQL5\Experts\
   ```

2. **Compile the EA** in MetaEditor:
   - Open MetaEditor (F4 in MT5)
   - Open `GoldTradingBot_Updated.mq5`
   - Click "Compile" (F7)

### Step 2: Configure EA Parameters

#### **Trading Settings**
- **Lot Size**: 0.01 (recommended for testing)
- **Stop Loss**: 50 pips
- **Take Profit**: 100 pips
- **Max Spread**: 5.0 pips
- **Slippage**: 3 pips

#### **Risk Management**
- **Risk Percent**: 2.0% per trade
- **Max Daily Trades**: 10
- **Magic Number**: 12345 (unique identifier)

#### **WebSocket Settings**
- **Backend URL**: `http://localhost:8000`
- **Secret Key**: `g4dV6pG9qW2z8K1rY7tB3nM5xC0hL2sD`
- **Enable WebSocket**: `true`
- **Update Interval**: 1000ms

### Step 3: Enable Web Requests

1. **In MetaTrader 5**:
   - Go to **Tools** → **Options** → **Expert Advisors**
   - Check **"Allow WebRequest for listed URL"**
   - Add: `http://localhost:8000`

2. **Alternative method**:
   - Add this line to the EA code (after the input parameters):
   ```mql5
   #property tester_web_request "http://localhost:8000"
   ```

### Step 4: Attach EA to Chart

1. **Open XAUUSD chart** (H1 timeframe recommended)
2. **Drag the EA** from Navigator to the chart
3. **Configure parameters** in the popup dialog
4. **Click OK** to start

## How It Works

### **Data Flow**
```
MT5 EA → Backend API → WebSocket → Frontend Interface
```

### **Commands Flow**
```
Frontend Interface → WebSocket → Backend API → MT5 EA
```

### **Real-time Updates**
- **Account Info**: Sent every 1 second
- **Market Data**: Sent on every tick
- **Trade Events**: Sent when orders open/close

## Testing the Integration

### **1. Start Backend Services**
```bash
# In WSL terminal
./start_services.sh
```

### **2. Start EA**
- Attach EA to XAUUSD chart
- Check "AutoTrading" is enabled
- Verify EA shows "Trading enabled" in comments

### **3. Test Web Interface**
- Open `http://localhost:3000`
- Go to Trading page
- Check connection status shows "Connected"
- Verify account balance matches MT5

### **4. Test Remote Control**
- Click "Start Trading" / "Stop Trading" in web interface
- Check EA comments change accordingly
- Verify trading stops/starts as expected

## Troubleshooting

### **EA Not Connecting**
- Check backend is running: `curl http://localhost:8000/health`
- Verify WebRequest is enabled for `http://localhost:8000`
- Check EA logs in MetaTrader 5

### **No Data in Web Interface**
- Verify EA is attached to chart
- Check "AutoTrading" is enabled
- Look for connection messages in EA logs

### **Trading Not Working**
- Check "Allow live trading" is enabled
- Verify account has sufficient margin
- Check trading hours and spread limits

### **WebSocket Errors**
- Ensure backend services are running
- Check secret key matches in EA and backend
- Verify firewall allows localhost connections

## Advanced Configuration

### **Custom Trading Strategy**
You can modify the `AnalyzeMarket()` function to implement your own strategy:

```mql5
int AnalyzeMarket()
{
    // Your custom analysis logic here
    // Return: 1 for BUY, -1 for SELL, 0 for no signal
    
    // Example: Simple moving average crossover
    double ma_fast = iMA(_Symbol, PERIOD_H1, 12, 0, MODE_EMA, PRICE_CLOSE);
    double ma_slow = iMA(_Symbol, PERIOD_H1, 26, 0, MODE_EMA, PRICE_CLOSE);
    
    if(ma_fast > ma_slow)
        return 1;  // BUY signal
    else if(ma_fast < ma_slow)
        return -1; // SELL signal
    
    return 0; // No signal
}
```

### **Custom Risk Management**
Modify risk parameters in the EA:

```mql5
// Dynamic lot size based on account balance
double CalculateLotSize()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = balance * RiskPercent / 100;
    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double stop_loss_pips = StopLoss;
    
    return NormalizeDouble(risk_amount / (stop_loss_pips * tick_value), 2);
}
```

## Security Considerations

### **Secret Key**
- Change the default secret key in production
- Use environment variables for sensitive data
- Never commit real credentials to version control

### **Network Security**
- Use HTTPS in production
- Implement proper authentication
- Restrict access to localhost in development

### **Trading Safety**
- Start with small lot sizes
- Test thoroughly on demo account
- Monitor EA performance regularly

## Performance Optimization

### **Update Frequency**
- Reduce `UpdateInterval` for faster updates
- Increase for better performance
- Balance between responsiveness and resource usage

### **Memory Management**
- EA automatically manages indicator handles
- Clean up resources in `OnDeinit()`
- Monitor memory usage in MT5

## Support

### **Logs and Debugging**
- Check MT5 Expert tab for EA logs
- Use `Print()` statements for debugging
- Monitor backend logs: `docker-compose logs backend`

### **Common Issues**
1. **EA not starting**: Check compilation errors
2. **No trades**: Verify trading conditions and market hours
3. **Connection issues**: Check backend status and network

### **Getting Help**
- Check MT5 documentation
- Review EA logs for error messages
- Test with simple strategies first

## Next Steps

1. **Test thoroughly** on demo account
2. **Monitor performance** and adjust parameters
3. **Implement custom strategies** as needed
4. **Deploy to production** with proper security

The EA is now ready to work with your WebSocket-based trading interface! 🚀