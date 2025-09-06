"""
Enhanced database models for comprehensive NSE securities management.
Adds sector classification, market data, and watchlist functionality.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
import enum

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, 
    Numeric, String, Text, UniqueConstraint, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
import uuid

from . import Base, Instrument


class MarketSegment(str, enum.Enum):
    """Market segments."""
    LARGE_CAP = "LARGE_CAP"
    MID_CAP = "MID_CAP"
    SMALL_CAP = "SMALL_CAP"
    MICRO_CAP = "MICRO_CAP"


class IndustryGroup(str, enum.Enum):
    """Industry groups based on NIFTY sectoral indices."""
    AUTOMOBILE = "AUTOMOBILE"
    BANKING = "BANKING"
    CONSUMER_DURABLES = "CONSUMER_DURABLES"
    CONSUMER_GOODS = "CONSUMER_GOODS"
    ENERGY = "ENERGY"
    FINANCIAL_SERVICES = "FINANCIAL_SERVICES"
    FMCG = "FMCG"
    HEALTHCARE = "HEALTHCARE"
    IT = "IT"
    MEDIA = "MEDIA"
    METALS = "METALS"
    PHARMA = "PHARMA"
    PSU_BANK = "PSU_BANK"
    PRIVATE_BANK = "PRIVATE_BANK"
    REALTY = "REALTY"
    TELECOM = "TELECOM"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    OIL_AND_GAS = "OIL_AND_GAS"
    CHEMICALS = "CHEMICALS"
    TEXTILES = "TEXTILES"
    COMMODITIES = "COMMODITIES"
    OTHER = "OTHER"


class InstrumentExtended(Base):
    """
    Extended instrument information for NSE securities.
    Enhances the base Instrument model with market data and classification.
    """
    __tablename__ = "instruments_extended"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('instruments.id'), nullable=False, unique=True)
    
    # Market Classification
    industry_group = Column(Enum(IndustryGroup), nullable=True)
    sector = Column(String(100), nullable=True)  # More granular than industry_group
    market_segment = Column(Enum(MarketSegment), nullable=True)
    
    # Financial Metrics
    market_cap = Column(BigInteger, nullable=True)  # In INR
    market_cap_category = Column(String(20), nullable=True)  # Large/Mid/Small Cap
    pe_ratio = Column(Numeric(10, 2), nullable=True)
    pb_ratio = Column(Numeric(10, 2), nullable=True)
    dividend_yield = Column(Numeric(5, 2), nullable=True)
    book_value = Column(Numeric(10, 2), nullable=True)
    
    # Trading Metrics
    avg_volume_30d = Column(BigInteger, nullable=True)
    avg_turnover_30d = Column(BigInteger, nullable=True)
    price_52w_high = Column(Numeric(10, 2), nullable=True)
    price_52w_low = Column(Numeric(10, 2), nullable=True)
    beta = Column(Numeric(5, 4), nullable=True)
    
    # Index Memberships (JSON array of index names)
    nifty_indices = Column(JSONB, nullable=True)  # ["NIFTY50", "NIFTY_IT", etc.]
    
    # Metadata
    isin = Column(String(12), nullable=True, unique=True)
    company_id = Column(String(20), nullable=True)  # NSE company ID
    listing_date = Column(DateTime(timezone=True), nullable=True)
    face_value = Column(Numeric(10, 2), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_trading_suspended = Column(Boolean, default=False)
    is_index_stock = Column(Boolean, default=False)
    is_f_and_o = Column(Boolean, default=False)  # Futures & Options available
    
    # Data freshness
    data_last_updated = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship
    instrument = relationship("Instrument", backref="extended_info")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_industry_group', 'industry_group'),
        Index('idx_market_cap', 'market_cap'),
        Index('idx_market_segment', 'market_segment'),
        Index('idx_active_trading', 'is_active', 'is_trading_suspended'),
        Index('idx_f_and_o', 'is_f_and_o'),
    )


class Watchlist(Base):
    """
    User watchlists for favorite instruments.
    """
    __tablename__ = "watchlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # User management (for future multi-user support)
    user_id = Column(String(100), nullable=True, default="default_user")
    
    # Metadata
    is_default = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)  # System-created watchlists
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(Base):
    """
    Items in a watchlist.
    """
    __tablename__ = "watchlist_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watchlist_id = Column(UUID(as_uuid=True), ForeignKey('watchlists.id'), nullable=False)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('instruments.id'), nullable=False)
    
    # Position in watchlist
    sort_order = Column(Integer, default=0)
    
    # User notes
    notes = Column(Text, nullable=True)
    
    # Alerts configuration
    price_alert_high = Column(Numeric(10, 2), nullable=True)
    price_alert_low = Column(Numeric(10, 2), nullable=True)
    volume_alert_threshold = Column(BigInteger, nullable=True)
    
    added_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    instrument = relationship("Instrument")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('watchlist_id', 'instrument_id', name='uq_watchlist_instrument'),
        Index('idx_watchlist_order', 'watchlist_id', 'sort_order'),
    )


class MarketStats(Base):
    """
    Daily market statistics and trending instruments.
    """
    __tablename__ = "market_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('instruments.id'), nullable=False)
    stats_date = Column(DateTime(timezone=True), nullable=False)
    
    # Trading metrics
    volume = Column(BigInteger, nullable=False, default=0)
    turnover = Column(BigInteger, nullable=False, default=0)
    trades_count = Column(Integer, nullable=False, default=0)
    
    # Price metrics
    open_price = Column(Numeric(10, 2), nullable=False)
    high_price = Column(Numeric(10, 2), nullable=False)
    low_price = Column(Numeric(10, 2), nullable=False)
    close_price = Column(Numeric(10, 2), nullable=False)
    
    # Change metrics
    price_change = Column(Numeric(10, 2), nullable=False)
    price_change_percent = Column(Numeric(8, 4), nullable=False)
    
    # Rankings (calculated daily)
    volume_rank = Column(Integer, nullable=True)  # 1 = highest volume
    gainer_rank = Column(Integer, nullable=True)  # 1 = highest gain
    loser_rank = Column(Integer, nullable=True)   # 1 = highest loss
    turnover_rank = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    instrument = relationship("Instrument")
    
    # Indexes for efficient trending queries
    __table_args__ = (
        Index('idx_stats_date', 'stats_date'),
        Index('idx_volume_rank', 'stats_date', 'volume_rank'),
        Index('idx_gainer_rank', 'stats_date', 'gainer_rank'),
        Index('idx_loser_rank', 'stats_date', 'loser_rank'),
        UniqueConstraint('instrument_id', 'stats_date', name='uq_instrument_stats_date'),
    )


class SectorPerformance(Base):
    """
    Sector-wise performance tracking.
    """
    __tablename__ = "sector_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sector_name = Column(String(100), nullable=False)
    industry_group = Column(Enum(IndustryGroup), nullable=True)
    stats_date = Column(DateTime(timezone=True), nullable=False)
    
    # Performance metrics
    total_stocks = Column(Integer, nullable=False)
    gainers_count = Column(Integer, nullable=False, default=0)
    losers_count = Column(Integer, nullable=False, default=0)
    unchanged_count = Column(Integer, nullable=False, default=0)
    
    # Aggregate metrics
    avg_change_percent = Column(Numeric(8, 4), nullable=False)
    total_turnover = Column(BigInteger, nullable=False, default=0)
    market_cap_weighted_return = Column(Numeric(8, 4), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_sector_date', 'stats_date', 'sector_name'),
        Index('idx_industry_date', 'stats_date', 'industry_group'),
    )
