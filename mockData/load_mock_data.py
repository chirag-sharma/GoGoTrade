"""
Mock data loader for NSE securities management system.
Loads realistic Indian stock market data from JSON files into the database.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.core.database import init_database, get_db_session
from app.models import Instrument, InstrumentType
from app.models.market_data import (
    InstrumentExtended, MarketStats, SectorPerformance,
    IndustryGroup, MarketSegment
)
from sqlalchemy import select


class MockDataLoader:
    """Loads mock data from JSON files into the database."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.industry_mapping = {
            'Oil & Gas': IndustryGroup.OIL_AND_GAS,
            'IT Services': IndustryGroup.IT,
            'Banking': IndustryGroup.BANKING,
            'FMCG': IndustryGroup.FMCG,
            'Financial Services': IndustryGroup.FINANCIAL_SERVICES,
            'Telecom': IndustryGroup.TELECOM,
            'Automobile': IndustryGroup.AUTOMOBILE,
            'Infrastructure': IndustryGroup.INFRASTRUCTURE,
            'Pharma': IndustryGroup.PHARMA,
            'Chemicals': IndustryGroup.CHEMICALS,
            'Consumer Durables': IndustryGroup.CONSUMER_DURABLES,
            'Mining': IndustryGroup.METALS,  # Map mining to metals
            'Metals': IndustryGroup.METALS,
            'Power': IndustryGroup.ENERGY,
            'Cement': IndustryGroup.INFRASTRUCTURE,
            'Internet': IndustryGroup.IT,
            'Fintech': IndustryGroup.FINANCIAL_SERVICES,
            'E-commerce': IndustryGroup.IT,
            'Insurance': IndustryGroup.FINANCIAL_SERVICES,
            'Retail': IndustryGroup.CONSUMER_GOODS,
            'Aviation': IndustryGroup.INFRASTRUCTURE,
            'Biotechnology': IndustryGroup.PHARMA,
        }
        
        self.segment_mapping = {
            'LARGE_CAP': MarketSegment.LARGE_CAP,
            'MID_CAP': MarketSegment.MID_CAP,
            'SMALL_CAP': MarketSegment.SMALL_CAP
        }

    def load_json_file(self, filename: str) -> list:
        """Load JSON data from file."""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {filename}: {e}")
            return []

    async def load_instruments(self) -> int:
        """Load instruments and extended info from JSON files."""
        print("📊 Loading NSE securities data...")
        
        # Load all JSON files
        nse_data = self.load_json_file('nse_securities.json')
        mid_small_data = self.load_json_file('mid_small_cap_securities.json')
        
        all_securities = nse_data + mid_small_data
        loaded_count = 0
        
        async with get_db_session() as db:
            try:
                for item in all_securities:
                    # Check if instrument already exists
                    result = await db.execute(
                        select(Instrument).where(Instrument.tradingsymbol == item['symbol'])
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        print(f"⚠️  Instrument {item['symbol']} already exists, skipping...")
                        continue
                    
                    # Create instrument
                    instrument = Instrument(
                        instrument_token=hash(item['symbol']) % 1000000,  # Simple token generation
                        exchange_token=hash(item['symbol']) % 100000,
                        tradingsymbol=item['symbol'],
                        name=item['name'],
                        last_price=Decimal(str(item['current_price'])),
                        tick_size=Decimal('0.05'),
                        lot_size=1,
                        instrument_type=InstrumentType.EQUITY,
                        segment='EQ',
                        exchange=item['exchange']
                    )
                    
                    db.add(instrument)
                    await db.flush()  # Get the ID
                    
                    # Create extended info
                    industry_group = self.industry_mapping.get(
                        item.get('industry'), 
                        IndustryGroup.OTHER
                    )
                    
                    market_segment = self.segment_mapping.get(
                        item.get('market_segment'),
                        MarketSegment.LARGE_CAP
                    )
                    
                    extended = InstrumentExtended(
                        instrument_id=instrument.id,
                        industry_group=industry_group,
                        sector=item.get('sector'),
                        market_segment=market_segment,
                        market_cap=item.get('market_cap'),
                        pe_ratio=Decimal(str(item['pe_ratio'])) if item.get('pe_ratio') else None,
                        pb_ratio=Decimal(str(item['pb_ratio'])) if item.get('pb_ratio') else None,
                        isin=item.get('isin'),
                        is_active=True,
                        is_f_and_o=item.get('is_f_and_o', False),
                        data_last_updated=datetime.now(timezone.utc)
                    )
                    
                    db.add(extended)
                    loaded_count += 1
                
                await db.commit()
                print(f"✅ Loaded {loaded_count} securities into database")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Failed to load instruments: {e}")
                raise
        
        return loaded_count

    async def load_market_stats(self) -> int:
        """Load market movers data."""
        print("📈 Loading market movers data...")
        
        movers_data = self.load_json_file('market_movers.json')
        loaded_count = 0
        
        async with get_db_session() as db:
            try:
                for item in movers_data:
                    # Get instrument ID
                    result = await db.execute(
                        select(Instrument.id).where(Instrument.tradingsymbol == item['symbol'])
                    )
                    instrument_id = result.scalar_one_or_none()
                    
                    if not instrument_id:
                        print(f"⚠️  Instrument {item['symbol']} not found, skipping market stat...")
                        continue
                    
                    # Check if stat already exists
                    stats_date = datetime.strptime(item['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    result = await db.execute(
                        select(MarketStats).where(
                            MarketStats.instrument_id == instrument_id,
                            MarketStats.stats_date == stats_date
                        )
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        continue
                    
                    # Calculate price levels (mock data)
                    price_change = Decimal(str(item['price_change']))
                    current_price = Decimal(str(abs(price_change) * 25))  # Mock current price
                    
                    # Set ranks based on category
                    gainer_rank = None
                    loser_rank = None
                    volume_rank = None
                    turnover_rank = None
                    
                    if item['category'] == 'gainers':
                        gainer_rank = loaded_count % 10 + 1
                    elif item['category'] == 'losers':
                        loser_rank = loaded_count % 10 + 1
                    elif item['category'] == 'most_active':
                        volume_rank = loaded_count % 10 + 1
                        turnover_rank = loaded_count % 10 + 1
                    
                    market_stat = MarketStats(
                        instrument_id=instrument_id,
                        stats_date=stats_date,
                        volume=item['volume'],
                        turnover=item['turnover'],
                        trades_count=item['volume'] // 100,  # Mock trades count
                        open_price=current_price,
                        high_price=current_price * Decimal('1.05'),
                        low_price=current_price * Decimal('0.95'),
                        close_price=current_price + price_change,
                        price_change=price_change,
                        price_change_percent=Decimal(str(item['price_change_percent'])),
                        gainer_rank=gainer_rank,
                        loser_rank=loser_rank,
                        volume_rank=volume_rank,
                        turnover_rank=turnover_rank
                    )
                    
                    db.add(market_stat)
                    loaded_count += 1
                
                await db.commit()
                print(f"✅ Loaded {loaded_count} market statistics")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Failed to load market stats: {e}")
                raise
        
        return loaded_count

    async def load_sector_performance(self) -> int:
        """Load sector performance data."""
        print("🏭 Loading sector performance data...")
        
        sector_data = self.load_json_file('sector_performance.json')
        loaded_count = 0
        
        async with get_db_session() as db:
            try:
                for item in sector_data:
                    # Check if sector performance already exists
                    perf_date = datetime.strptime(item['performance_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    result = await db.execute(
                        select(SectorPerformance).where(
                            SectorPerformance.sector_name == item['sector'],
                            SectorPerformance.stats_date == perf_date
                        )
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        continue
                    
                    # Map sector to industry group
                    industry_group = None
                    sector_name = item['sector']
                    if 'Technology' in sector_name:
                        industry_group = IndustryGroup.IT
                    elif 'Financial' in sector_name:
                        industry_group = IndustryGroup.FINANCIAL_SERVICES
                    elif 'Energy' in sector_name:
                        industry_group = IndustryGroup.ENERGY
                    elif 'Consumer' in sector_name:
                        industry_group = IndustryGroup.CONSUMER_GOODS
                    elif 'Healthcare' in sector_name:
                        industry_group = IndustryGroup.HEALTHCARE
                    elif 'Automobile' in sector_name:
                        industry_group = IndustryGroup.AUTOMOBILE
                    elif 'Infrastructure' in sector_name:
                        industry_group = IndustryGroup.INFRASTRUCTURE
                    elif 'Telecommunication' in sector_name:
                        industry_group = IndustryGroup.TELECOM
                    elif 'Metals' in sector_name:
                        industry_group = IndustryGroup.METALS
                    
                    # Calculate counts (mock data)
                    total_stocks = len(item.get('top_performers', []))
                    price_change = item['price_change_percent']
                    
                    if price_change > 0:
                        gainers_count = total_stocks * 70 // 100  # 70% gainers
                        losers_count = total_stocks * 20 // 100   # 20% losers  
                        unchanged_count = total_stocks - gainers_count - losers_count
                    else:
                        losers_count = total_stocks * 70 // 100   # 70% losers
                        gainers_count = total_stocks * 20 // 100  # 20% gainers
                        unchanged_count = total_stocks - gainers_count - losers_count
                    
                    sector_perf = SectorPerformance(
                        sector_name=sector_name,
                        industry_group=industry_group,
                        stats_date=perf_date,
                        total_stocks=max(total_stocks, 1),
                        gainers_count=gainers_count,
                        losers_count=losers_count,
                        unchanged_count=unchanged_count,
                        avg_change_percent=Decimal(str(item['price_change_percent'])),
                        total_turnover=int(item.get('total_market_cap', 0) // 1000),  # Mock turnover
                        market_cap_weighted_return=Decimal(str(item['price_change_percent']))
                    )
                    
                    db.add(sector_perf)
                    loaded_count += 1
                
                await db.commit()
                print(f"✅ Loaded {loaded_count} sector performance records")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Failed to load sector performance: {e}")
                raise
        
        return loaded_count

    async def load_all_data(self) -> dict:
        """Load all mock data into database."""
        print("🚀 Starting mock data loading process...")
        
        results = {
            'instruments': 0,
            'market_stats': 0,
            'sector_performance': 0,
            'errors': []
        }
        
        try:
            # Load instruments first
            results['instruments'] = await self.load_instruments()
            
            # Load market statistics
            results['market_stats'] = await self.load_market_stats()
            
            # Load sector performance
            results['sector_performance'] = await self.load_sector_performance()
            
            print("🎉 Mock data loading completed successfully!")
            print(f"📊 Summary: {results['instruments']} instruments, {results['market_stats']} market stats, {results['sector_performance']} sector records")
            
        except Exception as e:
            error_msg = f"Mock data loading failed: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return results

    async def verify_data(self) -> None:
        """Verify loaded data."""
        print("🔍 Verifying loaded data...")
        
        async with get_db_session() as db:
            # Count instruments
            result = await db.execute(select(Instrument))
            instruments = result.scalars().all()
            print(f"📊 Total instruments: {len(instruments)}")
            
            # Count extended info
            result = await db.execute(select(InstrumentExtended))
            extended = result.scalars().all()
            print(f"📈 Extended info records: {len(extended)}")
            
            # Count market stats
            result = await db.execute(select(MarketStats))
            stats = result.scalars().all()
            print(f"📊 Market statistics: {len(stats)}")
            
            # Count sector performance
            result = await db.execute(select(SectorPerformance))
            sectors = result.scalars().all()
            print(f"🏭 Sector performance records: {len(sectors)}")
            
            # Show sample data
            if instruments:
                print(f"📝 Sample instrument: {instruments[0].tradingsymbol} - {instruments[0].name}")
            
            if extended:
                print(f"📝 Sample extended info: {extended[0].sector} - {extended[0].industry_group}")


async def main():
    """Main function to load mock data."""
    await init_database()
    
    loader = MockDataLoader()
    results = await loader.load_all_data()
    await loader.verify_data()
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
