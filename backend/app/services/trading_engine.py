"""Trading Engine Service"""

import asyncio
import logging
from typing import Optional, Dict, Set
from datetime import datetime

from app.utils.logger import setup_logger
from app.services.mt5_service import MT5Service
from app.services.telegram_service import TelegramService

logger = setup_logger(__name__)

class TradingEngine:
    """Main trading engine for automated trading"""
    
    def __init__(self, mt5_service: MT5Service, telegram_service: TelegramService):
        self.mt5_service = mt5_service
        self.telegram_service = telegram_service
        self._is_running = False
        self.trading_task: Optional[asyncio.Task] = None
        self.active_users: Set[int] = set()
        self.user_websocket_clients: Dict[int, Set] = {}
        
    async def start(self) -> None:
        """Start the trading engine"""
        try:
            self._is_running = True
            logger.info("Trading engine started")
            
            # Start the main trading loop
            self.trading_task = asyncio.create_task(self._trading_loop())
            
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
            # Mock signal checking
            logger.debug("Checking for trading signals...")
            
        except Exception as e:
            logger.error(f"Error checking signals: {e}")
    
    async def _update_account_status(self) -> None:
        """Update account status"""
        try:
            # Mock account status update
            logger.debug("Updating account status...")
            
        except Exception as e:
            logger.error(f"Error updating account status: {e}")
    
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