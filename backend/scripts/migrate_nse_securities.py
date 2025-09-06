"""
Database migration script for NSE securities management.
Creates new tables and imports NSE instruments data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import init_database, settings
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.models.market_data import (
    InstrumentExtended, Watchlist, WatchlistItem, 
    MarketStats, SectorPerformance
)
from app.services.nse_data_service import NSEDataService


async def migrate_database():
    """
    Run database migration for NSE securities management.
    """
    print("🔄 Starting database migration for NSE securities...")
    
    try:
        # Initialize database first
        await init_database()
        
        # Create our own engine for this migration
        engine = create_async_engine(settings.DATABASE_URL)
        
        # 1. Create all tables
        print("📊 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
        
        # 2. Create default watchlists
        print("📋 Creating default watchlists...")
        await create_default_watchlists(engine)
        print("✅ Default watchlists created")
        
        # 3. Sync NSE data
        print("📈 Syncing NSE securities data...")
        nse_service = NSEDataService()
        results = await nse_service.full_nse_data_sync()
        print(f"✅ NSE data sync completed: {results}")
        
        # Clean up
        await engine.dispose()
        
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


async def create_default_watchlists(engine):
    """
    Create default system watchlists.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    # Create session maker for this engine
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
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
    
    async with async_session() as db:
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


async def verify_migration(engine):
    """
    Verify migration was successful.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    print("🔍 Verifying migration...")
    
    # Create session maker for this engine
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # Check instruments count
            from sqlalchemy import select, func
            from app.models import Instrument
            
            instruments_count = await db.execute(
                select(func.count(Instrument.id))
            )
            count = instruments_count.scalar()
            
            print(f"📊 Total instruments: {count}")
            
            # Check watchlists count
            watchlists_count = await db.execute(
                select(func.count(Watchlist.id))
            )
            wl_count = watchlists_count.scalar()
            
            print(f"📋 Total watchlists: {wl_count}")
            
            # Check extended info count
            extended_count = await db.execute(
                select(func.count(InstrumentExtended.id))
            )
            ext_count = extended_count.scalar()
            
            print(f"📈 Extended info records: {ext_count}")
            
            if count > 0 and wl_count > 0:
                print("✅ Migration verification successful!")
                return True
            else:
                print("❌ Migration verification failed!")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='NSE Securities Database Migration')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify migration, do not run it')
    
    args = parser.parse_args()
    
    async def main():
        engine = create_async_engine(settings.DATABASE_URL)
        try:
            if args.verify_only:
                await verify_migration(engine)
            else:
                await migrate_database()
                await verify_migration(engine)
        finally:
            await engine.dispose()
    
    asyncio.run(main())
