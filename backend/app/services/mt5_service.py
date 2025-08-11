"""MetaTrader 5 integration service

Note: The MetaTrader5 Python package is not available on PyPI and requires
the MetaTrader 5 terminal to be installed on the system. For production use,
you need to:

1. Install MetaTrader 5 terminal on your system
2. Download the MetaTrader5 Python package from the official MetaQuotes website
3. Install it manually: pip install MetaTrader5-5.0.45.0.tar.gz

For development and testing, this service runs in mock mode when the package
is not available.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd

from app.core.config import settings
from app.core.security import decrypt_sensitive_data
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import MetaTrader5, fallback to None if not available
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    logger.info("MetaTrader5 package loaded successfully")
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 package not available. Running in mock mode.")

class MT5Service:
    """MetaTrader 5 integration service"""
    
    def __init__(self):
        self.is_initialized = False
        self.current_account = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        
    async def initialize(self) -> bool:
        """Initialize MT5 connection"""
        if not MT5_AVAILABLE:
            logger.warning("MT5 not available, running in mock mode")
            self.is_initialized = True
            return True
            
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialize() failed, error code: {mt5.last_error()}")
                return False
            
            self.is_initialized = True
            logger.info("MT5 initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing MT5: {e}")
            return False
    
    async def connect_account(self, login: str, password: str, server: str) -> bool:
        """Connect to MT5 account"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not MT5_AVAILABLE:
                # Mock connection for development
                self.current_account = {
                    'login': login,
                    'server': server,
                    'name': 'Mock Account',
                    'balance': 10000.0,
                    'equity': 10000.0,
                    'margin': 0.0,
                    'free_margin': 10000.0,
                    'margin_level': 0.0,
                    'currency': 'USD'
                }
                logger.info(f"Mock MT5 connection established for account: {login}")
                return True
            
            # Decrypt password
            decrypted_password = decrypt_sensitive_data(password)
            
            # Attempt connection
            authorized = mt5.login(int(login), decrypted_password, server)
            
            if authorized:
                account_info = mt5.account_info()
                if account_info is None:
                    logger.error("Failed to get account info")
                    return False
                
                self.current_account = {
                    'login': login,
                    'server': server,
                    'name': account_info.name,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'free_margin': account_info.margin_free,
                    'margin_level': account_info.margin_level,
                    'currency': account_info.currency
                }
                
                self.connection_attempts = 0
                logger.info(f"Successfully connected to MT5 account: {login}")
                return True
            else:
                error_code = mt5.last_error()
                logger.error(f"Failed to connect to account {login}, error: {error_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to MT5 account: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from MT5"""
        try:
            if self.is_initialized:
                if MT5_AVAILABLE:
                    mt5.shutdown()
                self.is_initialized = False
                self.current_account = None
                logger.info("MT5 disconnected successfully")
        except Exception as e:
            logger.error(f"Error disconnecting from MT5: {e}")
    
    def is_connected(self) -> bool:
        """Check if MT5 is connected"""
        if not self.is_initialized:
            return False
        
        if not MT5_AVAILABLE:
            return self.current_account is not None
        
        account_info = mt5.account_info()
        return account_info is not None
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get current account information"""
        try:
            if not self.is_connected():
                return None
            
            if not MT5_AVAILABLE:
                # Return mock account info
                return {
                    'login': self.current_account['login'],
                    'balance': self.current_account['balance'],
                    'equity': self.current_account['equity'],
                    'margin': self.current_account['margin'],
                    'free_margin': self.current_account['free_margin'],
                    'margin_level': self.current_account['margin_level'],
                    'profit': 0.0,
                    'currency': self.current_account['currency'],
                    'leverage': 100,
                    'timestamp': datetime.now()
                }
            
            account_info = mt5.account_info()
            if account_info is None:
                return None
            
            return {
                'login': account_info.login,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit,
                'currency': account_info.currency,
                'leverage': account_info.leverage,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    async def get_symbol_info(self, symbol: str = "XAUUSD") -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        try:
            if not self.is_connected():
                return None
            
            if not MT5_AVAILABLE:
                # Return mock symbol info
                return {
                    'symbol': symbol,
                    'bid': 2000.0,
                    'ask': 2000.5,
                    'spread': 0.5,
                    'point': 0.01,
                    'digits': 2,
                    'trade_mode': 4,
                    'min_lot': 0.01,
                    'max_lot': 100.0,
                    'lot_step': 0.01,
                    'timestamp': datetime.now()
                }
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return None
            
            return {
                'symbol': symbol,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'spread': symbol_info.spread,
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'trade_mode': symbol_info.trade_mode,
                'min_lot': symbol_info.volume_min,
                'max_lot': symbol_info.volume_max,
                'lot_step': symbol_info.volume_step,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    async def get_market_data(self, symbol: str = "XAUUSD") -> Optional[Dict[str, Any]]:
        """Get current market data"""
        try:
            if not self.is_connected():
                return None
            
            if not MT5_AVAILABLE:
                # Return mock market data
                return {
                    'symbol': symbol,
                    'bid': 2000.0,
                    'ask': 2000.5,
                    'last': 2000.25,
                    'volume': 1000,
                    'time': datetime.now(),
                    'timestamp': datetime.now()
                }
            
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            
            return {
                'symbol': symbol,
                'bid': tick.bid,
                'ask': tick.ask,
                'spread': tick.ask - tick.bid,
                'volume': tick.volume,
                'time': datetime.fromtimestamp(tick.time),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    async def place_order(
        self,
        symbol: str,
        order_type: str,
        lot_size: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "Gold Trading Bot"
    ) -> Optional[Dict[str, Any]]:
        """Place a trading order"""
        try:
            if not self.is_connected():
                logger.error("Not connected to MT5")
                return None
            
            if not MT5_AVAILABLE:
                # Mock order placement
                import random
                ticket = random.randint(100000, 999999)
                current_price = 2000.0 if price is None else price
                
                return {
                    'retcode': 10009,  # TRADE_RETCODE_DONE
                    'ticket': ticket,
                    'order': ticket,
                    'volume': lot_size,
                    'price': current_price,
                    'bid': current_price - 0.5,
                    'ask': current_price + 0.5,
                    'comment': comment,
                    'request_id': ticket,
                    'retcode_external': 0
                }
            
            # Prepare order request
            order_type_mapping = {
                'BUY': mt5.ORDER_TYPE_BUY,
                'SELL': mt5.ORDER_TYPE_SELL,
                'BUY_LIMIT': mt5.ORDER_TYPE_BUY_LIMIT,
                'SELL_LIMIT': mt5.ORDER_TYPE_SELL_LIMIT,
                'BUY_STOP': mt5.ORDER_TYPE_BUY_STOP,
                'SELL_STOP': mt5.ORDER_TYPE_SELL_STOP
            }
            
            if order_type not in order_type_mapping:
                logger.error(f"Invalid order type: {order_type}")
                return None
            
            # Get current price if not provided
            if price is None:
                tick = mt5.symbol_info_tick(symbol)
                if tick is None:
                    logger.error(f"Failed to get current price for {symbol}")
                    return None
                price = tick.ask if order_type == 'BUY' else tick.bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type_mapping[order_type],
                "price": price,
                "deviation": settings.MT5_TIMEOUT,
                "magic": 12345,  # Magic number for identification
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add stop loss and take profit if provided
            if stop_loss is not None:
                request["sl"] = stop_loss
            if take_profit is not None:
                request["tp"] = take_profit
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("Order send failed, result is None")
                return None
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed, retcode: {result.retcode}, comment: {result.comment}")
                return None
            
            logger.info(f"Order placed successfully: {order_type} {lot_size} {symbol} at {price}")
            
            return {
                'ticket': result.order,
                'symbol': symbol,
                'order_type': order_type,
                'lot_size': lot_size,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'comment': comment,
                'retcode': result.retcode,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    async def close_position(self, ticket: int) -> bool:
        """Close an open position"""
        try:
            if not self.is_connected():
                return False
            
            if not MT5_AVAILABLE:
                # Mock position closing
                logger.info(f"Mock: Position {ticket} closed successfully")
                return True
            
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False
            
            position = position[0]
            
            # Prepare close request
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "position": ticket,
                "deviation": settings.MT5_TIMEOUT,
                "magic": 12345,
                "comment": "Gold Trading Bot - Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Failed to close position {ticket}")
                return False
            
            logger.info(f"Position {ticket} closed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error closing position {ticket}: {e}")
            return False
    
    async def get_open_positions(self, symbol: str = "XAUUSD") -> List[Dict[str, Any]]:
        """Get all open positions for a symbol"""
        try:
            if not self.is_connected():
                return []
            
            if not MT5_AVAILABLE:
                # Return mock positions
                return []
            
            positions = mt5.positions_get(symbol=symbol)
            if positions is None:
                return []
            
            result = []
            for position in positions:
                result.append({
                    'ticket': position.ticket,
                    'symbol': position.symbol,
                    'type': 'BUY' if position.type == mt5.POSITION_TYPE_BUY else 'SELL',
                    'volume': position.volume,
                    'price_open': position.price_open,
                    'price_current': position.price_current,
                    'profit': position.profit,
                    'swap': position.swap,
                    'commission': position.commission,
                    'time': datetime.fromtimestamp(position.time),
                    'comment': position.comment
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []
    
    async def get_trade_history(
        self,
        symbol: str = "XAUUSD",
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get trade history"""
        try:
            if not self.is_connected():
                return []
            
            if not MT5_AVAILABLE:
                # Return mock trade history
                return []
            
            if date_from is None:
                date_from = datetime.now() - timedelta(days=30)
            if date_to is None:
                date_to = datetime.now()
            
            deals = mt5.history_deals_get(date_from, date_to, group=symbol)
            if deals is None:
                return []
            
            result = []
            for deal in deals:
                result.append({
                    'ticket': deal.ticket,
                    'order': deal.order,
                    'symbol': deal.symbol,
                    'type': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL',
                    'volume': deal.volume,
                    'price': deal.price,
                    'profit': deal.profit,
                    'commission': deal.commission,
                    'swap': deal.swap,
                    'time': datetime.fromtimestamp(deal.time),
                    'comment': deal.comment
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return []
    
    async def get_price_data(
        self,
        symbol: str = "XAUUSD",
        timeframe: str = "H1",
        count: int = 100
    ) -> Optional[pd.DataFrame]:
        """Get historical price data"""
        try:
            if not self.is_connected():
                return None
            
            if not MT5_AVAILABLE:
                # Return mock price data
                import numpy as np
                dates = pd.date_range(end=datetime.now(), periods=count, freq='H')
                base_price = 2000.0
                prices = base_price + np.cumsum(np.random.randn(count) * 0.5)
                
                df = pd.DataFrame({
                    'time': dates,
                    'open': prices,
                    'high': prices + np.random.rand(count) * 2,
                    'low': prices - np.random.rand(count) * 2,
                    'close': prices + np.random.randn(count) * 0.5,
                    'tick_volume': np.random.randint(100, 1000, count)
                })
                df.set_index('time', inplace=True)
                return df
            
            timeframe_mapping = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
                'W1': mt5.TIMEFRAME_W1,
                'MN1': mt5.TIMEFRAME_MN1
            }
            
            if timeframe not in timeframe_mapping:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe_mapping[timeframe], 0, count)
            
            if rates is None:
                logger.error(f"Failed to get price data for {symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting price data: {e}")
            return None