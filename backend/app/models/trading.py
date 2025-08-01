"""Trading-related database models"""

from datetime import datetime, time, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time, 
    Numeric, BigInteger, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base

class MT5Account(Base):
    """MetaTrader 5 account configuration"""
    
    __tablename__ = "mt5_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_login = Column(String(20), nullable=False)
    account_password = Column(String(255), nullable=False)  # Encrypted
    server_name = Column(String(100), default="LiteFinance-Demo")
    account_type = Column(String(20), default="demo")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mt5_accounts")

class BotSettings(Base):
    """Trading bot configuration and settings"""
    
    __tablename__ = "bot_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_bot_active = Column(Boolean, default=False)
    risk_percentage = Column(Numeric(5, 2), default=Decimal('2.00'))
    max_daily_trades = Column(Integer, default=10)
    trading_start_time = Column(Time, default=time(0, 0, 0))
    trading_end_time = Column(Time, default=time(23, 59, 59))
    stop_loss_pips = Column(Integer, default=50)
    take_profit_pips = Column(Integer, default=100)
    lot_size = Column(Numeric(4, 2), default=Decimal('0.01'))
    algorithm_type = Column(String(50), default="trend_following")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bot_settings")

class AccountStatus(Base):
    """Account balance and equity tracking"""
    
    __tablename__ = "account_status"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    margin = Column(Numeric(15, 2), default=Decimal('0'))
    free_margin = Column(Numeric(15, 2), default=Decimal('0'))
    margin_level = Column(Numeric(8, 2), default=Decimal('0'))
    profit = Column(Numeric(15, 2), default=Decimal('0'))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="account_status")

class TradingSignal(Base):
    """Trading signals and decisions"""
    
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, CLOSE
    symbol = Column(String(10), default="XAUUSD")
    price = Column(Numeric(10, 5), nullable=False)
    confidence_score = Column(Numeric(5, 2), default=Decimal('0.0'))
    indicators = Column(JSONB)  # Store indicator values as JSON
    algorithm_used = Column(String(50))
    signal_strength = Column(String(20), default="medium")
    is_executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trading_signals")
    trades = relationship("Trade", back_populates="signal")

class Trade(Base):
    """Trade history and execution logs"""
    
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mt5_ticket = Column(BigInteger, unique=True)  # MT5 trade ticket number
    signal_id = Column(Integer, ForeignKey("trading_signals.id"))
    trade_type = Column(String(10), nullable=False)  # BUY, SELL
    symbol = Column(String(10), default="XAUUSD")
    lot_size = Column(Numeric(4, 2), nullable=False)
    open_price = Column(Numeric(10, 5), nullable=False)
    close_price = Column(Numeric(10, 5))
    stop_loss = Column(Numeric(10, 5))
    take_profit = Column(Numeric(10, 5))
    commission = Column(Numeric(10, 2), default=Decimal('0'))
    swap = Column(Numeric(10, 2), default=Decimal('0'))
    profit = Column(Numeric(15, 2), default=Decimal('0'))
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, CANCELLED
    open_time = Column(DateTime, default=datetime.utcnow)
    close_time = Column(DateTime)
    comment = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    signal = relationship("TradingSignal", back_populates="trades")
    sig_gol_entries = relationship("SigGolEntry", back_populates="linked_trade")
    journal_entries = relationship("JournalEntry", back_populates="trade")

class SigGolEntry(Base):
    """Sig Gol journal entries (separate from main journal)"""
    
    __tablename__ = "sig_gol_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    linked_trade_id = Column(Integer, ForeignKey("trades.id"))
    amount = Column(Numeric(15, 2), nullable=False)
    entry_type = Column(String(20), default="installment")
    description = Column(Text)
    installment_number = Column(Integer)
    total_installments = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sig_gol_entries")
    linked_trade = relationship("Trade", back_populates="sig_gol_entries")
    journal_entries = relationship("JournalEntry", back_populates="sig_gol_entry")

class JournalEntry(Base):
    """Main journal entries"""
    
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    sig_gol_entry_id = Column(Integer, ForeignKey("sig_gol_entries.id"))
    debit = Column(Numeric(15, 2), default=Decimal('0'))
    credit = Column(Numeric(15, 2), default=Decimal('0'))
    description = Column(Text, nullable=False)
    entry_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="journal_entries")
    trade = relationship("Trade", back_populates="journal_entries")
    sig_gol_entry = relationship("SigGolEntry", back_populates="journal_entries")

class SystemLog(Base):
    """System logs and error tracking"""
    
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    log_level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    module = Column(String(50))
    message = Column(Text, nullable=False)
    error_details = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="system_logs")

class TelegramNotification(Base):
    """Telegram notifications log"""
    
    __tablename__ = "telegram_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(30))
    chat_id = Column(String(50))
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="telegram_notifications")

class MarketData(Base):
    """Market data cache for quick access"""
    
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), default="XAUUSD")
    bid = Column(Numeric(10, 5), nullable=False)
    ask = Column(Numeric(10, 5), nullable=False)
    spread = Column(Numeric(8, 5))
    volume = Column(BigInteger)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PerformanceMetrics(Base):
    """Performance metrics and statistics"""
    
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    gross_profit = Column(Numeric(15, 2), default=Decimal('0'))
    gross_loss = Column(Numeric(15, 2), default=Decimal('0'))
    net_profit = Column(Numeric(15, 2), default=Decimal('0'))
    win_rate = Column(Numeric(5, 2), default=Decimal('0'))
    max_drawdown = Column(Numeric(5, 2), default=Decimal('0'))
    profit_factor = Column(Numeric(8, 2), default=Decimal('0'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="performance_metrics")