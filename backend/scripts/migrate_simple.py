"""
Simplified migration script that directly connects to database.
Bypasses configuration issues for initial setup.
"""

import asyncio
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Set up simplified database URL
DATABASE_URL = "postgresql+psycopg://gogotrade:SecurePassword123!@localhost:5432/gogotrade"

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Import models
from app.models import Base
from app.models.market_data import (
    InstrumentExtended, Watchlist, WatchlistItem, 
    MarketStats, SectorPerformance
)


class SimpleDatabaseManager:
    """Simple database manager for migration."""
    
    def __init__(self):
        self.engine = None
        self.async_session_maker = None
    
    async def initialize(self):
        """Initialize database connection."""
        self.engine = create_async_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False
        )
        
        self.async_session_maker = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def get_session(self):
        """Get database session."""
        return self.async_session_maker()
    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()


async def migrate_database():
    """
    Run database migration for NSE securities management.
    """
    print("🔄 Starting database migration for NSE securities...")
    
    db_manager = SimpleDatabaseManager()
    
    try:
        # Initialize database
        await db_manager.initialize()
        print("✅ Database connection established")
        
        # 1. Create all tables
        print("📊 Creating database tables...")
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
        
        # 2. Create default watchlists
        print("📋 Creating default watchlists...")
        await create_default_watchlists(db_manager)
        print("✅ Default watchlists created")
        
        print("🎉 Database migration completed successfully!")
        print("📝 Note: NSE data sync will be done separately after API is running")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await db_manager.close()


async def create_default_watchlists(db_manager):
    """
    Create default system watchlists.
    """
    default_watchlists = [
        {
            'name': 'NIFTY 50',
            'description': 'Top 50 large-cap stocks by market capitalization',
            'is_system': True,
            'is_default': True
        },
        {
            'name': 'IT Stocks',
            'description': 'Information Technology sector stocks',
            'is_system': True,
            'is_default': False
        },
        {
            'name': 'Banking Stocks',
            'description': 'Banking and financial services stocks',
            'is_system': True,
            'is_default': False
        },
        {
            'name': 'My Favorites',
            'description': 'Your personally selected stocks',
            'is_system': False,
            'is_default': False
        }
    ]
    
    async with db_manager.get_session() as db:
        for wl_data in default_watchlists:
            watchlist = Watchlist(
                name=wl_data['name'],
                description=wl_data['description'],
                user_id='default_user',
                is_default=wl_data['is_default'],
                is_system=wl_data['is_system']
            )
            db.add(watchlist)
        
        await db.commit()


async def verify_migration():
    """
    Verify migration was successful.
    """
    print("🔍 Verifying migration...")
    
    db_manager = SimpleDatabaseManager()
    await db_manager.initialize()
    
    try:
        async with db_manager.get_session() as db:
            # Check tables exist by checking watchlists
            from sqlalchemy import select, func
            
            watchlists_count = await db.execute(
                select(func.count(Watchlist.id))
            )
            wl_count = watchlists_count.scalar()
            
            print(f"📋 Total watchlists: {wl_count}")
            
            if wl_count > 0:
                print("✅ Migration verification successful!")
                return True
            else:
                print("❌ Migration verification failed!")
                return False
                
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
    finally:
        await db_manager.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='NSE Securities Database Migration')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify migration, do not run it')
    
    args = parser.parse_args()
    
    if args.verify_only:
        asyncio.run(verify_migration())
    else:
        asyncio.run(migrate_database())
        asyncio.run(verify_migration())
