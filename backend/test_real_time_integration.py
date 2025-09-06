"""
Real-time data integration test script.
Tests the live data feed, WebSocket connections, and signal generation.
"""

import asyncio
import json
import logging
from datetime import datetime
import websockets
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealTimeDataTester:
    """Test real-time data integration functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws") + "/api/v1/real-time/ws"
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def test_api_status(self):
        """Test API status endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/real-time/status") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ API Status: {data}")
                    return True
                else:
                    logger.error(f"❌ API Status failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ API Status error: {e}")
            return False
    
    async def test_subscription(self, symbols: list):
        """Test subscribing to live data."""
        try:
            payload = {"symbols": symbols}
            async with self.session.post(
                f"{self.base_url}/api/v1/real-time/subscribe",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Subscription successful: {data}")
                    return True
                else:
                    logger.error(f"❌ Subscription failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Subscription error: {e}")
            return False
    
    async def test_live_prices(self, symbols: list):
        """Test getting live prices."""
        try:
            for symbol in symbols:
                async with self.session.get(
                    f"{self.base_url}/api/v1/real-time/price/{symbol}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Live price for {symbol}: ${data['ltp']:.2f} ({data['change_percent']:+.2f}%)")
                    else:
                        logger.warning(f"⚠️ No price data for {symbol}: {response.status}")
            return True
        except Exception as e:
            logger.error(f"❌ Live prices error: {e}")
            return False
    
    async def test_signals(self):
        """Test getting trading signals."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/real-time/signals") as response:
                if response.status == 200:
                    signals = await response.json()
                    logger.info(f"✅ Active signals: {len(signals)}")
                    for signal in signals[:3]:  # Show first 3 signals
                        logger.info(f"   📈 {signal['symbol']}: {signal['signal_type']} "
                                  f"(confidence: {signal['confidence']:.1%})")
                    return True
                else:
                    logger.error(f"❌ Signals failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Signals error: {e}")
            return False
    
    async def test_websocket_connection(self, symbols: list, duration: int = 30):
        """Test WebSocket connection and real-time updates."""
        try:
            logger.info(f"🔌 Connecting to WebSocket: {self.ws_url}")
            
            async with websockets.connect(self.ws_url) as websocket:
                logger.info("✅ WebSocket connected")
                
                # Subscribe to symbols
                for symbol in symbols:
                    subscribe_msg = {
                        "action": "subscribe",
                        "symbol": symbol
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    logger.info(f"📡 Subscribed to {symbol}")
                
                # Listen for updates
                start_time = datetime.now()
                message_count = 0
                
                while (datetime.now() - start_time).seconds < duration:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        message_count += 1
                        
                        if data.get("type") == "price_update":
                            symbol = data.get("symbol")
                            price_data = data.get("data", {})
                            logger.info(f"📊 {symbol}: ${price_data.get('ltp', 0):.2f} "
                                      f"({price_data.get('change_percent', 0):+.2f}%)")
                        
                        elif data.get("type") == "trading_signal":
                            signal_data = data.get("data", {})
                            logger.info(f"🚨 Signal: {signal_data.get('symbol')} "
                                      f"{signal_data.get('signal_type')} "
                                      f"({signal_data.get('confidence', 0):.1%})")
                        
                        elif data.get("type") == "subscription_confirmed":
                            logger.info(f"✅ Subscription confirmed: {data.get('symbol')}")
                        
                        else:
                            logger.debug(f"📝 Message: {data}")
                    
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        ping_msg = {"action": "ping"}
                        await websocket.send(json.dumps(ping_msg))
                        logger.debug("🏓 Ping sent")
                
                logger.info(f"✅ WebSocket test completed. Received {message_count} messages in {duration}s")
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            return False
    
    async def test_sample_data_generation(self):
        """Test sample data generation."""
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/real-time/test/generate-sample-data"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Sample data generation: {data['message']}")
                    return True
                else:
                    logger.error(f"❌ Sample data generation failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Sample data generation error: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of all real-time features."""
        logger.info("🚀 Starting comprehensive real-time data integration test with Yahoo Finance...")
        
        # Use realistic symbols that exist in Yahoo Finance
        test_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        indian_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]
        
        # Initialize
        await self.initialize()
        
        try:
            # Test 1: API Status
            logger.info("\n🔍 Test 1: API Status")
            await self.test_api_status()
            
            # Test 2: Subscription with US stocks
            logger.info("\n🔍 Test 2: US Stocks Subscription")
            await self.test_subscription(test_symbols)
            
            # Test 3: Subscription with Indian stocks
            logger.info("\n🔍 Test 3: Indian Stocks Subscription")
            await self.test_subscription(indian_symbols)
            
            # Wait for Yahoo Finance data to be fetched
            logger.info("⏳ Waiting 60 seconds for Yahoo Finance data to be fetched...")
            await asyncio.sleep(60)
            
            # Test 4: Live Prices for US stocks
            logger.info("\n🔍 Test 4: US Stocks Live Prices")
            await self.test_live_prices(test_symbols)
            
            # Test 5: Live Prices for Indian stocks
            logger.info("\n🔍 Test 5: Indian Stocks Live Prices")
            await self.test_live_prices(indian_symbols)
            
            # Test 6: Trading Signals
            logger.info("\n🔍 Test 6: Trading Signals")
            await self.test_signals()
            
            # Test 7: WebSocket Connection (shorter duration due to Yahoo Finance rate limits)
            logger.info("\n🔍 Test 7: WebSocket Real-Time Updates")
            await self.test_websocket_connection(test_symbols[:2], duration=45)
            
            logger.info("\n🎉 Comprehensive Yahoo Finance test completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Comprehensive test failed: {e}")
        
        finally:
            await self.close()


async def main():
    """Main test function."""
    tester = RealTimeDataTester()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    print("Real-Time Data Integration Test with Yahoo Finance")
    print("=" * 60)
    print("This script tests the real-time data integration features:")
    print("• Yahoo Finance live data fetching for US and Indian stocks")
    print("• API endpoints for subscription and live prices")
    print("• WebSocket connections for real-time updates")
    print("• Trading signal generation based on real market data")
    print()
    print("Supported symbols:")
    print("• US Stocks: AAPL, GOOGL, MSFT, TSLA, AMZN, META, etc.")
    print("• Indian Stocks: RELIANCE, TCS, INFY, HDFCBANK, etc.")
    print()
    print("Make sure the GoGoTrade backend is running on http://localhost:8000")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
