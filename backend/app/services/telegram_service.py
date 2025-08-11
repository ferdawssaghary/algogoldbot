"""Telegram Service for notifications"""

import asyncio
from typing import Optional

from app.utils.logger import setup_logger
from app.core.config import settings
import httpx

logger = setup_logger(__name__)

class TelegramService:
    """Telegram bot service for notifications"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.is_running = False
        self.notification_task: Optional[asyncio.Task] = None
        
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
    
    def is_active(self) -> bool:
        """Check if telegram service is active"""
        return self.is_running
    
    def is_connected(self) -> bool:
        """Compatibility method used by the main app to check service state"""
        return self.is_running