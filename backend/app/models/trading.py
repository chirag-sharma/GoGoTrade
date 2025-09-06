"""
Database models for GoGoTrade application
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Numeric, BigInteger, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class OHLCVData(Base):
    """
    OHLCV (Open, High, Low, Close, Volume) data table
    TimescaleDB hypertable for efficient time-series storage
    """
    __tablename__ = 'ohlcv_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 15m, 1h, 1d

    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<OHLCVData(symbol='{self.symbol}', timestamp='{self.timestamp}', close={self.close})>"


class AISignal(Base):
    """
    AI-generated trading signals
    """
    __tablename__ = 'ai_signals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    symbol = Column(String(50), nullable=False, index=True)

    signal_type = Column(String(10), nullable=False)  # BUY, SELL, HOLD, WATCH
    confidence = Column(Numeric(5, 2), nullable=False)  # 0.00 to 100.00

    current_price = Column(Numeric(10, 2), nullable=False)
    target_price = Column(Numeric(10, 2), nullable=True)
    stop_loss = Column(Numeric(10, 2), nullable=True)

    reasoning = Column(Text, nullable=True)
    pattern_type = Column(String(50), nullable=True)

    # Technical indicators values at signal generation
    rsi = Column(Numeric(5, 2), nullable=True)
    macd_signal = Column(String(20), nullable=True)
    sma_20 = Column(Numeric(10, 2), nullable=True)
    sma_50 = Column(Numeric(10, 2), nullable=True)

    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<AISignal(symbol='{self.symbol}', signal='{self.signal_type}', confidence={self.confidence})>"


class BacktestResult(Base):
    """
    Backtesting results storage
    """
    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    strategy_name = Column(String(100), nullable=False)
    symbol = Column(String(50), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    initial_capital = Column(Numeric(15, 2), nullable=False)
    final_capital = Column(Numeric(15, 2), nullable=False)
    total_return = Column(Numeric(10, 4), nullable=False)  # Percentage
    annualized_return = Column(Numeric(10, 4), nullable=False)

    volatility = Column(Numeric(10, 4), nullable=False)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    sortino_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=False)

    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)
    win_rate = Column(Numeric(5, 2), nullable=False, default=0)

    # Strategy parameters (JSON stored as text)
    strategy_params = Column(Text, nullable=True)

    def __repr__(self):
        return f"<BacktestResult(strategy='{self.strategy_name}', symbol='{self.symbol}', return={self.total_return}%)>"


class TradingSession(Base):
    """
    Trading session tracking for compliance and audit
    """
    __tablename__ = 'trading_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False)

    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)

    session_type = Column(String(20), nullable=False)  # LIVE, PAPER, BACKTEST
    mode = Column(String(20), nullable=False)  # MANUAL, AUTO, MIXED

    total_trades = Column(Integer, default=0)
    total_pnl = Column(Numeric(15, 2), default=0)

    # Compliance tracking
    algo_order_tag = Column(String(50), nullable=True)
    compliance_status = Column(String(20), default='PENDING')  # PENDING, APPROVED, REJECTED

    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<TradingSession(id='{self.session_id}', type='{self.session_type}', trades={self.total_trades})>"
