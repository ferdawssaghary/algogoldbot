"""Telegram Bot API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()

class TelegramConfigIn(BaseModel):
    bot_token: str
    chat_id: str

@router.get("/status")
async def get_telegram_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Telegram bot status"""
    telegram_service = getattr(request.app.state, "telegram_service", None)
    return {
        "status": "active" if (telegram_service and telegram_service.is_connected()) else "inactive",
        "user_id": current_user.id,
        "bot_token": "configured" if settings.TELEGRAM_BOT_TOKEN else None,
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "notifications_enabled": settings.TELEGRAM_ENABLED
    }

@router.post("/test")
async def send_test_notification(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a test Telegram notification"""
    telegram_service = getattr(request.app.state, "telegram_service", None)
    if not telegram_service:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Telegram service unavailable")
    ok = await telegram_service.send_notification("Test signal from dashboard", "test")
    return {"success": ok}

@router.post("/configure")
async def configure_telegram(
    payload: TelegramConfigIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Configure Telegram bot settings at runtime"""
    settings.TELEGRAM_BOT_TOKEN = payload.bot_token
    settings.TELEGRAM_CHAT_ID = payload.chat_id
    return {"success": True, "message": "Telegram settings updated"}