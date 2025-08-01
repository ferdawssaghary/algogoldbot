"""User model for authentication and user management"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    """User model for authentication"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mt5_accounts = relationship("MT5Account", back_populates="user", cascade="all, delete-orphan")
    bot_settings = relationship("BotSettings", back_populates="user", cascade="all, delete-orphan")
    account_status = relationship("AccountStatus", back_populates="user", cascade="all, delete-orphan")
    trading_signals = relationship("TradingSignal", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    sig_gol_entries = relationship("SigGolEntry", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    system_logs = relationship("SystemLog", back_populates="user", cascade="all, delete-orphan")
    telegram_notifications = relationship("TelegramNotification", back_populates="user", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetrics", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"