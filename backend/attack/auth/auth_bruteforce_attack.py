#!/usr/bin/env python3
"""
Brute Force Attack Test
Test the auth module's protection against brute force attacks
"""
import requests
import time
import urllib3
from typing import List, Tuple, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Disable SSL warnings (using self-signed certificate)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target URL for testing
BASE_URL = "https://127.0.0.1:8000"

# Number of concurrent threads (adjust as needed)
MAX_WORKERS = 10

def create_session_with_retry():
    """Create requests session with retry mechanism"""
    session = requests.Session()
    
    # Disable SSL verification (using self-signed certificate)
    session.verify = False
    
    # Configure retry strategy (reduce retries to speed up)
    retry_strategy = Retry(
        total=1,  # Retry only once (reduce retries to speed up)
        backoff_factor=0.5,  # Retry interval: 0.5 seconds
        status_forcelist=[429, 500, 502, 503, 504],  # These status codes trigger retry
        allowed_methods=["POST", "GET"]  # Allowed retry methods
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def try_password(email: str, password: str, session: requests.Session) -> Optional[Tuple[str, str]]:
    """
    Try a single password
    
    Returns:
        (password, token) if successful, otherwise None
    """
    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            timeout=5  # Reduce timeout to speed up
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("token"):
                return (password, data.get("token"))
    except Exception:
        # Silently handle errors to speed up
        pass
    
    return None

def brute_force_attack(email: str, password_list: List[str], use_concurrent: bool = True) -> Tuple[bool, str]:
    """
    Brute force attack test
    Attempt to brute force user account using password list
    
    Args:
        email: Target email address
        password_list: List of passwords to try
        use_concurrent: Whether to use concurrent attack (default True, faster)
        
    Returns:
        (success status, token if successful)
    """
    print(f"\n[Attack Test] Starting brute force attack - Target email: {email}")
    print(f"[Attack Test] Attempting {len(password_list)} passwords...")
    if use_concurrent:
        print(f"[Attack Test] Using concurrent mode with {MAX_WORKERS} workers...")
    
    start_time = time.time()
    success_count = 0
    failed_count = 0
    successful_password = None
    token = None
    
    if use_concurrent:
        # Concurrent attack mode
        result_lock = threading.Lock()
        stop_flag = threading.Event()  # For quickly stopping all tasks
        completed = 0
        
        def worker(password: str):
            nonlocal successful_password, token, success_count, failed_count, completed
            
            # If password already found or stop signal received, return immediately
            if stop_flag.is_set() or successful_password:
                return None
            
            # Each thread uses its own session
            session = create_session_with_retry()
            result = try_password(email, password, session)
            session.close()
            
            with result_lock:
                # Check again if password already found (avoid duplicate processing)
                if stop_flag.is_set() or successful_password:
                    return None
                
                completed += 1
                if completed % 10 == 0:
                    print(f"[Progress] Attempted {completed}/{len(password_list)} passwords...")
                
                if result:
                    successful_password, token = result
                    success_count = 1
                    stop_flag.set()  # Set stop flag
                    return result
                else:
                    failed_count += 1
            
            return None
        
        # Use thread pool for concurrent execution
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(worker, pwd): pwd for pwd in password_list}
            
            for future in as_completed(futures):
                if stop_flag.is_set():
                    # Cancel remaining tasks
                    for f in futures:
                        f.cancel()
                    break
                try:
                    result = future.result(timeout=0.1)
                    if result:
                        break
                except Exception:
                    pass
    else:
        # Serial attack mode (keep original logic as fallback)
        session = create_session_with_retry()
        
        for i, password in enumerate(password_list, 1):
            result = try_password(email, password, session)
            
            if result:
                successful_password, token = result
                success_count = 1
                break
            
            failed_count += 1
            if i % 10 == 0:
                print(f"[Progress] Attempted {i}/{len(password_list)} passwords...")
            
            # Minimal delay (almost no delay)
            time.sleep(0.01)
        
        session.close()
    
    elapsed_time = time.time() - start_time
    
    print(f"\n[Attack Results]")
    print(f"  - Success: {success_count}")
    print(f"  - Failed: {failed_count}")
    print(f"  - Time elapsed: {elapsed_time:.2f} seconds")
    print(f"  - Speed: {len(password_list)/elapsed_time:.2f} attempts/second")
    
    if successful_password:
        print(f"[✓] Attack successful! Password: {successful_password}")
        print(f"[✓] Token: {token[:20]}...")
        return True, token
    else:
        print("[✗] Attack failed - All password attempts failed")
        return False, None

def test_common_passwords():
    """Test common password list"""
    # Common weak passwords list
    common_passwords = [
        "123456",
        "password",
        "12345678",
        "123456789",
        "1234567890",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
        "1234567",
        "sunshine",
        "princess",
        "dragon",
        "passw0rd",
        "master",
        "hello",
        "freedom",
        "whatever",
        "qazwsx",
        "trustno1",
        "654321",
        "jordan23",
        "harley",
        "password1",
        "shadow",
        "superman",
        "qwerty123",
        "michael",
        "football",
        "iloveyou",
        "123123",
        "admin123",
        "root",
        "toor",
        "test",
        "test123"
    ]
    
    # Test email - using test user from setup_test_user.py
    test_email = "test_student@example.com"
    
    success, token = brute_force_attack(test_email, common_passwords)
    
    if success:
        print("\n[Security Warning] System has brute force vulnerability!")
        print("Recommendation: Implement login rate limiting and account locking mechanism")
    else:
        print("\n[Security Test] Brute force attack failed (password not in list)")


if __name__ == "__main__":
    print("=" * 60)
    print("Auth Module - Brute Force Attack Test")
    print("=" * 60)
    
    test_common_passwords()
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)

