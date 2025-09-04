#!/usr/bin/env python3
"""
Simple Python HTTP server to serve GoGoTrade React build
This bypasses all Node.js issues
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
BUILD_DIR = "frontend/build"

class GoGoTradeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BUILD_DIR, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Check if build directory exists
    if not os.path.exists(BUILD_DIR):
        print(f"❌ Error: Build directory '{BUILD_DIR}' not found!")
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"🔍 Available directories: {list(Path('.').glob('*'))}")
        return
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), GoGoTradeHandler) as httpd:
            print(f"🚀 GoGoTrade Python Server Starting...")
            print(f"📂 Serving from: {os.path.abspath(BUILD_DIR)}")
            print(f"🌐 Server running on http://localhost:{PORT}")
            print(f"⏰ Started at: {__import__('datetime').datetime.now()}")
            print(f"🔥 Press Ctrl+C to stop")
            print(f"=" * 50)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
