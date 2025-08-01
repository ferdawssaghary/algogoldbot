//+------------------------------------------------------------------+
//|                                            GoldTradingBot.mq5    |
//|                        Copyright 2024, Gold Trading Bot Team    |
//|                                 https://goldtradingbot.com      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Gold Trading Bot Team"
#property link      "https://goldtradingbot.com"
#property version   "1.00"
#property description "Automated Gold (XAUUSD) Trading Expert Advisor"

//--- Input parameters
input group "=== Trading Settings ==="
input double   LotSize          = 0.01;     // Lot size
input int      StopLoss         = 50;       // Stop Loss in pips
input int      TakeProfit       = 100;      // Take Profit in pips
input double   MaxSpread        = 5.0;      // Maximum allowed spread
input int      Slippage         = 3;        // Maximum slippage in pips

input group "=== Risk Management ==="
input double   RiskPercent      = 2.0;      // Risk percentage per trade
input int      MaxDailyTrades   = 10;       // Maximum trades per day
input int      MagicNumber      = 12345;    // Magic number for trades

input group "=== Trading Hours ==="
input string   TradingStartTime = "00:00";  // Trading start time
input string   TradingEndTime   = "23:59";  // Trading end time

input group "=== Algorithm Settings ==="
input ENUM_TIMEFRAMES TimeFrame = PERIOD_H1; // Main timeframe
input int      FastMA           = 12;        // Fast Moving Average period
input int      SlowMA           = 26;        // Slow Moving Average period
input int      RSI_Period       = 14;       // RSI period
input double   RSI_Oversold     = 30;       // RSI oversold level
input double   RSI_Overbought   = 70;       // RSI overbought level

input group "=== WebSocket Settings ==="
input string   WebSocketURL     = "ws://localhost:8000/ws/mt5"; // WebSocket URL
input bool     EnableWebSocket  = true;     // Enable WebSocket communication

//--- Global variables
string symbol = "XAUUSD";
double point_value;
int daily_trades_count = 0;
datetime last_trade_date = 0;
int fast_ma_handle, slow_ma_handle, rsi_handle;
bool websocket_connected = false;

// WebSocket library functions (simplified for demo)
#include <Trade\Trade.mqh>
#include <Indicators\Indicators.mqh>

CTrade trade;
CPositionInfo position;
COrderInfo order;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Set symbol and point value
    point_value = SymbolInfoDouble(symbol, SYMBOL_POINT);
    
    // Initialize indicators
    fast_ma_handle = iMA(symbol, TimeFrame, FastMA, 0, MODE_EMA, PRICE_CLOSE);
    slow_ma_handle = iMA(symbol, TimeFrame, SlowMA, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle = iRSI(symbol, TimeFrame, RSI_Period, PRICE_CLOSE);
    
    if(fast_ma_handle == INVALID_HANDLE || slow_ma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE)
    {
        Print("Error creating indicators");
        return INIT_FAILED;
    }
    
    // Set trade parameters
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(symbol);
    trade.SetDeviationInPoints(Slippage);
    
    // Initialize WebSocket connection
    if(EnableWebSocket)
    {
        InitializeWebSocket();
    }
    
    Print("Gold Trading Bot initialized successfully");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Release indicator handles
    IndicatorRelease(fast_ma_handle);
    IndicatorRelease(slow_ma_handle);
    IndicatorRelease(rsi_handle);
    
    // Close WebSocket connection
    if(websocket_connected)
    {
        CloseWebSocket();
    }
    
    Print("Gold Trading Bot deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check if trading is allowed
    if(!IsTradeAllowed() || !IsMarketOpen() || !IsWithinTradingHours())
        return;
    
    // Check spread
    double spread = SymbolInfoInteger(symbol, SYMBOL_SPREAD) * point_value / point_value;
    if(spread > MaxSpread)
    {
        Comment("Spread too high: ", spread);
        return;
    }
    
    // Reset daily trade counter if new day
    if(TimeCurrent() >= last_trade_date + 86400) // 24 hours
    {
        daily_trades_count = 0;
        last_trade_date = TimeCurrent();
    }
    
    // Check maximum daily trades
    if(daily_trades_count >= MaxDailyTrades)
    {
        Comment("Maximum daily trades reached: ", daily_trades_count);
        return;
    }
    
    // Get current market data
    double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
    double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
    
    // Analyze market and generate signals
    int signal = AnalyzeMarket();
    
    // Execute trades based on signals
    if(signal == 1 && !HasOpenPosition(ORDER_TYPE_BUY))
    {
        OpenBuyOrder(ask);
    }
    else if(signal == -1 && !HasOpenPosition(ORDER_TYPE_SELL))
    {
        OpenSellOrder(bid);
    }
    
    // Update account information
    UpdateAccountInfo();
    
    // Send data to web application via WebSocket
    if(websocket_connected)
    {
        SendMarketData();
    }
}

//+------------------------------------------------------------------+
//| Analyze market conditions and generate trading signals          |
//+------------------------------------------------------------------+
int AnalyzeMarket()
{
    // Get indicator values
    double fast_ma[], slow_ma[], rsi[];
    ArraySetAsSeries(fast_ma, true);
    ArraySetAsSeries(slow_ma, true);
    ArraySetAsSeries(rsi, true);
    
    if(CopyBuffer(fast_ma_handle, 0, 0, 3, fast_ma) < 3 ||
       CopyBuffer(slow_ma_handle, 0, 0, 3, slow_ma) < 3 ||
       CopyBuffer(rsi_handle, 0, 0, 3, rsi) < 3)
    {
        return 0; // No signal
    }
    
    // Trend following strategy with RSI confirmation
    // Buy signal: Fast MA crosses above Slow MA and RSI is not overbought
    if(fast_ma[1] > slow_ma[1] && fast_ma[2] <= slow_ma[2] && rsi[1] < RSI_Overbought)
    {
        return 1; // Buy signal
    }
    
    // Sell signal: Fast MA crosses below Slow MA and RSI is not oversold
    if(fast_ma[1] < slow_ma[1] && fast_ma[2] >= slow_ma[2] && rsi[1] > RSI_Oversold)
    {
        return -1; // Sell signal
    }
    
    return 0; // No signal
}

//+------------------------------------------------------------------+
//| Open Buy Order                                                   |
//+------------------------------------------------------------------+
void OpenBuyOrder(double price)
{
    double sl = price - StopLoss * point_value * 10;
    double tp = price + TakeProfit * point_value * 10;
    
    if(trade.Buy(LotSize, symbol, price, sl, tp, "Gold Bot Buy"))
    {
        daily_trades_count++;
        Print("Buy order opened at ", price, " SL: ", sl, " TP: ", tp);
        
        // Send notification to web app
        if(websocket_connected)
        {
            SendTradeNotification("BUY", price, sl, tp);
        }
    }
    else
    {
        Print("Failed to open buy order. Error: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Open Sell Order                                                  |
//+------------------------------------------------------------------+
void OpenSellOrder(double price)
{
    double sl = price + StopLoss * point_value * 10;
    double tp = price - TakeProfit * point_value * 10;
    
    if(trade.Sell(LotSize, symbol, price, sl, tp, "Gold Bot Sell"))
    {
        daily_trades_count++;
        Print("Sell order opened at ", price, " SL: ", sl, " TP: ", tp);
        
        // Send notification to web app
        if(websocket_connected)
        {
            SendTradeNotification("SELL", price, sl, tp);
        }
    }
    else
    {
        Print("Failed to open sell order. Error: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Check if there's an open position of specified type             |
//+------------------------------------------------------------------+
bool HasOpenPosition(ENUM_ORDER_TYPE type)
{
    for(int i = 0; i < PositionsTotal(); i++)
    {
        if(position.SelectByIndex(i) && position.Symbol() == symbol && position.Magic() == MagicNumber)
        {
            if((type == ORDER_TYPE_BUY && position.PositionType() == POSITION_TYPE_BUY) ||
               (type == ORDER_TYPE_SELL && position.PositionType() == POSITION_TYPE_SELL))
            {
                return true;
            }
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Check if trading is within specified hours                      |
//+------------------------------------------------------------------+
bool IsWithinTradingHours()
{
    MqlDateTime dt;
    TimeCurrent(dt);
    
    string current_time = StringFormat("%02d:%02d", dt.hour, dt.min);
    
    return (current_time >= TradingStartTime && current_time <= TradingEndTime);
}

//+------------------------------------------------------------------+
//| Check if market is open                                         |
//+------------------------------------------------------------------+
bool IsMarketOpen()
{
    return SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE) == SYMBOL_TRADE_MODE_FULL;
}

//+------------------------------------------------------------------+
//| Update account information                                       |
//+------------------------------------------------------------------+
void UpdateAccountInfo()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double margin = AccountInfoDouble(ACCOUNT_MARGIN);
    double free_margin = AccountInfoDouble(ACCOUNT_FREEMARGIN);
    
    Comment(StringFormat("Balance: %.2f | Equity: %.2f | Margin: %.2f | Free: %.2f | Trades: %d",
                        balance, equity, margin, free_margin, daily_trades_count));
}

//+------------------------------------------------------------------+
//| Initialize WebSocket connection (simplified)                    |
//+------------------------------------------------------------------+
void InitializeWebSocket()
{
    // This is a simplified version - actual implementation would require
    // a WebSocket library or custom implementation
    websocket_connected = true;
    Print("WebSocket connection initialized");
}

//+------------------------------------------------------------------+
//| Close WebSocket connection                                       |
//+------------------------------------------------------------------+
void CloseWebSocket()
{
    websocket_connected = false;
    Print("WebSocket connection closed");
}

//+------------------------------------------------------------------+
//| Send market data to web application                             |
//+------------------------------------------------------------------+
void SendMarketData()
{
    double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
    double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
    double spread = ask - bid;
    
    // Create JSON-like string for market data
    string data = StringFormat("{\"type\":\"market_data\",\"symbol\":\"%s\",\"bid\":%.5f,\"ask\":%.5f,\"spread\":%.5f,\"timestamp\":%d}",
                              symbol, bid, ask, spread, TimeCurrent());
    
    // Send data (implementation depends on WebSocket library)
    Print("Market data: ", data);
}

//+------------------------------------------------------------------+
//| Send trade notification to web application                      |
//+------------------------------------------------------------------+
void SendTradeNotification(string trade_type, double price, double sl, double tp)
{
    string data = StringFormat("{\"type\":\"trade_opened\",\"trade_type\":\"%s\",\"symbol\":\"%s\",\"price\":%.5f,\"sl\":%.5f,\"tp\":%.5f,\"timestamp\":%d}",
                              trade_type, symbol, price, sl, tp, TimeCurrent());
    
    // Send notification (implementation depends on WebSocket library)
    Print("Trade notification: ", data);
}

//+------------------------------------------------------------------+
//| Handle WebSocket messages                                        |
//+------------------------------------------------------------------+
void OnWebSocketMessage(string message)
{
    // Parse incoming messages from web application
    // This could include commands to start/stop trading, update parameters, etc.
    Print("Received WebSocket message: ", message);
}