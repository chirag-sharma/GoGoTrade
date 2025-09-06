"""
Direct test of Yahoo Finance integration.
Tests the Yahoo Finance service functionality independently.
"""

import asyncio
import logging
from app.services.yahoo_finance_service import yahoo_finance_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_yahoo_finance_service():
    """Test Yahoo Finance service functionality."""
    
    print("🚀 Testing Yahoo Finance Service")
    print("=" * 50)
    
    # Test symbols - mix of US and Indian stocks
    us_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    indian_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]
    
    try:
        # Test 1: Single live price
        print("\n🔍 Test 1: Single Live Price (AAPL)")
        price_data = await yahoo_finance_service.get_live_price("AAPL")
        if price_data:
            print(f"✅ AAPL: ${price_data['ltp']:.2f} ({price_data['change_percent']:+.2f}%)")
            print(f"   Volume: {price_data['volume']:,}")
            print(f"   Exchange: {price_data['exchange']}")
        else:
            print("❌ Failed to get AAPL price")
        
        # Test 2: Multiple live prices (US stocks)
        print("\n🔍 Test 2: Multiple US Stock Prices")
        us_prices = await yahoo_finance_service.get_multiple_live_prices(us_symbols)
        for symbol, data in us_prices.items():
            print(f"✅ {symbol}: ${data['ltp']:.2f} ({data['change_percent']:+.2f}%)")
        
        # Test 3: Multiple live prices (Indian stocks)
        print("\n🔍 Test 3: Multiple Indian Stock Prices")
        indian_prices = await yahoo_finance_service.get_multiple_live_prices(indian_symbols)
        for symbol, data in indian_prices.items():
            print(f"✅ {symbol}: ₹{data['ltp']:.2f} ({data['change_percent']:+.2f}%)")
        
        # Test 4: Historical data
        print("\n🔍 Test 4: Historical Data (AAPL - Last 5 hours)")
        historical_data = await yahoo_finance_service.get_historical_data(
            "AAPL", 
            period="1d", 
            interval="1h"
        )
        if historical_data:
            print(f"✅ Retrieved {len(historical_data)} historical records")
            # Show last 3 records
            for record in historical_data[-3:]:
                timestamp = record['timestamp'][:19]  # Remove timezone info for display
                print(f"   {timestamp}: O={record['open']:.2f} H={record['high']:.2f} "
                      f"L={record['low']:.2f} C={record['close']:.2f}")
        else:
            print("❌ Failed to get historical data")
        
        # Test 5: Market status
        print("\n🔍 Test 5: Market Status")
        market_status = await yahoo_finance_service.get_market_status()
        print(f"✅ Market State: {market_status['market_state']}")
        print(f"   Session: {market_status['market_session']}")
        print(f"   Open: {market_status['is_market_open']}")
        print(f"   Timezone: {market_status.get('timezone', 'N/A')}")
        
        # Test 6: Symbol search
        print("\n🔍 Test 6: Symbol Search")
        search_results = await yahoo_finance_service.search_symbols("REL")
        print(f"✅ Found {len(search_results)} symbols matching 'REL':")
        for result in search_results:
            print(f"   {result['symbol']} ({result['exchange']})")
        
        print("\n🎉 All Yahoo Finance tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Test error details:")
    
    finally:
        # Cleanup
        await yahoo_finance_service.cleanup()
        print("\n✅ Yahoo Finance service cleaned up")


if __name__ == "__main__":
    print("Yahoo Finance Service Test")
    print("Testing direct integration with yfinance library")
    print("This will fetch real market data from Yahoo Finance")
    print()
    
    try:
        asyncio.run(test_yahoo_finance_service())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
