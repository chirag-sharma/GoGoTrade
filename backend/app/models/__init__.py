"""
Database models for GoGoTrade platform.
Defines SQLAlchemy models for TimescaleDB time-series data.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, 
    Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


Base = declarative_base()


class InstrumentType(str, enum.Enum):
    """Types of trading instruments."""
    EQUITY = "EQUITY"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"


class OrderType(str, enum.Enum):
    """Types of trading orders."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"


class OrderStatus(str, enum.Enum):
    """Status of trading orders."""
    PENDING = "PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class TransactionType(str, enum.Enum):
    """Transaction types."""
    BUY = "BUY"
    SELL = "SELL"


class SignalType(str, enum.Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


class Instrument(Base):
    """
    Master table for all tradable instruments.
    Contains static instrument information.
    """
    __tablename__ = "instruments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_token = Column(BigInteger, unique=True, nullable=False, index=True)
    exchange_token = Column(BigInteger, nullable=False)
    tradingsymbol = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    last_price = Column(Numeric(10, 2), nullable=True)
    expiry = Column(DateTime(timezone=True), nullable=True)
    strike = Column(Numeric(10, 2), nullable=True)
    tick_size = Column(Numeric(10, 4), nullable=False, default=0.05)
    lot_size = Column(Integer, nullable=False, default=1)
    instrument_type = Column(Enum(InstrumentType), nullable=False)
    segment = Column(String(10), nullable=False)  # NSE, BSE, NFO, etc.
    exchange = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    ohlcv_data = relationship("OHLCVData", back_populates="instrument", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="instrument", cascade="all, delete-orphan")
    signals = relationship("TradingSignal", back_populates="instrument", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Instrument(token={self.instrument_token}, symbol={self.tradingsymbol})>"


class OHLCVData(Base):
    """
    OHLCV (Open, High, Low, Close, Volume) time-series data.
    This will be converted to a TimescaleDB hypertable for efficient time-series queries.
    """
    __tablename__ = "ohlcv_data"
    
    # Composite primary key for TimescaleDB hypertable
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), primary_key=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    timeframe = Column(String(10), primary_key=True)  # 1m, 5m, 15m, 1h, 1d, etc.
    
    # OHLCV data
    open = Column(Numeric(12, 4), nullable=False)
    high = Column(Numeric(12, 4), nullable=False)
    low = Column(Numeric(12, 4), nullable=False)
    close = Column(Numeric(12, 4), nullable=False)
    volume = Column(BigInteger, nullable=False, default=0)
    
    # Additional fields
    open_interest = Column(BigInteger, nullable=True, default=0)
    trades_count = Column(Integer, nullable=True, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    instrument = relationship("Instrument", back_populates="ohlcv_data")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_ohlcv_timestamp', 'timestamp'),
        Index('idx_ohlcv_instrument_time', 'instrument_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<OHLCVData(instrument_id={self.instrument_id}, timestamp={self.timestamp}, close={self.close})>"


class Trade(Base):
    """
    Individual trade records for audit trail and compliance.
    """
    __tablename__ = "trades"
    
    # Composite primary key including order_timestamp for TimescaleDB hypertable
    order_id = Column(String(100), primary_key=True)
    order_timestamp = Column(DateTime(timezone=True), primary_key=True)
    
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False)
    exchange_order_id = Column(String(100), nullable=True)
    
    # Trade details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 4), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    order_status = Column(Enum(OrderStatus), nullable=False)
    
    # Execution details
    executed_quantity = Column(Integer, nullable=False, default=0)
    pending_quantity = Column(Integer, nullable=False, default=0)
    cancelled_quantity = Column(Integer, nullable=False, default=0)
    average_price = Column(Numeric(12, 4), nullable=True)
    
    # Compliance fields (SEBI requirements)
    algo_id = Column(String(50), nullable=True)  # Algorithm identifier
    strategy_id = Column(String(50), nullable=True)  # Strategy identifier
    user_id = Column(String(50), nullable=False)  # User/client identifier
    
    # Timestamps
    exchange_timestamp = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    instrument = relationship("Instrument", back_populates="trades")
    
    # Indexes
    __table_args__ = (
        Index('idx_trades_timestamp', 'order_timestamp'),
        Index('idx_trades_instrument_time', 'instrument_id', 'order_timestamp'),
        Index('idx_trades_user_time', 'user_id', 'order_timestamp'),
        Index('idx_trades_algo_strategy', 'algo_id', 'strategy_id'),
    )
    
    def __repr__(self):
        return f"<Trade(order_id={self.order_id}, {self.transaction_type}, qty={self.quantity}, price={self.price})>"


class TradingSignal(Base):
    """
    AI-generated trading signals and recommendations.
    """
    __tablename__ = "trading_signals"
    
    # Composite primary key including generated_at for TimescaleDB hypertable
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), primary_key=True)
    generated_at = Column(DateTime(timezone=True), primary_key=True)
    strategy_name = Column(String(100), primary_key=True)
    
    # Signal details
    signal_type = Column(Enum(SignalType), nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)  # 0.0 to 1.0
    target_price = Column(Numeric(12, 4), nullable=True)
    stop_loss = Column(Numeric(12, 4), nullable=True)
    timeframe = Column(String(10), nullable=False)  # Signal timeframe
    
    # Strategy information
    indicators_used = Column(Text, nullable=True)  # JSON string of indicators
    market_condition = Column(String(50), nullable=True)  # Bull, Bear, Sideways
    
    # Signal metadata
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    instrument = relationship("Instrument", back_populates="signals")
    
    # Indexes
    __table_args__ = (
        Index('idx_signals_timestamp', 'generated_at'),
        Index('idx_signals_active_time', 'is_active', 'generated_at'),
        Index('idx_signals_timeframe', 'timeframe', 'generated_at'),
    )
    
    def __repr__(self):
        return f"<TradingSignal(instrument_id={self.instrument_id}, {self.signal_type}, confidence={self.confidence_score})>"


class MarketSession(Base):
    """
    Track market sessions and trading hours for different exchanges.
    """
    __tablename__ = "market_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange = Column(String(10), nullable=False)
    segment = Column(String(10), nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    
    # Session timings
    pre_market_start = Column(DateTime(timezone=True), nullable=True)
    market_open = Column(DateTime(timezone=True), nullable=False)
    market_close = Column(DateTime(timezone=True), nullable=False)
    post_market_end = Column(DateTime(timezone=True), nullable=True)
    
    # Session status
    is_trading_day = Column(Boolean, default=True, nullable=False)
    is_holiday = Column(Boolean, default=False, nullable=False)
    holiday_reason = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (
        Index('idx_market_sessions_exchange_date', 'exchange', 'session_date'),
        UniqueConstraint('exchange', 'segment', 'session_date', 
                        name='uq_market_session_exchange_segment_date'),
    )
    
    def __repr__(self):
        return f"<MarketSession(exchange={self.exchange}, date={self.session_date}, trading={self.is_trading_day})>"


# Export all models
__all__ = [
    "Base",
    "InstrumentType", 
    "OrderType", 
    "OrderStatus", 
    "TransactionType", 
    "SignalType",
    "Instrument", 
    "OHLCVData", 
    "Trade", 
    "TradingSignal", 
    "MarketSession"
]
