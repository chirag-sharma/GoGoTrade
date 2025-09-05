"""
Performance and Load Testing Suite
Tests system performance, scalability, and resource usage
"""

import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests library not available - some tests will be skipped")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil library not available - resource monitoring tests will be skipped")


class TestPerformance:
    """Test system performance characteristics"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = []
    
    def test_api_response_times(self):
        """Test API endpoint response times"""
        if not REQUESTS_AVAILABLE:
            print("⚠️  Skipping API response time tests - requests not available")
            return
        
        endpoints = [
            ("/health", "Health Check"),
            ("/health/database", "Database Health"),
            ("/api/v1/trading-data/instruments", "Instruments"),
            ("/api/v1/trading-data/ohlcv/RELIANCE", "OHLCV Data"),
            ("/api/v1/strategies/signals/RELIANCE", "Trading Signals"),
            ("/api/v1/charts/chart-data/RELIANCE", "Chart Data")
        ]
        
        print("\n📊 API Response Time Analysis:")
        print("-" * 60)
        
        for endpoint, name in endpoints:
            try:
                # Warm up request
                requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                
                # Measure multiple requests
                times = []
                for _ in range(5):
                    start_time = time.time()
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    status = "✅" if avg_time < 1.0 else "⚠️" if avg_time < 2.0 else "❌"
                    
                    print(f"{status} {name:20} | Avg: {avg_time:.3f}s | Min: {min_time:.3f}s | Max: {max_time:.3f}s")
                    
                    self.test_results.append({
                        'endpoint': endpoint,
                        'name': name,
                        'avg_time': avg_time,
                        'min_time': min_time,
                        'max_time': max_time
                    })
                else:
                    print(f"❌ {name:20} | Failed to get valid responses")
                    
            except Exception as e:
                print(f"❌ {name:20} | Error: {e}")
    
    def test_concurrent_load(self):
        """Test system under concurrent load"""
        if not REQUESTS_AVAILABLE:
            print("⚠️  Skipping concurrent load tests - requests not available")
            return
        
        def make_request(endpoint):
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                return {
                    'success': response.status_code == 200,
                    'time': end_time - start_time,
                    'status_code': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
        
        print("\n🚀 Concurrent Load Test:")
        print("-" * 40)
        
        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        test_endpoint = "/api/v1/trading-data/instruments"
        
        for concurrent_users in concurrency_levels:
            print(f"\nTesting {concurrent_users} concurrent users:")
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_request, test_endpoint) 
                          for _ in range(concurrent_users * 2)]  # 2 requests per user
                
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_requests = sum(1 for r in results if r['success'])
            total_requests = len(results)
            success_rate = successful_requests / total_requests
            
            avg_response_time = sum(r['time'] for r in results if r['success']) / max(successful_requests, 1)
            
            status = "✅" if success_rate >= 0.95 else "⚠️" if success_rate >= 0.8 else "❌"
            
            print(f"{status} {concurrent_users:2d} users | "
                  f"Success: {success_rate:.1%} | "
                  f"Avg Response: {avg_response_time:.3f}s | "
                  f"Total Time: {total_time:.3f}s")
    
    def test_memory_usage_monitoring(self):
        """Monitor memory usage during operations"""
        if not PSUTIL_AVAILABLE:
            print("⚠️  Skipping memory monitoring - psutil not available")
            return
        
        print("\n💾 Memory Usage Monitoring:")
        print("-" * 30)
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Initial Memory: {initial_memory:.1f} MB")
        
        # Simulate some operations
        if REQUESTS_AVAILABLE:
            try:
                for i in range(20):
                    requests.get(f"{self.backend_url}/api/v1/trading-data/instruments", 
                               timeout=5)
                    
                    if i % 5 == 0:  # Check every 5 requests
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_increase = current_memory - initial_memory
                        
                        status = "✅" if memory_increase < 50 else "⚠️" if memory_increase < 100 else "❌"
                        print(f"{status} After {i+1:2d} requests: {current_memory:.1f} MB "
                              f"(+{memory_increase:.1f} MB)")
                
            except Exception as e:
                print(f"❌ Memory monitoring error: {e}")
    
    def test_database_query_performance(self):
        """Test database query performance through API"""
        if not REQUESTS_AVAILABLE:
            print("⚠️  Skipping database performance tests - requests not available")
            return
        
        print("\n🗄️  Database Query Performance:")
        print("-" * 35)
        
        # Test different data sizes
        symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "WIPRO"]
        
        for symbol in symbols:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}/api/v1/trading-data/ohlcv/{symbol}",
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    query_time = end_time - start_time
                    record_count = len(data) if isinstance(data, list) else 1
                    
                    status = "✅" if query_time < 0.5 else "⚠️" if query_time < 1.0 else "❌"
                    
                    print(f"{status} {symbol:8} | {record_count:4d} records | {query_time:.3f}s")
                else:
                    print(f"❌ {symbol:8} | HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {symbol:8} | Error: {e}")
    
    def generate_performance_report(self):
        """Generate a performance summary report"""
        print("\n" + "="*60)
        print("📈 PERFORMANCE TEST SUMMARY REPORT")
        print("="*60)
        
        if self.test_results:
            print("\n🎯 Response Time Analysis:")
            
            # Find fastest and slowest endpoints
            fastest = min(self.test_results, key=lambda x: x['avg_time'])
            slowest = max(self.test_results, key=lambda x: x['avg_time'])
            
            print(f"  ⚡ Fastest: {fastest['name']} ({fastest['avg_time']:.3f}s)")
            print(f"  🐌 Slowest: {slowest['name']} ({slowest['avg_time']:.3f}s)")
            
            # Performance categories
            fast_endpoints = [r for r in self.test_results if r['avg_time'] < 0.5]
            medium_endpoints = [r for r in self.test_results if 0.5 <= r['avg_time'] < 1.0]
            slow_endpoints = [r for r in self.test_results if r['avg_time'] >= 1.0]
            
            print(f"\n  ✅ Fast (< 0.5s):   {len(fast_endpoints)} endpoints")
            print(f"  ⚠️  Medium (0.5-1s): {len(medium_endpoints)} endpoints")
            print(f"  ❌ Slow (> 1s):     {len(slow_endpoints)} endpoints")
            
        print("\n🔧 Optimization Recommendations:")
        
        if self.test_results:
            slow_endpoints = [r for r in self.test_results if r['avg_time'] >= 1.0]
            if slow_endpoints:
                print("  - Optimize slow endpoints:")
                for endpoint in slow_endpoints:
                    print(f"    • {endpoint['name']}: {endpoint['avg_time']:.3f}s")
            else:
                print("  - All endpoints perform well!")
        
        print("  - Consider adding caching for frequently accessed data")
        print("  - Monitor memory usage under sustained load")
        print("  - Implement connection pooling if not already done")
        
        print("\n" + "="*60)


def run_performance_tests():
    """Run all performance tests"""
    print("🧪 Starting Performance Test Suite...")
    print("Note: Ensure the system is running (docker-compose up)")
    
    tester = TestPerformance()
    
    try:
        tester.test_api_response_times()
        tester.test_concurrent_load()
        tester.test_memory_usage_monitoring()
        tester.test_database_query_performance()
        tester.generate_performance_report()
        
    except KeyboardInterrupt:
        print("\n⚠️  Performance tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Performance test error: {e}")


if __name__ == "__main__":
    run_performance_tests()
