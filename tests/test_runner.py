"""
Test Suite Runner and Configuration
Central test runner with organized test execution and reporting
"""

import os
import sys
from pathlib import Path
import subprocess
import time
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class TestRunner:
    """Centralized test runner for the GoGoTrade application"""
    
    def __init__(self):
        self.test_directory = Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def check_system_requirements(self) -> Dict[str, bool]:
        """Check if system requirements are met for testing"""
        requirements = {
            "docker_running": self._check_docker(),
            "backend_accessible": self._check_backend(),
            "frontend_accessible": self._check_frontend(),
            "python_environment": self._check_python_env()
        }
        
        return requirements
    
    def _check_docker(self) -> bool:
        """Check if Docker containers are running"""
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0 and "gogotrade" in result.stdout
        except Exception:
            return False
    
    def _check_backend(self) -> bool:
        """Check if backend is accessible"""
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_frontend(self) -> bool:
        """Check if frontend is accessible"""
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_python_env(self) -> bool:
        """Check if required Python packages are available"""
        required_packages = ["fastapi", "sqlalchemy", "pandas"]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        
        return True
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        
        test_files = [
            "test_database.py",
            "test_ai_services.py",
            "test_backtesting.py"
        ]
        
        results = {}
        
        for test_file in test_files:
            test_path = self.test_directory / test_file
            
            if test_path.exists():
                print(f"  📝 Running {test_file}...")
                
                try:
                    # Run the test file directly as a Python script
                    result = subprocess.run(
                        [sys.executable, str(test_path)],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(self.test_directory.parent)
                    )
                    
                    results[test_file] = {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "errors": result.stderr
                    }
                    
                    status = "✅" if result.returncode == 0 else "❌"
                    print(f"    {status} {test_file}")
                    
                except subprocess.TimeoutExpired:
                    results[test_file] = {
                        "success": False,
                        "output": "",
                        "errors": "Test timed out"
                    }
                    print(f"    ⏰ {test_file} - Timed out")
                    
                except Exception as e:
                    results[test_file] = {
                        "success": False,
                        "output": "",
                        "errors": str(e)
                    }
                    print(f"    ❌ {test_file} - Error: {e}")
            else:
                print(f"    ⚠️  {test_file} not found")
        
        return results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔗 Running Integration Tests...")
        
        test_files = [
            "test_api_endpoints.py",
            "test_integration.py"
        ]
        
        results = {}
        
        # Check system requirements first
        requirements = self.check_system_requirements()
        
        if not requirements["backend_accessible"]:
            print("  ⚠️  Backend not accessible - skipping integration tests")
            return {"skipped": "Backend not accessible"}
        
        for test_file in test_files:
            test_path = self.test_directory / test_file
            
            if test_path.exists():
                print(f"  📝 Running {test_file}...")
                
                try:
                    result = subprocess.run(
                        [sys.executable, str(test_path)],
                        capture_output=True,
                        text=True,
                        timeout=120,  # Integration tests may take longer
                        cwd=str(self.test_directory.parent)
                    )
                    
                    results[test_file] = {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "errors": result.stderr
                    }
                    
                    status = "✅" if result.returncode == 0 else "❌"
                    print(f"    {status} {test_file}")
                    
                except Exception as e:
                    results[test_file] = {
                        "success": False,
                        "output": "",
                        "errors": str(e)
                    }
                    print(f"    ❌ {test_file} - Error: {e}")
            else:
                print(f"    ⚠️  {test_file} not found")
        
        return results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        test_files = [
            "test_performance.py"
        ]
        
        results = {}
        
        # Check if system is ready for performance testing
        requirements = self.check_system_requirements()
        
        if not all([requirements["backend_accessible"], requirements["docker_running"]]):
            print("  ⚠️  System not ready for performance tests")
            return {"skipped": "System not ready"}
        
        for test_file in test_files:
            test_path = self.test_directory / test_file
            
            if test_path.exists():
                print(f"  📝 Running {test_file}...")
                
                try:
                    result = subprocess.run(
                        [sys.executable, str(test_path)],
                        capture_output=True,
                        text=True,
                        timeout=300,  # Performance tests may take longer
                        cwd=str(self.test_directory.parent)
                    )
                    
                    results[test_file] = {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "errors": result.stderr
                    }
                    
                    status = "✅" if result.returncode == 0 else "❌"
                    print(f"    {status} {test_file}")
                    
                except Exception as e:
                    results[test_file] = {
                        "success": False,
                        "output": "",
                        "errors": str(e)
                    }
                    print(f"    ❌ {test_file} - Error: {e}")
            else:
                print(f"    ⚠️  {test_file} not found")
        
        return results
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting GoGoTrade Test Suite")
        print("=" * 50)
        
        self.start_time = time.time()
        
        # Check system requirements
        print("🔍 Checking System Requirements...")
        requirements = self.check_system_requirements()
        
        for req_name, req_status in requirements.items():
            status = "✅" if req_status else "❌"
            print(f"  {status} {req_name.replace('_', ' ').title()}")
        
        print()
        
        # Run test suites
        self.results["unit_tests"] = self.run_unit_tests()
        print()
        
        self.results["integration_tests"] = self.run_integration_tests()
        print()
        
        self.results["performance_tests"] = self.run_performance_tests()
        print()
        
        self.end_time = time.time()
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate a comprehensive test summary report"""
        print("=" * 50)
        print("📊 TEST SUITE SUMMARY REPORT")
        print("=" * 50)
        
        total_time = self.end_time - self.start_time if self.start_time and self.end_time else 0
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
        print()
        
        # Count results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_suites = 0
        
        for suite_name, suite_results in self.results.items():
            print(f"📋 {suite_name.replace('_', ' ').title()}:")
            
            if isinstance(suite_results, dict) and "skipped" in suite_results:
                print(f"  ⚠️  Skipped: {suite_results['skipped']}")
                skipped_suites += 1
            else:
                for test_name, test_result in suite_results.items():
                    total_tests += 1
                    if test_result["success"]:
                        passed_tests += 1
                        print(f"  ✅ {test_name}")
                    else:
                        failed_tests += 1
                        print(f"  ❌ {test_name}")
                        if test_result["errors"]:
                            print(f"     Error: {test_result['errors'][:100]}...")
            print()
        
        # Overall statistics
        print("📈 Overall Statistics:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Skipped Suites: {skipped_suites}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"  Success Rate: {success_rate:.1f}%")
            
            overall_status = "✅ EXCELLENT" if success_rate >= 90 else \
                           "⚠️ GOOD" if success_rate >= 70 else \
                           "❌ NEEDS ATTENTION"
            
            print(f"  Overall Status: {overall_status}")
        
        print()
        print("🔧 Next Steps:")
        
        if failed_tests > 0:
            print("  1. Review and fix failed tests")
            print("  2. Check system dependencies")
            print("  3. Verify Docker containers are running")
        else:
            print("  1. All tests passing! ✅")
            print("  2. Consider adding more test cases")
            print("  3. Monitor performance in production")
        
        print("\n" + "=" * 50)


def main():
    """Main test runner entry point"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        runner = TestRunner()
        
        if test_type == "unit":
            runner.run_unit_tests()
        elif test_type == "integration":
            runner.run_integration_tests()
        elif test_type == "performance":
            runner.run_performance_tests()
        elif test_type == "all":
            runner.run_all_tests()
        else:
            print("Usage: python test_runner.py [unit|integration|performance|all]")
    else:
        # Default: run all tests
        runner = TestRunner()
        runner.run_all_tests()


if __name__ == "__main__":
    main()
