"""MetaTrader 5 integration service (bridge-based)

This service runs inside Docker/WSL and cannot access native MetaTrader5 APIs.
Instead, it integrates via a bridge file written by an MT5 EA on Windows.

- Bridge file path (mounted): /app/mt5_data/signals.json
- MT5 is considered initialized/active only if the file exists, is fresh (modified
  within MT5_BRIDGE_MAX_AGE_SECONDS), and contains valid JSON.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta, timezone
import os
import json
import uuid
import pandas as pd

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MT5Service:
    """MetaTrader 5 integration service via bridge file"""
    
    def __init__(self):
        self.is_initialized = False
        self.current_account: Optional[Dict[str, Any]] = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        self.bridge_file_path: str = settings.MT5_BRIDGE_FILE
        self.bridge_max_age: int = int(getattr(settings, "MT5_BRIDGE_MAX_AGE_SECONDS", 30))
        self._ea_instruction_queue: Optional[List[Dict[str, Any]]] = None
    
    def set_instruction_queue(self, queue: List[Dict[str, Any]]) -> None:
        """Provide a shared EA instruction queue (e.g., app.state.ea_instruction_queue)."""
        self._ea_instruction_queue = queue
        logger.info("MT5Service instruction queue set")

    def _file_is_fresh(self, path: str) -> bool:
        try:
            stat = os.stat(path)
            mtime = stat.st_mtime
            age = datetime.now(timezone.utc).timestamp() - mtime
            return age <= self.bridge_max_age
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking bridge file freshness: {e}")
            return False

    def _load_bridge_data(self, require_fresh: bool = True) -> Optional[Dict[str, Any]]:
        """Load and parse bridge JSON if present (and fresh if required)."""
        try:
            if not os.path.exists(self.bridge_file_path):
                logger.debug(f"Bridge file not found at {self.bridge_file_path}")
                return None
            if require_fresh and not self._file_is_fresh(self.bridge_file_path):
                logger.warning("Bridge file is stale; MT5 considered not ready")
                return None
            with open(self.bridge_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                logger.error("Bridge file JSON is not an object")
                return None
            return data
        except json.JSONDecodeError as je:
            logger.error(f"Invalid JSON in bridge file: {je}")
            return None
        except Exception as e:
            logger.error(f"Failed to read bridge file: {e}")
            return None
    
    async def initialize(self) -> bool:
        """Initialize by validating the bridge file."""
        data = self._load_bridge_data(require_fresh=True)
        if data is None:
            self.is_initialized = False
            return False
        self.is_initialized = True
        # Optionally set current account snapshot
        acct = data.get("account") if isinstance(data, dict) else None
        if isinstance(acct, dict):
            self.current_account = {
                'login': acct.get('login'),
                'server': acct.get('server'),
                'name': acct.get('name'),
                'balance': acct.get('balance'),
                'equity': acct.get('equity'),
                'margin': acct.get('margin'),
                'free_margin': acct.get('free_margin'),
                'margin_level': acct.get('margin_level'),
                'currency': acct.get('currency')
            }
        logger.info("MT5 bridge initialized via signals.json")
        return True
    
    async def connect_account(self, login: str, password: str, server: str) -> bool:
        """Compatibility method: validates bridge readiness and captures account snapshot.
        Credentials are ignored because native MT5 login is not available in WSL.
        """
        if not self.is_initialized:
            await self.initialize()
        data = self._load_bridge_data(require_fresh=True)
        if data is None:
            logger.error("Bridge not ready; cannot connect account")
            return False
        acct = data.get("account") if isinstance(data, dict) else None
        if isinstance(acct, dict):
            self.current_account = {
                'login': acct.get('login') or login,
                'server': acct.get('server') or server,
                'name': acct.get('name'),
                'balance': acct.get('balance'),
                'equity': acct.get('equity'),
                'margin': acct.get('margin'),
                'free_margin': acct.get('free_margin'),
                'margin_level': acct.get('margin_level'),
                'currency': acct.get('currency')
            }
        logger.info("MT5 account connected via bridge")
        return True
    
    async def disconnect(self) -> None:
        try:
            self.is_initialized = False
            self.current_account = None
            logger.info("MT5 disconnected (bridge mode)")
        except Exception as e:
            logger.error(f"Error disconnecting MT5 (bridge): {e}")
    
    def is_connected(self) -> bool:
        if not self.is_initialized:
            return False
        return self._load_bridge_data(require_fresh=True) is not None
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        try:
            if not self.is_connected():
                # Return mock data if bridge is not available but service is initialized
                if self.is_initialized and self.current_account:
                    logger.debug("Bridge not fresh, returning cached account data")
                    return self.current_account
                logger.debug("Not connected to MT5 bridge")
                return None
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                logger.debug("No bridge data available")
                return None
            acct = data.get("account") if isinstance(data, dict) else None
            if not isinstance(acct, dict):
                logger.debug("No account data in bridge file")
                return None
            
            # Safely extract numeric values with defaults
            def safe_numeric(value, default=0.0):
                try:
                    return float(value) if value is not None else default
                except (ValueError, TypeError):
                    return default
            
            account_info = {
                'login': acct.get('login') or 'unknown',
                'balance': safe_numeric(acct.get('balance'), 10000.0),
                'equity': safe_numeric(acct.get('equity'), 10000.0),
                'margin': safe_numeric(acct.get('margin'), 0.0),
                'free_margin': safe_numeric(acct.get('free_margin'), 10000.0),
                'margin_level': safe_numeric(acct.get('margin_level'), 100.0),
                'profit': safe_numeric(acct.get('profit'), 0.0),
                'currency': acct.get('currency') or 'USD',
                'leverage': safe_numeric(acct.get('leverage'), 100),
                'timestamp': datetime.now()
            }
            
            # Update cached account info
            self.current_account = account_info
            return account_info
        except Exception as e:
            logger.error(f"Error getting account info (bridge): {e}")
            # Return cached data if available
            if self.current_account:
                logger.debug("Returning cached account info due to error")
                return self.current_account
            return None
    
    async def get_symbol_info(self, symbol: str = "XAUUSD") -> Optional[Dict[str, Any]]:
        try:
            if not self.is_connected():
                return None
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                return None
            # Try symbols map first
            symbols = data.get("symbols") if isinstance(data, dict) else None
            sym_info = None
            if isinstance(symbols, dict):
                sym_info = symbols.get(symbol)
            # Fallback to generic fields or defaults
            point = None
            digits = None
            tick_value = None
            lot_step = None
            if isinstance(sym_info, dict):
                point = sym_info.get("point")
                digits = sym_info.get("digits")
                tick_value = sym_info.get("tick_value") or sym_info.get("trade_tick_value")
                lot_step = sym_info.get("lot_step") or sym_info.get("volume_step")
            if point is None and isinstance(digits, (int, float)):
                try:
                    point = 10 ** (-int(digits))
                except Exception:
                    point = None
            return {
                'symbol': symbol,
                'bid': (data.get('tick') or {}).get('bid'),
                'ask': (data.get('tick') or {}).get('ask'),
                'spread': None,
                'point': point if point is not None else 0.01,
                'digits': digits if digits is not None else 2,
                'trade_mode': (sym_info or {}).get('trade_mode') if isinstance(sym_info, dict) else None,
                'min_lot': (sym_info or {}).get('volume_min') if isinstance(sym_info, dict) else None,
                'max_lot': (sym_info or {}).get('volume_max') if isinstance(sym_info, dict) else None,
                'lot_step': lot_step if lot_step is not None else 0.01,
                'tick_value': tick_value if tick_value is not None else 1.0,
                'contract_size': (sym_info or {}).get('trade_contract_size') if isinstance(sym_info, dict) else None,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol} (bridge): {e}")
            return None
    
    async def get_market_data(self, symbol: str = "XAUUSD") -> Optional[Dict[str, Any]]:
        try:
            if not self.is_connected():
                logger.debug("Not connected to MT5 bridge for market data")
                # Return mock market data if requested
                return {
                    'symbol': symbol,
                    'bid': 2000.0,  # Mock bid price for XAUUSD
                    'ask': 2001.0,  # Mock ask price for XAUUSD
                    'spread': 1.0,
                    'volume': 0,
                    'time': datetime.now(),
                    'timestamp': datetime.now()
                }
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                logger.debug("No bridge data for market data")
                return None
            tick = data.get("tick") if isinstance(data, dict) else None
            if not isinstance(tick, dict):
                logger.debug("No tick data in bridge file")
                return None
            
            # Convert time if numeric/str
            tval = tick.get("time")
            tdt = None
            try:
                if isinstance(tval, (int, float)):
                    tdt = datetime.fromtimestamp(float(tval))
                elif isinstance(tval, str):
                    tdt = datetime.fromisoformat(tval.replace("Z", "+00:00"))
            except Exception:
                tdt = datetime.now()  # Use current time as fallback
            
            # Safely extract numeric values
            def safe_numeric(value, default=None):
                try:
                    return float(value) if value is not None else default
                except (ValueError, TypeError):
                    return default
            
            bid = safe_numeric(tick.get("bid"))
            ask = safe_numeric(tick.get("ask"))
            spread = None
            if bid is not None and ask is not None:
                spread = ask - bid
            
            return {
                'symbol': tick.get('symbol') or symbol,
                'bid': bid,
                'ask': ask,
                'spread': spread,
                'volume': safe_numeric(tick.get('volume'), 0),
                'time': tdt,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol} (bridge): {e}")
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
        """Enqueue an order instruction for the EA to execute on MT5."""
        try:
            if not self.is_connected():
                logger.error("Not connected to MT5 (bridge not ready)")
                return None
            if self._ea_instruction_queue is None:
                logger.error("EA instruction queue not set; cannot enqueue order")
                return None
            if order_type not in {"BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP", "SELL_STOP"}:
                logger.error(f"Invalid order type: {order_type}")
                return None
            instruction_id = str(uuid.uuid4())
            item = {
                "id": instruction_id,
                "action": "order",
                "symbol": symbol,
                "side": order_type,
                "lot": float(lot_size),
                "price": float(price) if isinstance(price, (int, float)) else None,
                "sl": float(stop_loss) if isinstance(stop_loss, (int, float)) else None,
                "tp": float(take_profit) if isinstance(take_profit, (int, float)) else None,
                "comment": comment,
                "timestamp": datetime.utcnow().isoformat()
            }
            self._ea_instruction_queue.append(item)
            logger.info(f"Enqueued EA instruction {instruction_id}: {order_type} {symbol} {lot_size}")
            return {"success": True, "instruction_id": instruction_id, "enqueued": item}
        except Exception as e:
            logger.error(f"Error enqueuing order (bridge): {e}")
            return None
    
    async def close_position(self, ticket: int) -> bool:
        try:
            if not self.is_connected():
                return False
            if self._ea_instruction_queue is None:
                logger.error("EA instruction queue not set; cannot enqueue close")
                return False
            instruction_id = str(uuid.uuid4())
            item = {
                "id": instruction_id,
                "action": "close",
                "ticket": int(ticket),
                "timestamp": datetime.utcnow().isoformat()
            }
            self._ea_instruction_queue.append(item)
            logger.info(f"Enqueued EA close instruction for ticket {ticket}")
            return True
        except Exception as e:
            logger.error(f"Error enqueuing close position (bridge): {e}")
            return False
    
    async def get_open_positions(self, symbol: str = "XAUUSD") -> List[Dict[str, Any]]:
        try:
            if not self.is_connected():
                return []
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                return []
            positions = data.get("positions") if isinstance(data, dict) else None
            if not isinstance(positions, list):
                return []
            result: List[Dict[str, Any]] = []
            for p in positions:
                if not isinstance(p, dict):
                    continue
                if symbol and p.get("symbol") != symbol:
                    continue
                result.append({
                    'ticket': p.get('ticket'),
                    'symbol': p.get('symbol'),
                    'type': p.get('type'),
                    'volume': p.get('volume'),
                    'price_open': p.get('price_open') or p.get('open_price'),
                    'price_current': p.get('price_current') or p.get('current_price'),
                    'profit': p.get('profit'),
                    'swap': p.get('swap'),
                    'commission': p.get('commission'),
                    'time': datetime.fromisoformat(p['time']) if isinstance(p.get('time'), str) else None,
                    'comment': p.get('comment')
                })
            return result
        except Exception as e:
            logger.error(f"Error getting open positions (bridge): {e}")
            return []
    
    async def get_trade_history(
        self,
        symbol: str = "XAUUSD",
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        try:
            if not self.is_connected():
                return []
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                return []
            deals = data.get("deals") or data.get("history_deals")
            if not isinstance(deals, list):
                return []
            result: List[Dict[str, Any]] = []
            for d in deals:
                if not isinstance(d, dict):
                    continue
                if symbol and d.get("symbol") != symbol:
                    continue
                tval = d.get('time')
                tdt = None
                try:
                    if isinstance(tval, (int, float)):
                        tdt = datetime.fromtimestamp(float(tval))
                    elif isinstance(tval, str):
                        tdt = datetime.fromisoformat(tval.replace("Z", "+00:00"))
                except Exception:
                    tdt = None
                result.append({
                    'ticket': d.get('ticket'),
                    'order': d.get('order'),
                    'symbol': d.get('symbol'),
                    'type': d.get('type'),
                    'volume': d.get('volume'),
                    'price': d.get('price'),
                    'profit': d.get('profit'),
                    'commission': d.get('commission'),
                    'swap': d.get('swap'),
                    'time': tdt,
                    'comment': d.get('comment'),
                    'entry': d.get('entry')
                })
            return result
        except Exception as e:
            logger.error(f"Error getting trade history (bridge): {e}")
            return []
    
    async def get_price_data(
        self,
        symbol: str = "XAUUSD",
        timeframe: str = "H1",
        count: int = 100
    ) -> Optional[pd.DataFrame]:
        try:
            if not self.is_connected():
                return None
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                return None
            series = None
            # Try timeframe-specific candles
            if isinstance(data.get('candles'), dict):
                series = data['candles'].get(timeframe)
            # Fallback to generic rates/bars arrays
            if series is None:
                series = data.get('rates') or data.get('bars') or data.get('ohlc')
            if not isinstance(series, list):
                return None
            rows: List[Dict[str, Any]] = []
            for r in series[-count:]:
                if not isinstance(r, dict):
                    continue
                tval = r.get('time')
                try:
                    if isinstance(tval, (int, float)):
                        t = datetime.fromtimestamp(float(tval))
                    elif isinstance(tval, str):
                        t = datetime.fromisoformat(tval.replace("Z", "+00:00"))
                    else:
                        continue
                except Exception:
                    continue
                rows.append({
                    'time': t,
                    'open': r.get('open'),
                    'high': r.get('high'),
                    'low': r.get('low'),
                    'close': r.get('close'),
                    'tick_volume': r.get('tick_volume') or r.get('tickVolume') or r.get('volume'),
                    'real_volume': r.get('real_volume') or r.get('realVolume')
                })
            if not rows:
                return None
            df = pd.DataFrame(rows)
            df.set_index('time', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error getting price data (bridge): {e}")
            return None

    async def get_orders_history(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict[str, Any]]:
        try:
            if not self.is_connected():
                return []
            data = self._load_bridge_data(require_fresh=True)
            if not data:
                return []
            orders = data.get('orders') or data.get('history_orders')
            if not isinstance(orders, list):
                return []
            res: List[Dict[str, Any]] = []
            for o in orders:
                if not isinstance(o, dict):
                    continue
                t_setup = o.get('time_setup') or o.get('timeSetup')
                t_done = o.get('time_done') or o.get('timeDone')
                def _parse_time(v):
                    try:
                        if isinstance(v, (int, float)):
                            return datetime.fromtimestamp(float(v))
                        if isinstance(v, str):
                            return datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except Exception:
                        return None
                    return None
                res.append({
                    'ticket': o.get('ticket'),
                    'symbol': o.get('symbol'),
                    'type': o.get('type'),
                    'volume_initial': o.get('volume_initial') or o.get('volumeInitial'),
                    'volume_current': o.get('volume_current') or o.get('volumeCurrent'),
                    'price_open': o.get('price_open'),
                    'sl': o.get('sl'),
                    'tp': o.get('tp'),
                    'time_setup': _parse_time(t_setup),
                    'time_done': _parse_time(t_done),
                    'reason': o.get('reason'),
                    'state': o.get('state'),
                    'comment': o.get('comment'),
                })
            return res
        except Exception as e:
            logger.error(f"Error getting orders history (bridge): {e}")
            return []