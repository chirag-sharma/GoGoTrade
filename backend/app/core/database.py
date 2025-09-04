"""
Database configuration and connection management.
Handles TimescaleDB connection and Redis connection setup.
"""

import os
from typing import AsyncGenerator, Optional
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import redis.asyncio as redis
from pydantic_settings import BaseSettings

from app.models import Base


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # PostgreSQL/TimescaleDB settings
    DATABASE_URL: str = "postgresql+psycopg://gogotrade:gogotrade@localhost:5432/gogotrade"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_MAX_CONNECTIONS: int = 20
    
    # TimescaleDB specific settings
    TIMESCALEDB_CHUNK_INTERVAL: str = "7 days"  # Chunk interval for hypertables
    TIMESCALEDB_COMPRESSION_INTERVAL: str = "30 days"  # Compression interval
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = DatabaseSettings()

# Database engine (will be initialized on startup)
engine = None
async_session_maker = None

# Redis connection pool (will be initialized on startup)
redis_pool = None


async def init_database():
    """Initialize database connection and Redis pool."""
    global engine, async_session_maker, redis_pool
    
    # Create async database engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=False,  # Set to True for SQL query logging
    )
    
    # Create session maker
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Initialize Redis connection pool
    redis_pool = redis.ConnectionPool.from_url(
        settings.REDIS_URL,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
    )
    
    print("✅ Database connections initialized")


async def close_database():
    """Close database connections and Redis pool."""
    global engine, redis_pool
    
    if engine:
        await engine.dispose()
        print("✅ Database engine disposed")
    
    if redis_pool:
        await redis_pool.disconnect()
        print("✅ Redis connection pool closed")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with automatic cleanup.
    
    Usage:
        async with get_db_session() as db:
            # Use db session
            pass
    """
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """
    Get Redis connection.
    
    Returns:
        Redis connection instance
    """
    if not redis_pool:
        raise RuntimeError("Redis not initialized. Call init_database() first.")
    
    return redis.Redis(connection_pool=redis_pool)


async def create_tables():
    """Create all database tables."""
    if not engine:
        raise RuntimeError("Database engine not initialized")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")


async def setup_timescaledb():
    """
    Setup TimescaleDB specific configurations.
    Creates hypertables and sets up compression policies.
    """
    if not engine:
        raise RuntimeError("Database engine not initialized")
    
    async with engine.begin() as conn:
        # Enable TimescaleDB extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
        
        # Convert ohlcv_data table to hypertable
        await conn.execute(text("""
            SELECT create_hypertable('ohlcv_data', 'timestamp', 
                                   chunk_time_interval => INTERVAL '{chunk_interval}',
                                   if_not_exists => TRUE);
        """.format(chunk_interval=settings.TIMESCALEDB_CHUNK_INTERVAL)))
        
        # Setup compression policy for ohlcv_data
        await conn.execute(text("""
            ALTER TABLE ohlcv_data SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'instrument_id, timeframe'
            );
        """))
        
        await conn.execute(text("""
            SELECT add_compression_policy('ohlcv_data', INTERVAL '{compression_interval}', if_not_exists => TRUE);
        """.format(compression_interval=settings.TIMESCALEDB_COMPRESSION_INTERVAL)))
        
        # Convert trades table to hypertable (using order_timestamp)
        await conn.execute(text("""
            SELECT create_hypertable('trades', 'order_timestamp',
                                   chunk_time_interval => INTERVAL '1 day',
                                   if_not_exists => TRUE);
        """))
        
        # Convert trading_signals table to hypertable
        await conn.execute(text("""
            SELECT create_hypertable('trading_signals', 'generated_at',
                                   chunk_time_interval => INTERVAL '7 days',
                                   if_not_exists => TRUE);
        """))
    
    # Create views and aggregates outside transaction
    # Use autocommit for operations that cannot run in transactions
    async_engine_autocommit = create_async_engine(
        settings.DATABASE_URL + "?autocommit=true",
        pool_size=1,
    )
    
    async with async_engine_autocommit.connect() as conn:
        # Create materialized views for common queries
        await conn.execute(text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS daily_ohlcv AS
            SELECT 
                instrument_id,
                DATE(timestamp) as date,
                first(open, timestamp) as open,
                max(high) as high,
                min(low) as low,
                last(close, timestamp) as close,
                sum(volume) as volume
            FROM ohlcv_data 
            WHERE timeframe = '1d'
            GROUP BY instrument_id, DATE(timestamp)
            ORDER BY instrument_id, date;
        """))
        
        # Create continuous aggregate for real-time 5-minute candles
        await conn.execute(text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_5m
            WITH (timescaledb.continuous) AS
            SELECT 
                time_bucket('5 minutes', timestamp) AS bucket,
                instrument_id,
                first(open, timestamp) as open,
                max(high) as high,
                min(low) as low,
                last(close, timestamp) as close,
                sum(volume) as volume
            FROM ohlcv_data 
            WHERE timeframe = '1m'
            GROUP BY bucket, instrument_id;
        """))
        
        # Add refresh policy for continuous aggregate
        await conn.execute(text("""
            SELECT add_continuous_aggregate_policy('ohlcv_5m',
                start_offset => INTERVAL '1 hour',
                end_offset => INTERVAL '5 minutes',
                schedule_interval => INTERVAL '5 minutes',
                if_not_exists => TRUE);
        """))
    
    await async_engine_autocommit.dispose()
    
    print("✅ TimescaleDB hypertables and policies configured")


class DatabaseManager:
    """Database manager class for handling connections and operations."""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self.redis_pool = None
    
    async def initialize(self):
        """Initialize all database connections."""
        await init_database()
        await create_tables()
        await setup_timescaledb()
        print("✅ Database manager fully initialized")
    
    async def close(self):
        """Close all database connections."""
        await close_database()
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with get_db_session() as session:
            yield session
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        return await get_redis()
    
    async def health_check(self) -> dict:
        """
        Perform health check on all database connections.
        
        Returns:
            Dictionary with health status of all connections
        """
        health_status = {
            "postgresql": False,
            "redis": False,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Check PostgreSQL connection
        try:
            async with get_db_session() as db:
                result = await db.execute("SELECT 1")
                health_status["postgresql"] = result.scalar() == 1
        except Exception as e:
            health_status["postgresql_error"] = str(e)
        
        # Check Redis connection
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            health_status["redis"] = True
            await redis_client.close()
        except Exception as e:
            health_status["redis_error"] = str(e)
        
        return health_status


# Global database manager instance
db_manager = DatabaseManager()
