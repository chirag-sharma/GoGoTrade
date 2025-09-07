"""
Database migration script for GoGoTrade platform.
Initializes TimescaleDB with proper schemas and sample data.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import db_manager
from app.models import (
    Instrument, InstrumentType, OHLCVData, Trade, TradingSignal,
    MarketSession, TransactionType, OrderType, OrderStatus, SignalType
)


async def create_sample_instruments() -> list:
    """Create sample Indian stock instruments."""
    
    sample_instruments = [
        {
            "instrument_token": 738561,
            "exchange_token": 2884,
            "tradingsymbol": "RELIANCE",
            "name": "Reliance Industries Limited",
            "last_price": Decimal("2450.75"),
            "tick_size": Decimal("0.05"),
            "lot_size": 1,
            "instrument_type": InstrumentType.EQUITY,
            "segment": "NSE",
            "exchange": "NSE"
        },
        {
            "instrument_token": 60417,
            "exchange_token": 236,
            "tradingsymbol": "INFY",
            "name": "Infosys Limited",
            "last_price": Decimal("1582.30"),
            "tick_size": Decimal("0.05"),
            "lot_size": 1,
            "instrument_type": InstrumentType.EQUITY,
            "segment": "NSE",
            "exchange": "NSE"
        },
        {
            "instrument_token": 81153,
            "exchange_token": 317,
            "tradingsymbol": "TCS",
            "name": "Tata Consultancy Services Limited",
            "last_price": Decimal("3845.60"),
            "tick_size": Decimal("0.05"),
            "lot_size": 1,
            "instrument_type": InstrumentType.EQUITY,
            "segment": "NSE",
            "exchange": "NSE"
        },
        {
            "instrument_token": 70401,
            "exchange_token": 275,
            "tradingsymbol": "HDFCBANK",
            "name": "HDFC Bank Limited",
            "last_price": Decimal("1675.25"),
            "tick_size": Decimal("0.05"),
            "lot_size": 1,
            "instrument_type": InstrumentType.EQUITY,
            "segment": "NSE",
            "exchange": "NSE"
        },
        {
            "instrument_token": 895745,
            "exchange_token": 3499,
            "tradingsymbol": "ITC",
            "name": "ITC Limited",
            "last_price": Decimal("445.80"),
            "tick_size": Decimal("0.05"),
            "lot_size": 1,
            "instrument_type": InstrumentType.EQUITY,
            "segment": "NSE",
            "exchange": "NSE"
        },
        # Futures instruments
        {
            "instrument_token": 8967425,
            "exchange_token": 35029,
            "tradingsymbol": "NIFTY25SEPFUT",
            "name": "NIFTY Sep 2025 Future",
            "last_price": Decimal("19875.50"),
            "expiry": datetime(2025, 9, 26, tzinfo=timezone.utc),
            "tick_size": Decimal("0.05"),
            "lot_size": 25,
            "instrument_type": InstrumentType.FUTURES,
            "segment": "NFO",
            "exchange": "NSE"
        },
        {
            "instrument_token": 8967426,
            "exchange_token": 35030,
            "tradingsymbol": "BANKNIFTY25SEPFUT",
            "name": "BANKNIFTY Sep 2025 Future",
            "last_price": Decimal("45245.75"),
            "expiry": datetime(2025, 9, 26, tzinfo=timezone.utc),
            "tick_size": Decimal("0.05"),
            "lot_size": 15,
            "instrument_type": InstrumentType.FUTURES,
            "segment": "NFO",
            "exchange": "NSE"
        }
    ]
    
    instruments = []
    async with db_manager.get_session() as db:
        for instrument_data in sample_instruments:
            instrument = Instrument(**instrument_data)
            db.add(instrument)
            instruments.append(instrument)
        
        await db.commit()
        print(f"✅ Created {len(instruments)} sample instruments")
    
    return instruments


async def create_sample_ohlcv_data(instruments: list):
    """Create sample OHLCV data for instruments."""
    
    async with db_manager.get_session() as db:
        base_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        for instrument in instruments[:3]:  # Create data for first 3 instruments
            # Generate 24 hours of 1-minute data
            for i in range(1440):  # 24 * 60 minutes
                timestamp = base_time - timedelta(minutes=i)
                
                # Simple price simulation (random walk)
                base_price = float(instrument.last_price)
                price_change = (i % 10 - 5) * 0.5  # Simple oscillation
                
                open_price = base_price + price_change
                high_price = open_price + abs(price_change) * 0.5
                low_price = open_price - abs(price_change) * 0.3
                close_price = open_price + (price_change * 0.8)
                volume = 1000 + (i % 100) * 10
                
                ohlcv = OHLCVData(
                    instrument_id=instrument.id,
                    timestamp=timestamp,
                    timeframe="1m",
                    open=Decimal(str(round(open_price, 2))),
                    high=Decimal(str(round(high_price, 2))),
                    low=Decimal(str(round(low_price, 2))),
                    close=Decimal(str(round(close_price, 2))),
                    volume=volume
                )
                db.add(ohlcv)
            
            # Generate daily data for last 30 days
            for i in range(30):
                timestamp = base_time.replace(hour=9, minute=15) - timedelta(days=i)
                
                base_price = float(instrument.last_price)
                price_change = (i % 20 - 10) * 2  # Larger changes for daily
                
                open_price = base_price + price_change
                high_price = open_price + abs(price_change) * 1.2
                low_price = open_price - abs(price_change) * 0.8
                close_price = open_price + (price_change * 0.9)
                volume = 50000 + (i % 1000) * 100
                
                ohlcv = OHLCVData(
                    instrument_id=instrument.id,
                    timestamp=timestamp,
                    timeframe="1d",
                    open=Decimal(str(round(open_price, 2))),
                    high=Decimal(str(round(high_price, 2))),
                    low=Decimal(str(round(low_price, 2))),
                    close=Decimal(str(round(close_price, 2))),
                    volume=volume
                )
                db.add(ohlcv)
        
        await db.commit()
        print("✅ Created sample OHLCV data for instruments")


async def create_sample_trading_signals(instruments: list):
    """Create sample trading signals."""
    
    signal_strategies = [
        "RSI_MACD_Combined",
        "Bollinger_Band_Breakout", 
        "Moving_Average_Crossover",
        "Support_Resistance_AI",
        "Volume_Price_Analysis"
    ]
    
    async with db_manager.get_session() as db:
        base_time = datetime.now(timezone.utc)
        
        for instrument in instruments[:5]:  # Signals for first 5 instruments
            for i in range(10):  # 10 signals per instrument
                timestamp = base_time - timedelta(hours=i*2)
                
                # Alternate between different signal types
                signal_types = [SignalType.BUY, SignalType.SELL, SignalType.HOLD, 
                              SignalType.STRONG_BUY, SignalType.STRONG_SELL]
                signal_type = signal_types[i % len(signal_types)]
                
                confidence = 0.6 + (i % 4) * 0.1  # Confidence between 0.6 and 0.9
                
                signal = TradingSignal(
                    instrument_id=instrument.id,
                    signal_type=signal_type,
                    confidence_score=Decimal(str(confidence)),
                    target_price=instrument.last_price * Decimal("1.05") if signal_type in [SignalType.BUY, SignalType.STRONG_BUY] 
                                 else instrument.last_price * Decimal("0.95"),
                    stop_loss=instrument.last_price * Decimal("0.98") if signal_type in [SignalType.BUY, SignalType.STRONG_BUY] 
                              else instrument.last_price * Decimal("1.02"),
                    timeframe="1d",
                    strategy_name=signal_strategies[i % len(signal_strategies)],
                    indicators_used=json.dumps({
                        "RSI": 65.5,
                        "MACD": 12.3,
                        "BB_Upper": 2450.0,
                        "BB_Lower": 2380.0,
                        "Volume_Ratio": 1.25
                    }),
                    market_condition="Bull" if i % 3 == 0 else "Bear" if i % 3 == 1 else "Sideways",
                    generated_at=timestamp,
                    expires_at=timestamp + timedelta(days=1),
                    is_active=True
                )
                db.add(signal)
        
        await db.commit()
        print("✅ Created sample trading signals")


async def create_sample_trades(instruments: list):
    """Create sample trade records."""
    
    async with db_manager.get_session() as db:
        base_time = datetime.now(timezone.utc)
        
        for instrument in instruments[:3]:  # Trades for first 3 instruments
            for i in range(5):  # 5 trades per instrument
                timestamp = base_time - timedelta(hours=i*6)
                
                trade = Trade(
                    instrument_id=instrument.id,
                    order_id=f"ORDER_{instrument.tradingsymbol}_{i+1:03d}",
                    exchange_order_id=f"NSE_{timestamp.strftime('%Y%m%d')}_{i+1:06d}",
                    transaction_type=TransactionType.BUY if i % 2 == 0 else TransactionType.SELL,
                    quantity=100 * (i + 1),
                    price=instrument.last_price,
                    order_type=OrderType.LIMIT if i % 3 == 0 else OrderType.MARKET,
                    order_status=OrderStatus.COMPLETE,
                    executed_quantity=100 * (i + 1),
                    pending_quantity=0,
                    cancelled_quantity=0,
                    average_price=instrument.last_price,
                    algo_id=f"ALGO_{i % 3 + 1}",
                    strategy_id=f"STRATEGY_{(i % 2) + 1}",
                    user_id="USER_DEMO_001",
                    order_timestamp=timestamp,
                    exchange_timestamp=timestamp + timedelta(milliseconds=500)
                )
                db.add(trade)
        
        await db.commit()
        print("✅ Created sample trade records")


async def create_market_sessions():
    """Create market session data."""
    
    async with db_manager.get_session() as db:
        base_date = datetime.now(timezone.utc).date()
        
        # Create sessions for last 30 days
        for i in range(30):
            session_date = base_date - timedelta(days=i)
            is_weekend = session_date.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            # NSE Equity session
            nse_session = MarketSession(
                exchange="NSE",
                segment="EQ",
                session_date=datetime.combine(session_date, datetime.min.time(), timezone.utc),
                pre_market_start=datetime.combine(session_date, datetime.strptime("09:00", "%H:%M").time(), timezone.utc),
                market_open=datetime.combine(session_date, datetime.strptime("09:15", "%H:%M").time(), timezone.utc),
                market_close=datetime.combine(session_date, datetime.strptime("15:30", "%H:%M").time(), timezone.utc),
                post_market_end=datetime.combine(session_date, datetime.strptime("16:00", "%H:%M").time(), timezone.utc),
                is_trading_day=not is_weekend,
                is_holiday=is_weekend,
                holiday_reason="Weekend" if is_weekend else None
            )
            db.add(nse_session)
            
            # NSE F&O session
            if not is_weekend:
                nfo_session = MarketSession(
                    exchange="NSE",
                    segment="FO",
                    session_date=datetime.combine(session_date, datetime.min.time(), timezone.utc),
                    market_open=datetime.combine(session_date, datetime.strptime("09:15", "%H:%M").time(), timezone.utc),
                    market_close=datetime.combine(session_date, datetime.strptime("15:30", "%H:%M").time(), timezone.utc),
                    is_trading_day=True,
                    is_holiday=False
                )
                db.add(nfo_session)
        
        await db.commit()
        print("✅ Created market session data")


async def initialize_redis_cache(instruments: list):
    """Initialize Redis cache with instrument data."""
    
    redis_client = await db_manager.get_redis()
    
    try:
        # Cache instrument tokens for quick lookup
        for instrument in instruments:
            key = f"instrument:{instrument.instrument_token}"
            data = {
                "id": str(instrument.id),
                "symbol": instrument.tradingsymbol,
                "name": instrument.name,
                "last_price": str(instrument.last_price),
                "exchange": instrument.exchange,
                "instrument_type": instrument.instrument_type.value
            }
            await redis_client.hmset(key, data)
            await redis_client.expire(key, 86400)  # Expire in 24 hours
        
        # Create reverse lookup (symbol to token)
        for instrument in instruments:
            key = f"symbol:{instrument.tradingsymbol}"
            await redis_client.set(key, instrument.instrument_token)
            await redis_client.expire(key, 86400)
        
        # Cache market status
        await redis_client.set("market:status", "OPEN")
        await redis_client.set("market:last_update", datetime.now(timezone.utc).isoformat())
        
        print("✅ Initialized Redis cache with sample data")
        
    finally:
        await redis_client.close()


async def main():
    """Main migration function."""
    print("🚀 Starting GoGoTrade database migration...")
    
    try:
        # Initialize database connections
        print("📊 Initializing database connections...")
        await db_manager.initialize()
        
        # Create sample data
        print("📈 Creating sample instruments...")
        instruments = await create_sample_instruments()
        
        print("📊 Creating sample OHLCV data...")
        await create_sample_ohlcv_data(instruments)
        
        print("🎯 Creating sample trading signals...")
        await create_sample_trading_signals(instruments)
        
        print("💼 Creating sample trades...")
        await create_sample_trades(instruments)
        
        print("📅 Creating market sessions...")
        await create_market_sessions()
        
        print("🔄 Initializing Redis cache...")
        await initialize_redis_cache(instruments)
        
        # Health check
        print("🔍 Performing health check...")
        health_status = await db_manager.health_check()
        print(f"Database Health: {health_status}")
        
        print("✅ Database migration completed successfully!")
        print("\n📋 Migration Summary:")
        print(f"   • {len(instruments)} instruments created")
        print(f"   • OHLCV data: ~4,320 records per instrument (1m + 1d timeframes)")
        print(f"   • Trading signals: 50 signals across instruments")
        print(f"   • Trade records: 15 sample trades")
        print(f"   • Market sessions: 30 days of session data")
        print(f"   • Redis cache initialized with instrument data")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise e
    
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
