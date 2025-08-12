"""Application configuration settings"""

import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "Gold Trading Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "postgresql://goldtrader:securepassword123@postgres:5432/gold_trading_bot"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Security settings
    SECRET_KEY: str = "your-super-secure-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MetaTrader 5 settings
    MT5_SERVER: str = "LiteFinance-Demo"
    MT5_LOGIN: Optional[str] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_PATH: Optional[str] = None
    MT5_TIMEOUT: int = 60000
    
    # Trading settings
    DEFAULT_SYMBOL: str = "XAUUSD"
    DEFAULT_LOT_SIZE: float = 0.01
    DEFAULT_STOP_LOSS: int = 50
    DEFAULT_TAKE_PROFIT: int = 100
    MAX_SPREAD: float = 5.0
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = "8348419204:AAEEr0DQfcBmwwWssvTu-ljg94C19qUPim8"
    TELEGRAM_CHAT_ID: str = "-1002481438774"
    TELEGRAM_ENABLED: bool = True
    
    # EA Bridge settings
    EA_BRIDGE_ENABLED: bool = False
    EA_SHARED_SECRET: Optional[str] = None
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://frontend:3000", "*"]
    
    # Redis settings (for caching and background tasks)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    MT5_DATA_DIR: str = os.path.join(BASE_DIR, "mt5_data")
    
    # API settings
    API_V1_STR: str = "/api"
    
    # Email settings (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Trading algorithm settings
    ALGORITHM_TYPE: str = "trend_following"
    RISK_PERCENTAGE: float = 2.0
    MAX_DAILY_TRADES: int = 10
    TRADING_START_TIME: str = "00:00:00"
    TRADING_END_TIME: str = "23:59:59"
    
    # Performance settings
    ENABLE_METRICS: bool = True
    METRICS_INTERVAL: int = 60  # seconds
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()