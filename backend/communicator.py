#!/usr/bin/env python3
import json
# Security enhancements
from security import get_allowed_origins, is_origin_allowed

def json_response(handler, status, data, headers=None):
    """Send JSON formatted HTTP response"""
    body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    # CORS configuration
    origin = handler.headers.get("Origin", "")
    allowed_origins = get_allowed_origins()
    if '*' in allowed_origins or is_origin_allowed(origin):
        handler.send_header("Access-Control-Allow-Origin", origin if origin else "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, X-User-ID, X-Key-Id")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Credentials", "true")
    if headers:
        for k, v in headers.items():
            handler.send_header(k, v)
    handler.end_headers()
    handler.wfile.write(body)

def text_response(handler, status, text, content_type="text/plain; charset=utf-8"):
    """Send text formatted HTTP response"""
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    # CORS configuration
    origin = handler.headers.get("Origin", "")
    allowed_origins = get_allowed_origins()
    if '*' in allowed_origins or is_origin_allowed(origin):
        handler.send_header("Access-Control-Allow-Origin", origin if origin else "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, X-User-ID, X-Key-Id")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Credentials", "true")
    handler.end_headers()
    handler.wfile.write(body)

def read_json(handler):
    """Read JSON data from HTTP request"""
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length == 0:
        return {}
    
    # Limit request body size to prevent DoS
    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
    if length > MAX_BODY_SIZE:
        raise ValueError(f"Request body too large: {length} bytes (max: {MAX_BODY_SIZE} bytes)")
    
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}
