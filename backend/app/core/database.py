"""Database configuration and session management"""

import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    poolclass=NullPool,  # Use NullPool for better compatibility with async
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create declarative base
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables with retry until Postgres is ready"""
    # Import models inside function to avoid circulars
    from app.models.user import User  # noqa: F401
    from app.models.trading import (  # noqa: F401
        MT5Account, BotSettings, AccountStatus, TradingSignal,
        Trade, SigGolEntry, JournalEntry, SystemLog,
        TelegramNotification, MarketData, PerformanceMetrics
    )
    from app.core.security import get_password_hash
    
    last_err = None
    for attempt in range(1, 11):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully")
            # Seed default admin if missing
            async with AsyncSessionLocal() as s:
                from sqlalchemy import select, func
                res = await s.execute(select(User).where(User.username == 'admin'))
                admin = res.scalar_one_or_none()
                if admin is None:
                    u = User(username='admin', email='admin@goldtrading.com', password_hash=get_password_hash('admin123'), is_active=True)
                    s.add(u)
                    await s.commit()
                    # create default bot settings
                    res2 = await s.execute(select(User).where(User.username == 'admin'))
                    admin2 = res2.scalar_one_or_none()
                    if admin2:
                        from app.models.trading import BotSettings
                        s.add(BotSettings(user_id=admin2.id))
                        await s.commit()
            return
        except Exception as e:
            last_err = e
            print(f"Database not ready (attempt {attempt}/10): {e}")
            await asyncio.sleep(3)
    # If we get here, retries exhausted
    raise RuntimeError(f"Failed to initialize database after retries: {last_err}")

async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()