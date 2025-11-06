#!/usr/bin/env python3
"""
University Data API Server - Main Entry Point
"""
from http.server import HTTPServer
from db_connector import test_db_connection
from api_handler import SimpleAPIServer

def run(host="127.0.0.1", port=8000):
    """Start HTTP server"""
    # Test database connection
    print("Testing database connection...")
    success, message = test_db_connection()
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        print("Warning: Server will continue to start, but database operations may fail")
    
    httpd = HTTPServer((host, port), SimpleAPIServer)
    print(f"Serving on http://{host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
