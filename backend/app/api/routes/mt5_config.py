"""MT5 Configuration API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/config")
async def get_mt5_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get MT5 configuration"""
    return {
        "user_id": current_user.id,
        "server": "LiteFinance-Demo",
        "account_login": "",
        "is_connected": False,
        "account_info": None
    }

@router.post("/connect")
async def connect_mt5(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect to MT5"""
    return {
        "status": "connected",
        "user_id": current_user.id,
        "message": "MT5 connected successfully (mock mode)"
    }

@router.post("/disconnect")
async def disconnect_mt5(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect from MT5"""
    return {
        "status": "disconnected",
        "user_id": current_user.id,
        "message": "MT5 disconnected successfully"
    }