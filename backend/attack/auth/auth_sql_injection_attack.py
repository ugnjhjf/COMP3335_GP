#!/usr/bin/env python3
"""
SQL Injection Attack Test
Test the auth module's protection against SQL injection attacks
"""
import requests
import urllib3
from typing import List, Tuple

# Disable SSL warnings (using self-signed certificate)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target URL for testing
BASE_URL = "https://127.0.0.1:8000"

def sql_injection_attack(email_payloads: List[str], password: str = "test123") -> Tuple[bool, List[str]]:
    """
    SQL injection attack test
    Attempt SQL injection payloads in email field
    
    Args:
        email_payloads: List of SQL injection payloads
        password: Test password
        
    Returns:
        (whether injection was successful, list of successful payloads)
    """
    print(f"\n[Attack Test] Starting SQL injection attack test")
    print(f"[Attack Test] Attempting {len(email_payloads)} SQL injection payloads...")
    
    successful_payloads = []
    vulnerable = False
    
    for i, payload in enumerate(email_payloads, 1):
        try:
            # Send login request
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": payload,
                    "password": password
                },
                timeout=5,
                verify=False  # Disable SSL verification (self-signed certificate)
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                # If token is returned, injection might be successful
                if data.get("ok") and data.get("token"):
                    print(f"[!] Possible SQL injection successful! Payload: {payload}")
                    successful_payloads.append(payload)
                    vulnerable = True
                else:
                    # Check if error message contains SQL errors
                    error_msg = str(data.get("error", "")).lower()
                    if any(keyword in error_msg for keyword in ["sql", "mysql", "syntax", "database"]):
                        print(f"[!] SQL error message detected! Payload: {payload}")
                        print(f"    Error: {data.get('error')}")
                        successful_payloads.append(payload)
                        vulnerable = True
            
            # Check response time (time-based blind injection)
            if response.elapsed.total_seconds() > 2:
                print(f"[!] Unusually long response time ({response.elapsed.total_seconds():.2f}s)! Payload: {payload}")
                successful_payloads.append(payload)
                vulnerable = True
            
            if i % 10 == 0:
                print(f"[Progress] Tested {i}/{len(email_payloads)} payloads...")
                
        except requests.exceptions.Timeout:
            print(f"[!] Request timeout! Payload: {payload}")
            successful_payloads.append(payload)
            vulnerable = True
        except Exception as e:
            print(f"[Error] Payload '{payload}' test failed: {e}")
    
    print(f"\n[Attack Results]")
    print(f"  - Payloads tested: {len(email_payloads)}")
    print(f"  - Successful payloads: {len(successful_payloads)}")
    print(f"  - System vulnerable: {'Yes' if vulnerable else 'No'}")
    
    if successful_payloads:
        print(f"\n[Successful Payload List]:")
        for payload in successful_payloads:
            print(f"  - {payload}")
    
    return vulnerable, successful_payloads

def test_sql_injection_payloads():
    """Test SQL injection payloads"""
    # SQL injection payload list
    sql_payloads = [
        # Basic SQL injection
        "admin' OR '1'='1",
        "admin' OR '1'='1'--",
        "admin' OR '1'='1'#",
        "admin' OR '1'='1'/*",
        "' OR 1=1--",
        "' OR '1'='1",
        "' OR 1=1#",
        "' OR 'a'='a",
        "' OR ''='",
        
        # Union injection
        "admin' UNION SELECT NULL--",
        "' UNION SELECT * FROM users--",
        
        # Boolean-based blind
        "' OR '1'='1' AND '1'='1",
        "' OR '1'='1' AND '1'='2",
        
        # Time-based blind
        "admin'; WAITFOR DELAY '00:00:05'--",
        "admin'; SLEEP(5)--",
        "' OR SLEEP(5)--",
        
        # Stacked queries
        "admin'; DROP TABLE users--",
        "'; DELETE FROM users--",
        
        # Comment bypass
        "admin'/**/OR/**/1=1--",
        "admin'/*comment*/OR/*comment*/1=1--",
        
        # Encoding bypass
        "admin%27%20OR%20%271%27%3D%271",
        "admin' OR CHAR(49)=CHAR(49)--",
        
        # Other variants
        "admin') OR ('1'='1",
        "admin' OR 1=1 LIMIT 1--",
        "' OR 1=1 LIMIT 1--",
        "admin' OR 'x'='x",
    ]
    
    vulnerable, successful_payloads = sql_injection_attack(sql_payloads)
    
    if vulnerable:
        print("\n[Security Warning] System has SQL injection vulnerability!")
        print("Recommendations:")
        print("  1. Use parameterized queries (implemented)")
        print("  2. Validate and sanitize all user inputs")
        print("  3. Implement principle of least privilege")
    else:
        print("\n[Security Test] SQL injection attack successfully prevented")
        print("System uses parameterized queries, effectively preventing SQL injection")

if __name__ == "__main__":
    print("=" * 60)
    print("Auth Module - SQL Injection Attack Test")
    print("=" * 60)
    
    test_sql_injection_payloads()
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)

