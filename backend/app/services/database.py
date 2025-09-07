"""
Database service layer for GoGoTrade.
Provides high-level database operations for instruments, OHLCV data, and signals.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
import uuid

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session, get_redis
from app.models import (
    Instrument, InstrumentType, OHLCVData, Trade, TradingSignal,
    MarketSession, TransactionType, OrderType, OrderStatus, SignalType
)


class InstrumentService:
    """Service for managing instrument data."""
    
    @staticmethod
    async def get_instrument_by_token(instrument_token: int) -> Optional[Instrument]:
        """Get instrument by token."""
        async with get_db_session() as db:
            result = await db.execute(
                select(Instrument).where(Instrument.instrument_token == instrument_token)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_instrument_by_symbol(symbol: str) -> Optional[Instrument]:
        """Get instrument by trading symbol."""
        async with get_db_session() as db:
            result = await db.execute(
                select(Instrument).where(Instrument.tradingsymbol == symbol)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def list_instruments(
        exchange: Optional[str] = None, 
        instrument_type: Optional[InstrumentType] = None,
        limit: int = 100
    ) -> List[Instrument]:
        """List instruments with optional filters."""
        async with get_db_session() as db:
            query = select(Instrument)
            
            if exchange:
                query = query.where(Instrument.exchange == exchange)
            if instrument_type:
                query = query.where(Instrument.instrument_type == instrument_type)
            
            query = query.limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def create_instrument(instrument_data: Dict[str, Any]) -> Instrument:
        """Create a new instrument."""
        async with get_db_session() as db:
            instrument = Instrument(**instrument_data)
            db.add(instrument)
            await db.commit()
            await db.refresh(instrument)
            return instrument


class OHLCVService:
    """Service for managing OHLCV time-series data."""
    
    @staticmethod
    async def get_ohlcv_data(
        instrument_id: uuid.UUID,
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[OHLCVData]:
        """Get OHLCV data for an instrument."""
        async with get_db_session() as db:
            query = select(OHLCVData).where(
                and_(
                    OHLCVData.instrument_id == instrument_id,
                    OHLCVData.timeframe == timeframe
                )
            )
            
            if start_time:
                query = query.where(OHLCVData.timestamp >= start_time)
            if end_time:
                query = query.where(OHLCVData.timestamp <= end_time)
            
            query = query.order_by(desc(OHLCVData.timestamp)).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def get_latest_price(instrument_id: uuid.UUID) -> Optional[Decimal]:
        """Get latest close price for an instrument."""
        async with get_db_session() as db:
            result = await db.execute(
                select(OHLCVData.close)
                .where(OHLCVData.instrument_id == instrument_id)
                .order_by(desc(OHLCVData.timestamp))
                .limit(1)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def add_ohlcv_data(ohlcv_data: List[Dict[str, Any]]) -> int:
        """Bulk insert OHLCV data."""
        async with get_db_session() as db:
            ohlcv_records = [OHLCVData(**data) for data in ohlcv_data]
            db.add_all(ohlcv_records)
            await db.commit()
            return len(ohlcv_records)


class TradingSignalService:
    """Service for managing trading signals."""
    
    @staticmethod
    async def get_active_signals(
        instrument_id: Optional[uuid.UUID] = None,
        signal_type: Optional[SignalType] = None,
        min_confidence: Optional[float] = None
    ) -> List[TradingSignal]:
        """Get active trading signals."""
        async with get_db_session() as db:
            query = select(TradingSignal).where(TradingSignal.is_active == True)
            
            if instrument_id:
                query = query.where(TradingSignal.instrument_id == instrument_id)
            if signal_type:
                query = query.where(TradingSignal.signal_type == signal_type)
            if min_confidence:
                query = query.where(TradingSignal.confidence_score >= min_confidence)
            
            query = query.order_by(desc(TradingSignal.generated_at))
            result = await db.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def create_signal(signal_data: Dict[str, Any]) -> TradingSignal:
        """Create a new trading signal."""
        async with get_db_session() as db:
            signal = TradingSignal(**signal_data)
            db.add(signal)
            await db.commit()
            await db.refresh(signal)
            return signal


class TradeService:
    """Service for managing trade records."""
    
    @staticmethod
    async def get_trades(
        instrument_id: Optional[uuid.UUID] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Trade]:
        """Get trade records with filters."""
        async with get_db_session() as db:
            query = select(Trade)
            
            if instrument_id:
                query = query.where(Trade.instrument_id == instrument_id)
            if user_id:
                query = query.where(Trade.user_id == user_id)
            if start_time:
                query = query.where(Trade.order_timestamp >= start_time)
            if end_time:
                query = query.where(Trade.order_timestamp <= end_time)
            
            query = query.order_by(desc(Trade.order_timestamp)).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def create_trade(trade_data: Dict[str, Any]) -> Trade:
        """Create a new trade record."""
        async with get_db_session() as db:
            trade = Trade(**trade_data)
            db.add(trade)
            await db.commit()
            await db.refresh(trade)
            return trade


class CacheService:
    """Service for Redis caching operations."""
    
    @staticmethod
    async def cache_instrument_data(instrument: Instrument, ttl: int = 3600):
        """Cache instrument data in Redis."""
        try:
            redis_client = await get_redis()
            
            key = f"instrument:{instrument.instrument_token}"
            data = {
                "id": str(instrument.id),
                "symbol": instrument.tradingsymbol,
                "name": instrument.name,
                "last_price": str(instrument.last_price or "0"),
                "exchange": instrument.exchange,
                "instrument_type": instrument.instrument_type.value
            }
            
            await redis_client.hmset(key, data)
            await redis_client.expire(key, ttl)
            
            # Create reverse lookup
            symbol_key = f"symbol:{instrument.tradingsymbol}"
            await redis_client.set(symbol_key, str(instrument.instrument_token))
            await redis_client.expire(symbol_key, ttl)
            
            await redis_client.close()
        except Exception as e:
            print(f"Cache error: {e}")
    
    @staticmethod
    async def get_cached_instrument(symbol: str) -> Optional[Dict[str, str]]:
        """Get cached instrument data."""
        try:
            redis_client = await get_redis()
            
            # First get token from symbol
            token = await redis_client.get(f"symbol:{symbol}")
            if not token:
                await redis_client.close()
                return None
            
            # Then get instrument data
            data = await redis_client.hgetall(f"instrument:{token}")
            await redis_client.close()
            
            return data if data else None
        except Exception as e:
            print(f"Cache error: {e}")
            return None
    
    @staticmethod
    async def cache_market_status(status: str, ttl: int = 300):
        """Cache market status."""
        try:
            redis_client = await get_redis()
            await redis_client.set("market:status", status)
            await redis_client.set("market:last_update", datetime.now(timezone.utc).isoformat())
            await redis_client.expire("market:status", ttl)
            await redis_client.expire("market:last_update", ttl)
            await redis_client.close()
        except Exception as e:
            print(f"Cache error: {e}")


class AnalyticsService:
    """Service for analytics and market insights."""
    
    @staticmethod
    async def get_market_summary() -> Dict[str, Any]:
        """Get market summary statistics."""
        async with get_db_session() as db:
            # Total instruments
            instruments_count = await db.execute(
                select(func.count(Instrument.id))
            )
            
            # Active signals count
            signals_count = await db.execute(
                select(func.count(TradingSignal.id))
                .where(TradingSignal.is_active == True)
            )
            
            # Recent trades count (last 24 hours)
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            trades_count = await db.execute(
                select(func.count(Trade.id))
                .where(Trade.order_timestamp >= yesterday)
            )
            
            return {
                "total_instruments": instruments_count.scalar(),
                "active_signals": signals_count.scalar(),
                "recent_trades_24h": trades_count.scalar(),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    async def get_top_signals(limit: int = 10) -> List[Dict[str, Any]]:
        """Get top trading signals by confidence."""
        async with get_db_session() as db:
            result = await db.execute(
                select(TradingSignal, Instrument)
                .join(Instrument)
                .where(TradingSignal.is_active == True)
                .order_by(desc(TradingSignal.confidence_score))
                .limit(limit)
            )
            
            signals = []
            for signal, instrument in result:
                signals.append({
                    "symbol": instrument.tradingsymbol,
                    "signal_type": signal.signal_type.value,
                    "confidence": float(signal.confidence_score),
                    "strategy": signal.strategy_name,
                    "target_price": float(signal.target_price or 0),
                    "generated_at": signal.generated_at.isoformat()
                })
            
            return signals


# Export services
__all__ = [
    "InstrumentService",
    "OHLCVService", 
    "TradingSignalService",
    "TradeService",
    "CacheService",
    "AnalyticsService"
]
