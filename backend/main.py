#!/usr/bin/env python3
"""
University Data API Server - Main Entry Point (HTTPS)
"""
import ssl
from pathlib import Path
from http.server import HTTPServer
from api_handler import SimpleAPIServer
from encryption import ensureEncryptionKey

def run(host="127.0.0.1", port=8000, cert_file="../security/cert.pem", key_file="../security/key.pem"):
    """Start HTTPS server"""
    ensureEncryptionKey()

    cert_path = Path(cert_file)
    key_path = Path(key_file)
    if not cert_path.exists() or not key_path.exists():
        raise FileNotFoundError(
            f"TLS files not found. Expected {cert_path} and {key_path}. "
            "Generate them with OpenSSL or mkcert (see setup instructions)."
        )

    httpd = HTTPServer((host, port), SimpleAPIServer)

    # Create a secure SSLContext
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Reasonable defaults: TLS1.2+ and sane ciphers
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:@SECLEVEL=2")
    context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    # Wrap the server socket with TLS
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving on https://{host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Default to 8443 to avoid needing root for 443 during development
    run()
