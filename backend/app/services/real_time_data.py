"""
Real-time market data integration service.
Handles live data feeds, WebSocket connections, and real-time price updates.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Set, Callable
import websockets
import aiohttp
import yfinance as yf
import pandas as pd
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import get_db_session, get_redis
from app.models import Instrument, OHLCVData, TradingSignal
from app.services.market_data_processor import MarketDataProcessor
from app.services.yahoo_finance_service import yahoo_finance_service


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealTimeDataConfig:
    """Configuration for real-time data feeds."""
    
    # Yahoo Finance settings
    UPDATE_INTERVAL = 30  # seconds (Yahoo Finance rate limit consideration)
    BATCH_SIZE = 10  # symbols per batch request
    
    # Redis keys
    LIVE_PRICES_KEY = "live_prices"
    MARKET_DEPTH_KEY = "market_depth"
    SIGNALS_KEY = "trading_signals"
    
    # Update intervals
    PRICE_UPDATE_INTERVAL = 30  # seconds (respecting Yahoo Finance limits)
    CANDLE_UPDATE_INTERVAL = 300  # 5 minutes
    SIGNAL_UPDATE_INTERVAL = 300  # 5 minutes


class RealTimeDataIntegration:
    """
    Real-time market data integration service.
    Manages multiple data sources and real-time updates.
    """
    
    def __init__(self):
        self.config = RealTimeDataConfig()
        self.active_subscriptions: Set[str] = set()
        self.price_callbacks: List[Callable] = []
        self.data_processor = MarketDataProcessor()
        self.is_running = False
        
        # Connection managers
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # Data buffers
        self.price_buffer: Dict[str, Dict] = {}
        self.candle_buffer: Dict[str, List] = {}
        
    async def initialize(self):
        """Initialize the real-time data service."""
        logger.info("Initializing real-time data integration...")
        
        # Initialize HTTP session
        self.http_session = aiohttp.ClientSession()
        
        # Initialize data processor
        await self.data_processor.initialize()
        
        # Start background tasks
        asyncio.create_task(self._price_update_worker())
        asyncio.create_task(self._fetch_historical_data_worker())
        asyncio.create_task(self._signal_update_worker())
        
        self.is_running = True
        logger.info("✅ Real-time data integration initialized")
    
    async def close(self):
        """Clean up resources."""
        self.is_running = False
        
        # Close WebSocket connections
        for ws in self.websocket_connections.values():
            await ws.close()
        
        # Close HTTP session
        if self.http_session:
            await self.http_session.close()
        
        # Cleanup Yahoo Finance service
        await yahoo_finance_service.cleanup()
        
        logger.info("✅ Real-time data integration closed")
    
    async def subscribe_to_live_prices(self, symbols: List[str]) -> bool:
        """
        Subscribe to live price feeds for given symbols.
        
        Args:
            symbols: List of trading symbols to subscribe
            
        Returns:
            True if subscription successful
        """
        try:
            logger.info(f"Subscribing to live prices for {len(symbols)} symbols using Yahoo Finance")
            
            # Add to active subscriptions
            self.active_subscriptions.update(symbols)
            
            # Start Yahoo Finance data fetching
            await self._start_yahoo_finance_feed(symbols)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to live prices: {e}")
            return False
    
    async def unsubscribe_from_live_prices(self, symbols: List[str]) -> bool:
        """
        Unsubscribe from live price feeds.
        
        Args:
            symbols: List of symbols to unsubscribe
            
        Returns:
            True if unsubscription successful
        """
        try:
            # Remove from active subscriptions
            self.active_subscriptions.difference_update(symbols)
            
            # TODO: Send unsubscribe messages to WebSocket connections
            logger.info(f"Unsubscribed from {len(symbols)} symbols")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}")
            return False
    
    async def get_live_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current live price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with price data or None
        """
        try:
            redis_client = await get_redis()
            price_data = await redis_client.hget(
                self.config.LIVE_PRICES_KEY, 
                symbol
            )
            
            if price_data:
                return json.loads(price_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get live price for {symbol}: {e}")
            return None
    
    async def store_live_price(self, symbol: str, price_data: Dict):
        """
        Store live price data in Redis and trigger callbacks.
        
        Args:
            symbol: Trading symbol
            price_data: Price information
        """
        try:
            # Add timestamp
            price_data['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            # Store in Redis
            redis_client = await get_redis()
            await redis_client.hset(
                self.config.LIVE_PRICES_KEY,
                symbol,
                json.dumps(price_data, default=str)
            )
            
            # Set TTL for live data
            await redis_client.expire(self.config.LIVE_PRICES_KEY, 300)
            
            # Store in buffer for batch processing
            self.price_buffer[symbol] = price_data
            
            # Trigger callbacks
            for callback in self.price_callbacks:
                asyncio.create_task(callback(symbol, price_data))
                
        except Exception as e:
            logger.error(f"Failed to store live price: {e}")
    
    async def store_ohlcv_data(self, symbol: str, timeframe: str, ohlcv: Dict):
        """
        Store OHLCV candle data in database.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1m, 5m, etc.)
            ohlcv: OHLCV data dictionary
        """
        try:
            async with get_db_session() as db:
                # Get instrument ID
                instrument = await db.execute(
                    select(Instrument).where(Instrument.tradingsymbol == symbol)
                )
                instrument = instrument.scalar_one_or_none()
                
                if not instrument:
                    logger.warning(f"Instrument not found: {symbol}")
                    return
                
                # Prepare OHLCV data
                ohlcv_record = OHLCVData(
                    instrument_id=instrument.id,
                    timestamp=datetime.fromisoformat(ohlcv['timestamp']),
                    timeframe=timeframe,
                    open=Decimal(str(ohlcv['open'])),
                    high=Decimal(str(ohlcv['high'])),
                    low=Decimal(str(ohlcv['low'])),
                    close=Decimal(str(ohlcv['close'])),
                    volume=int(ohlcv.get('volume', 0)),
                    trades_count=int(ohlcv.get('trades_count', 0))
                )
                
                # Use upsert to handle duplicates
                stmt = pg_insert(OHLCVData).values(
                    instrument_id=ohlcv_record.instrument_id,
                    timestamp=ohlcv_record.timestamp,
                    timeframe=ohlcv_record.timeframe,
                    open=ohlcv_record.open,
                    high=ohlcv_record.high,
                    low=ohlcv_record.low,
                    close=ohlcv_record.close,
                    volume=ohlcv_record.volume,
                    trades_count=ohlcv_record.trades_count
                )
                
                stmt = stmt.on_conflict_do_update(
                    index_elements=['instrument_id', 'timestamp', 'timeframe'],
                    set_=dict(
                        open=stmt.excluded.open,
                        high=stmt.excluded.high,
                        low=stmt.excluded.low,
                        close=stmt.excluded.close,
                        volume=stmt.excluded.volume,
                        trades_count=stmt.excluded.trades_count
                    )
                )
                
                await db.execute(stmt)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store OHLCV data: {e}")
    
    async def _start_yahoo_finance_feed(self, symbols: List[str]):
        """Start Yahoo Finance data feed."""
        try:
            logger.info("Starting Yahoo Finance data feed...")
            
            async def yahoo_finance_worker():
                """Yahoo Finance data fetching worker."""
                while self.is_running:
                    try:
                        # Get active symbols to fetch
                        active_symbols = list(self.active_subscriptions)
                        if not active_symbols:
                            await asyncio.sleep(10)
                            continue
                        
                        # Process symbols in batches to respect rate limits
                        for i in range(0, len(active_symbols), self.config.BATCH_SIZE):
                            batch = active_symbols[i:i + self.config.BATCH_SIZE]
                            
                            # Fetch live prices for batch
                            prices_data = await yahoo_finance_service.get_multiple_live_prices(batch)
                            
                            # Update prices for each symbol in batch
                            for symbol, price_data in prices_data.items():
                                if symbol in self.active_subscriptions:
                                    await self.store_live_price(symbol, price_data)
                            
                            # Small delay between batches
                            await asyncio.sleep(2)
                        
                        # Wait before next update cycle
                        await asyncio.sleep(self.config.UPDATE_INTERVAL)
                        
                    except Exception as e:
                        logger.error(f"Yahoo Finance worker error: {e}")
                        await asyncio.sleep(30)  # Wait longer on error
            
            # Start the worker
            asyncio.create_task(yahoo_finance_worker())
            
        except Exception as e:
            logger.error(f"Failed to start Yahoo Finance feed: {e}")
    
    async def _fetch_historical_data_worker(self):
        """Background worker to fetch and store historical OHLCV data."""
        while self.is_running:
            try:
                # Get active symbols
                active_symbols = list(self.active_subscriptions)
                
                for symbol in active_symbols:
                    try:
                        # Fetch 1-minute data for the current day
                        historical_data = await yahoo_finance_service.get_historical_data(
                            symbol, 
                            period="1d", 
                            interval="1m"
                        )
                        
                        if historical_data:
                            # Store the latest few candles
                            for candle in historical_data[-5:]:  # Store last 5 candles
                                await self.store_ohlcv_data(symbol, '1m', candle)
                        
                        # Small delay between symbols
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch historical data for {symbol}: {e}")
                
                # Wait before next cycle (fetch historical data less frequently)
                await asyncio.sleep(self.config.CANDLE_UPDATE_INTERVAL)
                
            except Exception as e:
                logger.error(f"Historical data worker error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _price_update_worker(self):
        """Background worker for processing price updates."""
        while self.is_running:
            try:
                if self.price_buffer:
                    # Process buffered price updates
                    buffer_copy = self.price_buffer.copy()
                    self.price_buffer.clear()
                    
                    # Update last prices in instruments table
                    await self._update_instrument_prices(buffer_copy)
                    
            except Exception as e:
                logger.error(f"Price update worker error: {e}")
            
            await asyncio.sleep(self.config.PRICE_UPDATE_INTERVAL)
    
    async def _signal_update_worker(self):
        """Background worker for generating trading signals."""
        while self.is_running:
            try:
                # Generate signals for active symbols
                await self._generate_trading_signals()
                
            except Exception as e:
                logger.error(f"Signal update worker error: {e}")
            
            await asyncio.sleep(self.config.SIGNAL_UPDATE_INTERVAL)
    
    async def _update_instrument_prices(self, price_data: Dict[str, Dict]):
        """Update last prices in instruments table."""
        try:
            async with get_db_session() as db:
                for symbol, data in price_data.items():
                    await db.execute(
                        update(Instrument)
                        .where(Instrument.tradingsymbol == symbol)
                        .values(last_price=Decimal(str(data['ltp'])))
                    )
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update instrument prices: {e}")
    
    async def _generate_trading_signals(self):
        """Generate trading signals based on real-time data."""
        try:
            redis_client = await get_redis()
            
            # Get all live prices
            price_data = await redis_client.hgetall(self.config.LIVE_PRICES_KEY)
            
            for symbol, price_json in price_data.items():
                price_info = json.loads(price_json)
                
                # Generate signal using the data processor
                signal = await self.data_processor.generate_signal(symbol, price_info)
                
                if signal:
                    # Store signal in Redis
                    signal_key = f"{self.config.SIGNALS_KEY}:{symbol}"
                    await redis_client.set(
                        signal_key,
                        json.dumps(signal, default=str),
                        ex=300  # 5-minute expiry
                    )
                    
                    logger.info(f"Generated signal for {symbol}: {signal['signal_type']}")
            
        except Exception as e:
            logger.error(f"Failed to generate trading signals: {e}")
    
    def add_price_callback(self, callback: Callable):
        """Add callback function for price updates."""
        self.price_callbacks.append(callback)
    
    def remove_price_callback(self, callback: Callable):
        """Remove price update callback."""
        if callback in self.price_callbacks:
            self.price_callbacks.remove(callback)


# Global real-time data service instance
real_time_data_service = RealTimeDataIntegration()


@asynccontextmanager
async def get_real_time_service():
    """Get the real-time data service."""
    if not real_time_data_service.is_running:
        await real_time_data_service.initialize()
    
    try:
        yield real_time_data_service
    finally:
        pass  # Keep service running


async def start_real_time_data_service():
    """Start the real-time data service."""
    await real_time_data_service.initialize()
    logger.info("🚀 Real-time data service started")


async def stop_real_time_data_service():
    """Stop the real-time data service."""
    await real_time_data_service.close()
    logger.info("🛑 Real-time data service stopped")
