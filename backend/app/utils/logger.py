"""Logging utility for the application"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from app.core.config import settings

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(settings.LOGS_DIR)
    logs_dir.mkdir(exist_ok=True)
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = getattr(logging, (level or settings.LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler for general logs
    general_log_file = logs_dir / "app.log"
    file_handler = RotatingFileHandler(
        general_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = logs_dir / "error.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Trading-specific log handler
    if 'trading' in name.lower() or 'mt5' in name.lower():
        trading_log_file = logs_dir / "trading.log"
        trading_handler = TimedRotatingFileHandler(
            trading_log_file,
            when='midnight',
            interval=1,
            backupCount=30
        )
        trading_handler.setLevel(logging.INFO)
        trading_handler.setFormatter(detailed_formatter)
        logger.addHandler(trading_handler)
    
    return logger

class TradingLogger:
    """Specialized logger for trading events"""
    
    def __init__(self):
        self.logger = setup_logger("trading")
        
    def log_trade_signal(self, signal_type: str, symbol: str, price: float, confidence: float):
        """Log trading signal"""
        self.logger.info(f"SIGNAL: {signal_type} {symbol} @ {price:.5f} (confidence: {confidence:.2f})")
    
    def log_trade_entry(self, trade_type: str, symbol: str, price: float, lot_size: float, sl: float, tp: float):
        """Log trade entry"""
        self.logger.info(f"ENTRY: {trade_type} {lot_size} {symbol} @ {price:.5f} SL:{sl:.5f} TP:{tp:.5f}")
    
    def log_trade_exit(self, symbol: str, price: float, profit: float, reason: str):
        """Log trade exit"""
        self.logger.info(f"EXIT: {symbol} @ {price:.5f} Profit: {profit:.2f} Reason: {reason}")
    
    def log_account_status(self, balance: float, equity: float, margin: float):
        """Log account status"""
        self.logger.info(f"ACCOUNT: Balance: {balance:.2f} Equity: {equity:.2f} Margin: {margin:.2f}")
    
    def log_error(self, operation: str, error: str):
        """Log trading error"""
        self.logger.error(f"TRADING_ERROR: {operation} - {error}")

class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = setup_logger("performance")
        
    def log_api_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Log API request performance"""
        self.logger.info(f"API: {method} {endpoint} - {response_time:.3f}s - {status_code}")
    
    def log_database_query(self, query_type: str, table: str, execution_time: float):
        """Log database query performance"""
        self.logger.info(f"DB: {query_type} {table} - {execution_time:.3f}s")
    
    def log_system_metrics(self, cpu_percent: float, memory_percent: float, disk_usage: float):
        """Log system performance metrics"""
        self.logger.info(f"SYSTEM: CPU: {cpu_percent:.1f}% RAM: {memory_percent:.1f}% Disk: {disk_usage:.1f}%")