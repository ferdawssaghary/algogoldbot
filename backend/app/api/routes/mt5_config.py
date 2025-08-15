"""MT5 Configuration API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.trading import MT5Account
from app.core.security import encrypt_sensitive_data
from sqlalchemy import select

router = APIRouter()

class MT5ConfigIn(BaseModel):
    account_login: str
    account_password: str
    server_name: str = "LiteFinance-MT5-Demo"

@router.get("/config")
async def get_mt5_config(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get MT5 configuration"""
    result = await db.execute(select(MT5Account).where(MT5Account.user_id == current_user.id))
    acc = result.scalar_one_or_none()
    mt5_service = getattr(request.app.state, "mt5_service", None)
    is_connected = mt5_service.is_connected() if mt5_service else False
    account_info = await mt5_service.get_account_info() if mt5_service and is_connected else None
    return {
        "user_id": current_user.id,
        "server": acc.server_name if acc else "LiteFinance-MT5-Demo",
        "account_login": acc.account_login if acc else "",
        "is_connected": is_connected,
        "account_info": account_info
    }

@router.post("/config")
async def save_mt5_config(
    payload: MT5ConfigIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save MT5 configuration to database"""
    result = await db.execute(select(MT5Account).where(MT5Account.user_id == current_user.id))
    acc = result.scalar_one_or_none()
    if acc is None:
        acc = MT5Account(
            user_id=current_user.id,
            account_login=payload.account_login,
            account_password=encrypt_sensitive_data(payload.account_password),
            server_name=payload.server_name,
            is_active=True,
        )
        db.add(acc)
    else:
        acc.account_login = payload.account_login
        acc.account_password = encrypt_sensitive_data(payload.account_password)
        acc.server_name = payload.server_name
    await db.commit()
    return {"success": True, "message": "MT5 configuration saved"}

@router.post("/connect")
async def connect_mt5(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect to MT5 using saved credentials"""
    mt5_service = getattr(request.app.state, "mt5_service", None)
    if not mt5_service:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MT5 service unavailable")
    result = await db.execute(select(MT5Account).where(MT5Account.user_id == current_user.id))
    acc = result.scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MT5 credentials not configured")
    success = await mt5_service.connect_account(acc.account_login, acc.account_password, acc.server_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to connect MT5")
    return {"status": "connected", "message": "MT5 connected successfully"}

@router.post("/disconnect")
async def disconnect_mt5(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect from MT5"""
    mt5_service = getattr(request.app.state, "mt5_service", None)
    if not mt5_service:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MT5 service unavailable")
    await mt5_service.disconnect()
    return {"status": "disconnected", "message": "MT5 disconnected successfully"}