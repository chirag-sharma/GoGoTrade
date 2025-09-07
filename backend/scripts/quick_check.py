#!/usr/bin/env python3
"""
Quick system status check - lightweight version for regular monitoring
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def quick_status_check():
    """Quick system status check."""
    base_url = "http://localhost:8000"
    
    print("🔍 GoGoTrade Quick Status Check")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            
            # Check if backend is running
            try:
                async with session.get(f"{base_url}/api/v1/status") as response:
                    if response.status == 200:
                        print("✅ Backend Server: Running")
                        
                        # Get detailed status
                        data = await response.json()
                        print(f"   Version: {data.get('version', 'Unknown')}")
                        print(f"   Status: {data.get('status', 'Unknown')}")
                    else:
                        print(f"❌ Backend Server: HTTP {response.status}")
                        return
            except Exception as e:
                print(f"❌ Backend Server: Not running ({e})")
                print("\n💡 To start the server:")
                print("   cd backend && ./startup.sh")
                print("   or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
                return
            
            # Check real-time status
            try:
                async with session.get(f"{base_url}/api/v1/real-time/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Real-time Service: {data.get('market_session', 'Unknown')}")
                        print(f"   Active Subscriptions: {data.get('active_subscriptions', 0)}")
                        print(f"   Market Open: {data.get('is_market_open', False)}")
                    else:
                        print(f"⚠️  Real-time Service: HTTP {response.status}")
            except Exception as e:
                print(f"⚠️  Real-time Service: Error ({e})")
            
            # Check for live data
            try:
                async with session.get(f"{base_url}/api/v1/real-time/prices") as response:
                    if response.status == 200:
                        prices = await response.json()
                        if prices:
                            print(f"✅ Live Data: {len(prices)} symbols active")
                            # Show one example
                            for price in prices[:1]:
                                symbol = price.get('symbol', 'N/A')
                                ltp = price.get('ltp', 0)
                                change = price.get('change_percent', 0)
                                print(f"   Example: {symbol} ${ltp:.2f} ({change:+.2f}%)")
                        else:
                            print("⚠️  Live Data: No active symbols")
                            print("   💡 Subscribe with: curl -X POST http://localhost:8000/api/v1/real-time/subscribe -H 'Content-Type: application/json' -d '{\"symbols\": [\"AAPL\"]}'")
                    else:
                        print(f"⚠️  Live Data: HTTP {response.status}")
            except Exception as e:
                print(f"⚠️  Live Data: Error ({e})")
            
            # Check signals
            try:
                async with session.get(f"{base_url}/api/v1/real-time/signals") as response:
                    if response.status == 200:
                        signals = await response.json()
                        if signals:
                            print(f"✅ Trading Signals: {len(signals)} active")
                        else:
                            print("ℹ️  Trading Signals: None active")
                    else:
                        print(f"⚠️  Trading Signals: HTTP {response.status}")
            except Exception as e:
                print(f"⚠️  Trading Signals: Error ({e})")
            
            print("\n🔗 Quick Links:")
            print(f"• API Docs: {base_url}/docs")
            print(f"• Status: {base_url}/api/v1/status")
            print(f"• Real-time: {base_url}/api/v1/real-time/status")
            
    except Exception as e:
        print(f"❌ System check failed: {e}")


if __name__ == "__main__":
    asyncio.run(quick_status_check())
