"""Trading Engine Service"""

import asyncio
from typing import Optional, Dict, Set
from datetime import datetime, date

from app.utils.logger import setup_logger
from app.services.mt5_service import MT5Service
from app.services.telegram_service import TelegramService
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.trading import BotSettings, Trade

logger = setup_logger(__name__)

class TradingEngine:
    """Main trading engine for automated trading"""
    
    def __init__(self, mt5_service: MT5Service, telegram_service: TelegramService):
        self.mt5_service = mt5_service
        self.telegram_service = telegram_service
        self._is_running = False
        self.trading_task: Optional[asyncio.Task] = None
        self.position_watcher_task: Optional[asyncio.Task] = None
        self.active_users: Set[int] = set()
        self.user_websocket_clients: Dict[int, Set] = {}
        self.trades_today_count: int = 0
        self.trades_today_date: date = date.today()
        self.user_tracked_tickets: Dict[int, Set[int]] = {}
        
    async def start(self) -> None:
        """Start the trading engine"""
        try:
            self._is_running = True
            logger.info("Trading engine started")
            
            # Start the main trading loop
            self.trading_task = asyncio.create_task(self._trading_loop())
            # Start the position watcher loop
            self.position_watcher_task = asyncio.create_task(self._position_watcher_loop())
            
        except Exception as e:
            logger.error(f"Failed to start trading engine: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the trading engine"""
        try:
            self._is_running = False
            
            if self.trading_task:
                self.trading_task.cancel()
                try:
                    await self.trading_task
                except asyncio.CancelledError:
                    pass
            if self.position_watcher_task:
                self.position_watcher_task.cancel()
                try:
                    await self.position_watcher_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Trading engine stopped")
            
        except Exception as e:
            logger.error(f"Error stopping trading engine: {e}")
    
    async def _trading_loop(self) -> None:
        """Main trading loop"""
        while self._is_running:
            try:
                # Check for trading signals
                await self._check_signals()
                
                # Update account status
                await self._update_account_status()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _check_signals(self) -> None:
        """Check for trading signals"""
        try:
            # Reset daily counter
            if self.trades_today_date != date.today():
                self.trades_today_date = date.today()
                self.trades_today_count = 0

            if self.trades_today_count >= 10:
                logger.debug("Daily trade limit reached")
                return

            # Fetch price data
            df = await self.mt5_service.get_price_data(symbol="XAUUSD", timeframe="M15", count=200)
            if df is None or df.empty:
                return

            # Compute indicators
            ema_fast = df["close"].ewm(span=12, adjust=False).mean()
            ema_slow = df["close"].ewm(span=26, adjust=False).mean()
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            rs = gain / loss.replace({0: 1e-9})
            rsi = 100 - (100 / (1 + rs))

            # Generate signal on last two bars
            cross_up = ema_fast.iloc[-2] <= ema_slow.iloc[-2] and ema_fast.iloc[-1] > ema_slow.iloc[-1]
            cross_down = ema_fast.iloc[-2] >= ema_slow.iloc[-2] and ema_fast.iloc[-1] < ema_slow.iloc[-1]
            rsi_last = float(rsi.iloc[-1])

            order_type = None
            if cross_up and rsi_last < 70:
                order_type = "BUY"
            elif cross_down and rsi_last > 30:
                order_type = "SELL"

            if not order_type:
                return

            # For each active user, apply their settings
            async with AsyncSessionLocal() as session:
                for user_id in list(self.active_users):
                    try:
                        await self._execute_signal_for_user(session, user_id, order_type)
                    except Exception as ue:
                        await self.telegram_service.send_error(f"User {user_id} trade error: {ue}")
        except Exception as e:
            logger.error(f"Error checking signals: {e}")
            await self.telegram_service.send_error(f"Signal loop error: {e}")

    async def _execute_signal_for_user(self, db_session, user_id: int, order_type: str) -> None:
        result = await db_session.execute(select(BotSettings).where(BotSettings.user_id == user_id))
        s: BotSettings | None = result.scalar_one_or_none()
        timeframe = s.timeframe if s and s.timeframe else "M15"
        if s and s.enable_strategy is False:
            return
        # reload data for user timeframe if different
        df = await self.mt5_service.get_price_data(symbol="XAUUSD", timeframe=timeframe, count=200)
        if df is None or df.empty:
            return
        stop_loss_pips = int(s.stop_loss_pips) if s else (settings.DEFAULT_STOP_LOSS or 50)
        take_profit_pips = int(s.take_profit_pips) if s else (settings.DEFAULT_TAKE_PROFIT or 100)
        max_spread_pips = float(getattr(s, 'max_spread', settings.MAX_SPREAD)) if s else (settings.MAX_SPREAD or 5.0)
        risk_pct = float(s.risk_percentage) if s else (settings.RISK_PERCENTAGE or 2.0)

        md = await self.mt5_service.get_market_data("XAUUSD")
        sym = await self.mt5_service.get_symbol_info("XAUUSD")
        if not md or not sym:
            return
        bid = float(md.get("bid"))
        ask = float(md.get("ask"))
        price = ask if order_type == "BUY" else bid
        current_spread_pips = abs(ask - bid) / (sym.get("point") or 0.01)
        if current_spread_pips > max_spread_pips:
            return

        pip_value = sym.get("point") or 0.01
        sl = price - stop_loss_pips * pip_value if order_type == "BUY" else price + stop_loss_pips * pip_value
        tp = price + take_profit_pips * pip_value if order_type == "BUY" else price - take_profit_pips * pip_value

        acct = await self.mt5_service.get_account_info()
        balance = float(acct.get("balance", 0.0)) if acct else 0.0
        tick_value = float(s.custom_tick_value) if s and s.custom_tick_value is not None else float(sym.get("tick_value") or 1.0)
        point = float(s.custom_point) if s and s.custom_point is not None else float(sym.get("point") or 0.01)
        per_pip_value_per_lot = tick_value / (point / 0.01)
        risk_amount = balance * (risk_pct / 100.0)
        sl_pips = float(stop_loss_pips)
        lot_size = max(0.01, min(100.0, risk_amount / (sl_pips * per_pip_value_per_lot + 1e-6)))
        lot_step = float(sym.get("lot_step") or 0.01)
        lot_size = max(lot_step, (round(lot_size / lot_step) * lot_step))

        result = await self.mt5_service.place_order(
            symbol="XAUUSD",
            order_type=order_type,
            lot_size=lot_size,
            price=None,
            stop_loss=sl,
            take_profit=tp,
            comment="EMA12/26 + RSI14"
        )
        if result:
            self.trades_today_count += 1
            await self.telegram_service.send_notification(
                f"{order_type} XAUUSD @ {price:.2f} SL {sl:.2f} TP {tp:.2f} (risk {risk_pct:.1f}%)",
                "trade_entry"
            )
            # Track ticket for user
            ticket = int(result.get("ticket")) if result.get("ticket") else None
            if ticket:
                self.user_tracked_tickets.setdefault(user_id, set()).add(ticket)
            # Persist trade entry
            try:
                trade = Trade(
                    user_id=user_id,
                    mt5_ticket=ticket,
                    signal_id=None,
                    trade_type=order_type,
                    symbol="XAUUSD",
                    lot_size=lot_size,
                    open_price=price,
                    stop_loss=sl,
                    take_profit=tp,
                    status="OPEN",
                    comment="EMA12/26+RSI14"
                )
                db_session.add(trade)
                await db_session.commit()
            except Exception as pe:
                await db_session.rollback()
                await self.telegram_service.send_error(f"Persist trade error ticket {ticket}: {pe}")
            # Basic exit detection placeholder (to be extended with polling open positions and matching)
            # For now, rely on trade history checks in a separate loop if implemented, then:
            # await self.telegram_service.send_notification("CLOSE XAUUSD ...", "trade_exit")

    async def _update_account_status(self) -> None:
        """Update account status"""
        try:
            info = await self.mt5_service.get_account_info()
            md = await self.mt5_service.get_market_data("XAUUSD")
            if not info and not md:
                return
            payload = {
                "type": "account_status",
                "balance": float(info.get("balance", 0.0)) if info else None,
                "equity": float(info.get("equity", 0.0)) if info else None,
                "profit": float(info.get("profit", 0.0)) if info else None,
                "tick": {
                    "symbol": md.get("symbol") if md else None,
                    "bid": float(md.get("bid")) if md else None,
                    "ask": float(md.get("ask")) if md else None,
                    "time": (md.get("time").isoformat() if hasattr(md.get("time"), 'isoformat') else None) if md else None
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            for user_id, clients in list(self.user_websocket_clients.items()):
                for ws in list(clients):
                    try:
                        await ws.send_json(payload)
                    except Exception:
                        # Drop dead clients silently
                        pass
        except Exception as e:
            logger.error(f"Error updating account status: {e}")

    async def _position_watcher_loop(self) -> None:
        while self._is_running:
            try:
                if not self.user_tracked_tickets:
                    await asyncio.sleep(10)
                    continue
                # Get all currently open positions
                open_positions = await self.mt5_service.get_open_positions(symbol="XAUUSD")
                open_tickets = {int(p.get("ticket")) for p in open_positions}
                # For each user, find tickets that have closed
                for user_id, tickets in list(self.user_tracked_tickets.items()):
                    closed = [t for t in list(tickets) if t not in open_tickets]
                    if not closed:
                        continue
                    # For each closed ticket, try to fetch closing info
                    for t in closed:
                        try:
                            # Narrow history search window using DB trade open_time
                            from sqlalchemy import select as sa_select
                            async with AsyncSessionLocal() as s:
                                res = await s.execute(sa_select(Trade).where(Trade.user_id == user_id, Trade.mt5_ticket == t))
                                trade: Trade | None = res.scalar_one_or_none()
                                date_from = None
                                if trade and trade.open_time:
                                    from datetime import timedelta
                                    date_from = trade.open_time - timedelta(hours=2)
                            history = await self.mt5_service.get_trade_history(symbol="XAUUSD", date_from=date_from)
                            # Prefer OUT deals for the ticket
                            deals = [d for d in history if int(d.get("order", 0)) == t or int(d.get("ticket", 0)) == t]
                            out_deals = [d for d in deals if (d.get("entry") == 'OUT' or d.get("entry") == 'OUT_BY')]
                            deal = out_deals[0] if out_deals else (deals[0] if deals else None)
                            if deal:
                                profit = float(deal.get("profit", 0.0))
                                price = float(deal.get("price", 0.0))
                                volume = float(deal.get("volume", 0.0))
                                comment = deal.get("comment") or ''
                                msg = f"Closed XAUUSD ticket {t} @ {price:.2f} vol {volume:.2f} P/L {profit:.2f} {comment}"
                                # Update DB trade
                                try:
                                    async with AsyncSessionLocal() as s2:
                                        res2 = await s2.execute(sa_select(Trade).where(Trade.user_id == user_id, Trade.mt5_ticket == t))
                                        tr = res2.scalar_one_or_none()
                                        if tr:
                                            tr.close_price = price
                                            tr.profit = profit
                                            tr.status = "CLOSED"
                                            from datetime import datetime as dt
                                            tr.close_time = deal.get("time") if isinstance(deal.get("time"), dt) else dt.utcnow()
                                            await s2.commit()
                                except Exception as ue:
                                    await self.telegram_service.send_error(f"Persist exit error {t}: {ue}")
                            else:
                                msg = f"Closed XAUUSD ticket {t} (details unavailable)"
                            await self.telegram_service.send_notification(msg, "trade_exit")
                        except Exception as ce:
                            await self.telegram_service.send_error(f"Exit detection error for ticket {t}: {ce}")
                        finally:
                            tickets.discard(t)
                    if not tickets:
                        self.user_tracked_tickets.pop(user_id, None)
                await asyncio.sleep(15)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(15)
    
    def is_active(self) -> bool:
        """Check if trading engine is active"""
        return self._is_running
    
    def is_running(self) -> bool:
        """Compatibility method used by main app to check engine state"""
        return self._is_running
    
    async def start_trading(self, user_id: int, db) -> Dict:
        """Start trading for a specific user"""
        try:
            self.active_users.add(user_id)
            logger.info(f"Trading enabled for user_id={user_id}")
            return {"success": True, "message": "Trading started"}
        except Exception as e:
            logger.error(f"Error starting trading for user {user_id}: {e}")
            return {"success": False, "message": "Failed to start trading"}
    
    async def stop_trading(self, user_id: int, db) -> Dict:
        """Stop trading for a specific user"""
        try:
            self.active_users.discard(user_id)
            logger.info(f"Trading disabled for user_id={user_id}")
            return {"success": True, "message": "Trading stopped"}
        except Exception as e:
            logger.error(f"Error stopping trading for user {user_id}: {e}")
            return {"success": False, "message": "Failed to stop trading"}
    
    async def get_status(self, user_id: int, db) -> Dict:
        """Return a minimal status payload expected by the API"""
        is_user_active = user_id in self.active_users
        # Placeholder metrics; in a full implementation these would be queried/calculated
        return {
            "is_active": is_user_active,
            "total_trades": 0,
            "open_trades": 0,
            "daily_profit": 0.0,
            "account_balance": 0.0,
            "account_equity": 0.0,
        }
    
    async def add_websocket_client(self, user_id: int, websocket) -> None:
        """Register a websocket client for a user"""
        if user_id not in self.user_websocket_clients:
            self.user_websocket_clients[user_id] = set()
        self.user_websocket_clients[user_id].add(websocket)
        logger.debug(f"WebSocket client added for user_id={user_id}")
    
    async def remove_websocket_client(self, user_id: int, websocket) -> None:
        """Unregister a websocket client for a user"""
        clients = self.user_websocket_clients.get(user_id)
        if not clients:
            return
        if websocket in clients:
            clients.remove(websocket)
        if not clients:
            self.user_websocket_clients.pop(user_id, None)
        logger.debug(f"WebSocket client removed for user_id={user_id}")