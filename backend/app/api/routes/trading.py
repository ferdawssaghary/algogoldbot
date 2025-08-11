"""Trading API routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/status")
async def get_trading_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current trading status"""
    return {
        "status": "stopped",
        "user_id": current_user.id,
        "message": "Trading is currently stopped"
    }

@router.post("/start")
async def start_trading(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start trading bot"""
    return {
        "status": "started",
        "user_id": current_user.id,
        "message": "Trading bot started successfully"
    }

@router.post("/stop")
async def stop_trading(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop trading bot"""
    return {
        "status": "stopped",
        "user_id": current_user.id,
        "message": "Trading bot stopped successfully"
    }