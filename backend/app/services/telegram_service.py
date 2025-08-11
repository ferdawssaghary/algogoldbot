"""Telegram Service for notifications"""

import asyncio
from typing import Optional, TYPE_CHECKING

from app.utils.logger import setup_logger
from app.core.config import settings
import httpx

logger = setup_logger(__name__)

if TYPE_CHECKING:
    from app.services.mt5_service import MT5Service

class TelegramService:
    """Telegram bot service for notifications"""
    
    def __init__(self, mt5_service: Optional["MT5Service"] = None):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.is_running = False
        self.notification_task: Optional[asyncio.Task] = None
        self.mt5_service = mt5_service
        self._last_summary_date: Optional[str] = None
        
    async def start(self) -> None:
        """Start the telegram service"""
        try:
            self.is_running = True
            logger.info("Telegram service started")
            
            # Start the notification loop
            self.notification_task = asyncio.create_task(self._notification_loop())
            
        except Exception as e:
            logger.error(f"Failed to start telegram service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the telegram service"""
        try:
            self.is_running = False
            
            if self.notification_task:
                self.notification_task.cancel()
                try:
                    await self.notification_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Telegram service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping telegram service: {e}")
    
    async def _notification_loop(self) -> None:
        """Main notification loop"""
        while self.is_running:
            try:
                # Check for notifications
                await self._check_notifications()
                # Daily summary at 23:59 UTC
                from datetime import datetime as dt
                now = dt.utcnow()
                today_str = now.strftime('%Y-%m-%d')
                if now.hour == 23 and now.minute >= 59 and self._last_summary_date != today_str:
                    await self._send_daily_summary()
                    self._last_summary_date = today_str
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in notification loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _check_notifications(self) -> None:
        """Check for pending notifications"""
        try:
            # Mock notification checking
            logger.debug("Checking for notifications...")
            
        except Exception as e:
            logger.error(f"Error checking notifications: {e}")
    
    async def send_message(self, message: str) -> bool:
        """Send a message via Telegram"""
        try:
            if not settings.TELEGRAM_ENABLED or not self.bot_token or not self.chat_id:
                logger.info(f"Telegram disabled or not configured. Message: {message}")
                return True
            api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(api_url, json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                })
                if resp.status_code == 200 and resp.json().get("ok"):
                    logger.info("Telegram message sent")
                    return True
                logger.error(f"Telegram API error: {resp.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending telegram message: {e}")
            return False
    
    async def send_notification(self, message: str, event_type: str = "info") -> bool:
        """Compatibility method used by the main app to send notifications"""
        return await self.send_message(f"[{event_type}] {message}")
    
    async def send_error(self, message: str) -> bool:
        return await self.send_notification(message, "error")

    async def _send_daily_summary(self) -> None:
        try:
            if not self.mt5_service:
                return
            info = await self.mt5_service.get_account_info()
            if not info:
                return
            msg = (
                f"Daily Summary\n"
                f"Balance: {float(info.get('balance', 0.0)):.2f}\n"
                f"Equity: {float(info.get('equity', 0.0)):.2f}\n"
                f"Profit: {float(info.get('profit', 0.0)):.2f}"
            )
            await self.send_notification(msg, "daily_summary")
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    def is_active(self) -> bool:
        """Check if telegram service is active"""
        return self.is_running
    
    def is_connected(self) -> bool:
        """Compatibility method used by the main app to check service state"""
        return self.is_running