"""
Add sample Indian stock data for testing APIs.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import init_database, get_db_session
from app.models import Instrument, InstrumentType
from app.models.market_data import InstrumentExtended, IndustryGroup, MarketSegment
from sqlalchemy import select


async def add_sample_stocks():
    """Add sample Indian stocks for testing."""
    
    sample_stocks = [
        {
            'instrument_token': 408065,
            'exchange_token': 1594,
            'tradingsymbol': 'RELIANCE',
            'name': 'Reliance Industries Limited',
            'last_price': Decimal('2450.75'),
            'instrument_type': InstrumentType.EQUITY,
            'segment': 'NSE',
            'exchange': 'NSE',
            'tick_size': Decimal('0.05'),
            'lot_size': 1,
            # Extended info
            'industry_group': IndustryGroup.OIL_AND_GAS,
            'sector': 'Oil & Gas',
            'market_segment': MarketSegment.LARGE_CAP,
            'market_cap': 1658000000000,  # 16.58 lakh crores
            'pe_ratio': Decimal('25.5'),
            'pb_ratio': Decimal('2.1'),
            'isin': 'INE002A01018'
        },
        {
            'instrument_token': 2977281,
            'exchange_token': 11629,
            'tradingsymbol': 'TCS',
            'name': 'Tata Consultancy Services Limited',
            'last_price': Decimal('3890.45'),
            'instrument_type': InstrumentType.EQUITY,
            'segment': 'NSE',
            'exchange': 'NSE',
            'tick_size': Decimal('0.05'),
            'lot_size': 1,
            # Extended info
            'industry_group': IndustryGroup.IT,
            'sector': 'Information Technology',
            'market_segment': MarketSegment.LARGE_CAP,
            'market_cap': 1420000000000,  # 14.2 lakh crores
            'pe_ratio': Decimal('28.2'),
            'pb_ratio': Decimal('12.5'),
            'isin': 'INE467B01029'
        },
        {
            'instrument_token': 1270529,
            'exchange_token': 4963,
            'tradingsymbol': 'INFY',
            'name': 'Infosys Limited',
            'last_price': Decimal('1650.30'),
            'instrument_type': InstrumentType.EQUITY,
            'segment': 'NSE',
            'exchange': 'NSE',
            'tick_size': Decimal('0.05'),
            'lot_size': 1,
            # Extended info
            'industry_group': IndustryGroup.IT,
            'sector': 'Information Technology',
            'market_segment': MarketSegment.LARGE_CAP,
            'market_cap': 685000000000,  # 6.85 lakh crores
            'pe_ratio': Decimal('24.8'),
            'pb_ratio': Decimal('8.2'),
            'isin': 'INE009A01021'
        },
        {
            'instrument_token': 1895937,
            'exchange_token': 7404,
            'tradingsymbol': 'HDFCBANK',
            'name': 'HDFC Bank Limited',
            'last_price': Decimal('1580.75'),
            'instrument_type': InstrumentType.EQUITY,
            'segment': 'NSE',
            'exchange': 'NSE',
            'tick_size': Decimal('0.05'),
            'lot_size': 1,
            # Extended info
            'industry_group': IndustryGroup.BANKING,
            'sector': 'Banking',
            'market_segment': MarketSegment.LARGE_CAP,
            'market_cap': 1200000000000,  # 12 lakh crores
            'pe_ratio': Decimal('19.5'),
            'pb_ratio': Decimal('2.8'),
            'isin': 'INE040A01034'
        },
        {
            'instrument_token': 348929,
            'exchange_token': 1363,
            'tradingsymbol': 'ICICIBANK',
            'name': 'ICICI Bank Limited',
            'last_price': Decimal('1145.60'),
            'instrument_type': InstrumentType.EQUITY,
            'segment': 'NSE',
            'exchange': 'NSE',
            'tick_size': Decimal('0.05'),
            'lot_size': 1,
            # Extended info
            'industry_group': IndustryGroup.BANKING,
            'sector': 'Banking',
            'market_segment': MarketSegment.LARGE_CAP,
            'market_cap': 810000000000,  # 8.1 lakh crores
            'pe_ratio': Decimal('16.2'),
            'pb_ratio': Decimal('2.2'),
            'isin': 'INE090A01021'
        },
        {
            'instrument_token': 225537,
            'exchange_token': 881,
            'tradingsymbol': 'BAJFINANCE',
            'name': 'Bajaj Finance Limited',
            'last_price': Decimal('6890.25'),
            'instrument_type': InstrumentType.EQUITY,
            'segment': 'NSE',
            'exchange': 'NSE',
            'tick_size': Decimal('0.05'),
            'lot_size': 1,
            # Extended info
            'industry_group': IndustryGroup.FINANCIAL_SERVICES,
            'sector': 'Financial Services',
            'market_segment': MarketSegment.LARGE_CAP,
            'market_cap': 425000000000,  # 4.25 lakh crores
            'pe_ratio': Decimal('32.1'),
            'pb_ratio': Decimal('4.8'),
            'isin': 'INE296A01024'
        }
    ]
    
    await init_database()
    
    async with get_db_session() as db:
        # Check if data already exists
        existing = await db.execute(select(Instrument).limit(1))
        if existing.first():
            print("Sample data already exists, skipping...")
            return
        
        print("Adding sample Indian stocks...")
        
        for stock_data in sample_stocks:
            # Create basic instrument
            instrument = Instrument(
                instrument_token=stock_data['instrument_token'],
                exchange_token=stock_data['exchange_token'],
                tradingsymbol=stock_data['tradingsymbol'],
                name=stock_data['name'],
                last_price=stock_data['last_price'],
                instrument_type=stock_data['instrument_type'],
                segment=stock_data['segment'],
                exchange=stock_data['exchange'],
                tick_size=stock_data['tick_size'],
                lot_size=stock_data['lot_size']
            )
            
            db.add(instrument)
            await db.flush()  # Get the ID
            
            # Create extended info
            extended = InstrumentExtended(
                instrument_id=instrument.id,
                industry_group=stock_data['industry_group'],
                sector=stock_data['sector'],
                market_segment=stock_data['market_segment'],
                market_cap=stock_data['market_cap'],
                pe_ratio=stock_data['pe_ratio'],
                pb_ratio=stock_data['pb_ratio'],
                isin=stock_data['isin'],
                is_active=True,
                is_f_and_o=True,  # Most large caps have F&O
                data_last_updated=datetime.now(timezone.utc)
            )
            
            db.add(extended)
            print(f"  ✅ Added {stock_data['tradingsymbol']} - {stock_data['name']}")
        
        await db.commit()
        print(f"🎉 Successfully added {len(sample_stocks)} sample stocks!")


if __name__ == "__main__":
    asyncio.run(add_sample_stocks())
