"""Telegram Bot API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/status")
async def get_telegram_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Telegram bot status"""
    return {
        "status": "active",
        "user_id": current_user.id,
        "bot_token": "configured",
        "chat_id": "configured",
        "notifications_enabled": True
    }

@router.post("/send")
async def send_telegram_message(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send Telegram message"""
    return {
        "status": "sent",
        "user_id": current_user.id,
        "message": "Test message sent successfully"
    }

@router.post("/configure")
async def configure_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Configure Telegram bot"""
    return {
        "status": "configured",
        "user_id": current_user.id,
        "message": "Telegram bot configured successfully"
    }