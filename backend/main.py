#!/usr/bin/env python3
"""
University Data API Server - Main Entry Point
"""
from http.server import HTTPServer
from api_handler import SimpleAPIServer
from encryption import ensureEncryptionKey

def run(host="127.0.0.1", port=8000):
    """Start HTTP server"""
    ensureEncryptionKey()
    # Database connection will be established on first login attempt
    # 数据库连接将在首次登录尝试时建立
    
    httpd = HTTPServer((host, port), SimpleAPIServer)
    print(f"Serving on http://{host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
