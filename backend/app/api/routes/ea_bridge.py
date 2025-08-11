from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

class EASettingsIn(BaseModel):
    enabled: bool
    shared_secret: str

@router.get("/settings")
async def get_ea_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return {
        "enabled": settings.EA_BRIDGE_ENABLED,
        "shared_secret": settings.EA_SHARED_SECRET or ""
    }

@router.post("/settings")
async def save_ea_settings(
    payload: EASettingsIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    settings.EA_BRIDGE_ENABLED = payload.enabled
    settings.EA_SHARED_SECRET = payload.shared_secret
    return {"success": True}