"""Trading Engine Service"""

import asyncio
import logging
from typing import Optional
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
        self.is_running = False
        self.trading_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """Start the trading engine"""
        try:
            self.is_running = True
            logger.info("Trading engine started")
            
            # Start the main trading loop
            self.trading_task = asyncio.create_task(self._trading_loop())
            
        except Exception as e:
            logger.error(f"Failed to start trading engine: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the trading engine"""
        try:
            self.is_running = False
            
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
        while self.is_running:
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
        return self.is_running