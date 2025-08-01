"""CRUD operations for user management"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.core.security import get_password_hash, verify_password

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, username: str, email: str, password: str) -> User:
    """Create new user"""
    hashed_password = get_password_hash(password)
    
    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

async def update_user(
    db: AsyncSession, 
    user_id: int, 
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[User]:
    """Update user information"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if password is not None:
        user.password_hash = get_password_hash(password)
    if is_active is not None:
        user.is_active = is_active
    
    await db.commit()
    await db.refresh(user)
    
    return user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    
    return True

async def get_user_with_settings(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user with all related settings loaded"""
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.mt5_accounts),
            selectinload(User.bot_settings)
        )
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()