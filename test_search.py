#!/usr/bin/env python3
"""
Simple test script to verify backend search functionality
"""
import requests
import time
import json

def test_search_endpoint():
    """Test the search endpoint"""
    base_url = "http://localhost:8000"
    
    # Test basic health first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print("✅ Backend is responding")
        else:
            print("❌ Backend health check failed")
            return
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
        return
    
    # Test search endpoint
    try:
        search_response = requests.get(
            f"{base_url}/api/v1/search",
            params={"query": "RELIANCE"},
            timeout=10
        )
        print(f"\nSearch endpoint status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            data = search_response.json()
            print("✅ Search endpoint working!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Search endpoint failed: {search_response.text}")
            
    except Exception as e:
        print(f"❌ Search request failed: {e}")

if __name__ == "__main__":
    print("Testing GoGoTrade Backend Search Functionality")
    print("=" * 50)
    test_search_endpoint()
