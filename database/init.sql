-- Gold Trading Bot Database Schema
-- Created for XAUUSD automated trading system

-- Users table for authentication and account management
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MT5 Account configurations
CREATE TABLE IF NOT EXISTS mt5_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    account_login VARCHAR(20) NOT NULL,
    account_password VARCHAR(255) NOT NULL, -- Encrypted
    server_name VARCHAR(100) DEFAULT 'LiteFinance-Demo',
    account_type VARCHAR(20) DEFAULT 'demo',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading bot configuration and settings
CREATE TABLE IF NOT EXISTS bot_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    is_bot_active BOOLEAN DEFAULT false,
    risk_percentage DECIMAL(5,2) DEFAULT 2.00, -- Risk per trade as percentage
    max_daily_trades INTEGER DEFAULT 10,
    trading_start_time TIME DEFAULT '00:00:00',
    trading_end_time TIME DEFAULT '23:59:59',
    stop_loss_pips INTEGER DEFAULT 50,
    take_profit_pips INTEGER DEFAULT 100,
    lot_size DECIMAL(4,2) DEFAULT 0.01,
    algorithm_type VARCHAR(50) DEFAULT 'trend_following',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account balance and equity tracking
CREATE TABLE IF NOT EXISTS account_status (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    balance DECIMAL(15,2) NOT NULL,
    equity DECIMAL(15,2) NOT NULL,
    margin DECIMAL(15,2) DEFAULT 0,
    free_margin DECIMAL(15,2) DEFAULT 0,
    margin_level DECIMAL(8,2) DEFAULT 0,
    profit DECIMAL(15,2) DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading signals and decisions
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    signal_type VARCHAR(10) CHECK (signal_type IN ('BUY', 'SELL', 'CLOSE')),
    symbol VARCHAR(10) DEFAULT 'XAUUSD',
    price DECIMAL(10,5) NOT NULL,
    confidence_score DECIMAL(5,2) DEFAULT 0.0,
    indicators JSONB, -- Store indicator values as JSON
    algorithm_used VARCHAR(50),
    signal_strength VARCHAR(20) DEFAULT 'medium',
    is_executed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trade history and execution logs
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mt5_ticket BIGINT UNIQUE, -- MT5 trade ticket number
    signal_id INTEGER REFERENCES trading_signals(id),
    trade_type VARCHAR(10) CHECK (trade_type IN ('BUY', 'SELL')),
    symbol VARCHAR(10) DEFAULT 'XAUUSD',
    lot_size DECIMAL(4,2) NOT NULL,
    open_price DECIMAL(10,5) NOT NULL,
    close_price DECIMAL(10,5),
    stop_loss DECIMAL(10,5),
    take_profit DECIMAL(10,5),
    commission DECIMAL(10,2) DEFAULT 0,
    swap DECIMAL(10,2) DEFAULT 0,
    profit DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED')),
    open_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    close_time TIMESTAMP,
    comment TEXT
);

-- Sig Gol journal entries (separate from main journal)
CREATE TABLE IF NOT EXISTS sig_gol_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    linked_trade_id INTEGER REFERENCES trades(id),
    amount DECIMAL(15,2) NOT NULL,
    entry_type VARCHAR(20) DEFAULT 'installment',
    description TEXT,
    installment_number INTEGER,
    total_installments INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main journal entries
CREATE TABLE IF NOT EXISTS journal_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    trade_id INTEGER REFERENCES trades(id),
    sig_gol_entry_id INTEGER REFERENCES sig_gol_entries(id),
    debit DECIMAL(15,2) DEFAULT 0,
    credit DECIMAL(15,2) DEFAULT 0,
    description TEXT NOT NULL,
    entry_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System logs and error tracking
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    log_level VARCHAR(10) CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module VARCHAR(50),
    message TEXT NOT NULL,
    error_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Telegram notifications log
CREATE TABLE IF NOT EXISTS telegram_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    notification_type VARCHAR(30),
    chat_id VARCHAR(50),
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market data cache for quick access
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) DEFAULT 'XAUUSD',
    bid DECIMAL(10,5) NOT NULL,
    ask DECIMAL(10,5) NOT NULL,
    spread DECIMAL(8,5),
    volume BIGINT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics and statistics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    gross_profit DECIMAL(15,2) DEFAULT 0,
    gross_loss DECIMAL(15,2) DEFAULT 0,
    net_profit DECIMAL(15,2) DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    max_drawdown DECIMAL(5,2) DEFAULT 0,
    profit_factor DECIMAL(8,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_open_time ON trades(open_time);
CREATE INDEX IF NOT EXISTS idx_signals_user_id ON trading_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON trading_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_account_status_user_id ON account_status(user_id);
CREATE INDEX IF NOT EXISTS idx_account_status_recorded_at ON account_status(recorded_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- Insert default admin user (password: admin123 - should be changed in production)
INSERT INTO users (username, email, password_hash) VALUES 
('admin', 'admin@goldtrading.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewEF/.QY.H8.h8gO')
ON CONFLICT (username) DO NOTHING;

-- Insert default bot settings for admin user
INSERT INTO bot_settings (user_id, risk_percentage, max_daily_trades, stop_loss_pips, take_profit_pips)
SELECT id, 2.00, 10, 50, 100 FROM users WHERE username = 'admin'
ON CONFLICT DO NOTHING;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mt5_accounts_updated_at BEFORE UPDATE ON mt5_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bot_settings_updated_at BEFORE UPDATE ON bot_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();