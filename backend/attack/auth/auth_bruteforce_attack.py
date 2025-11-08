#!/usr/bin/env python3
"""
Brute Force Attack Test
Test the auth module's protection against brute force attacks
"""
import requests
import time
from typing import List, Tuple

# Target URL for testing
BASE_URL = "http://127.0.0.1:8000"

def brute_force_attack(email: str, password_list: List[str]) -> Tuple[bool, str]:
    """
    Brute force attack test
    Attempt to brute force user account using password list
    
    Args:
        email: Target email address
        password_list: List of passwords to try
        
    Returns:
        (success status, token if successful)
    """
    print(f"\n[Attack Test] Starting brute force attack - Target email: {email}")
    print(f"[Attack Test] Attempting {len(password_list)} passwords...")
    
    success_count = 0
    failed_count = 0
    successful_password = None
    token = None
    
    for i, password in enumerate(password_list, 1):
        try:
            # Send login request
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and data.get("token"):
                    print(f"[✓] Attack successful! Password: {password}")
                    print(f"[✓] Token: {data.get('token')[:20]}...")
                    success_count += 1
                    successful_password = password
                    token = data.get("token")
                    break
            else:
                failed_count += 1
                if i % 10 == 0:
                    print(f"[Progress] Attempted {i}/{len(password_list)} passwords...")
            
            # Add delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"[Error] Request failed: {e}")
            failed_count += 1
    
    print(f"\n[Attack Results]")
    print(f"  - Success: {success_count}")
    print(f"  - Failed: {failed_count}")
    
    if successful_password:
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
    
    # Test email (modify according to actual situation)
    test_email = "alice.student@university.edu"
    
    success, token = brute_force_attack(test_email, common_passwords)
    
    if success:
        print("\n[Security Warning] System has brute force vulnerability!")
        print("Recommendation: Implement login rate limiting and account locking mechanism")
    else:
        print("\n[Security Test] Brute force attack successfully prevented")

if __name__ == "__main__":
    print("=" * 60)
    print("Auth Module - Brute Force Attack Test")
    print("=" * 60)
    
    test_common_passwords()
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)

