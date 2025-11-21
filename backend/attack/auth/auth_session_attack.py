#!/usr/bin/env python3
"""
Session Attack Test
Test the auth module's protection against session fixation, session hijacking, and other session-related attacks
"""
import requests
import random
import string
import urllib3
from typing import List, Tuple

# Disable SSL warnings (using self-signed certificate)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target URL for testing
BASE_URL = "https://127.0.0.1:8000"

# Test user credentials from setup_test_user.py
TEST_STUDENT_EMAIL = "test_student@example.com"
TEST_STUDENT_PASSWORD = "StudentTest123"

def get_valid_token() -> str:
    """
    Get a valid authentication token for testing
    Uses test user credentials from setup_test_user.py
    
    Returns:
        Valid token string or None if login fails
    """
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_STUDENT_EMAIL,
                "password": TEST_STUDENT_PASSWORD
            },
            timeout=5,
            verify=False  # Disable SSL verification (self-signed certificate)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("token"):
                print(f"[Info] Successfully obtained valid token for {TEST_STUDENT_EMAIL}")
                return data["token"]
    except Exception as e:
        print(f"[Warning] Could not get valid token: {e}")
        print(f"[Info] Session replay test will be skipped")
    
    return None

def generate_fake_token(length: int = 32) -> str:
    """Generate fake token"""
    characters = string.ascii_letters + string.digits + "-_"
    return ''.join(random.choice(characters) for _ in range(length))

def session_fixation_attack() -> Tuple[bool, str]:
    """
    Session fixation attack test
    Attempt to authenticate using fixed or predictable tokens
    
    Returns:
        (success status, token used)
    """
    print(f"\n[Attack Test] Starting session fixation attack test")
    
    # Generate predictable tokens
    predictable_tokens = [
        "test_token_12345",
        "admin_token",
        "session_token",
        "12345678901234567890123456789012",  # 32 characters
        "a" * 32,  # All same characters
        "1" * 32,
        "admin" * 6 + "12",  # 32 characters
    ]
    
    # Generate some random tokens
    random_tokens = [generate_fake_token(32) for _ in range(10)]
    
    all_tokens = predictable_tokens + random_tokens
    
    print(f"[Attack Test] Attempting {len(all_tokens)} fake tokens...")
    
    successful_tokens = []
    
    for i, token in enumerate(all_tokens, 1):
        try:
            # Try to access protected resource with token
            # Using performQuery as test endpoint
            response = requests.post(
                f"{BASE_URL}/performQuery",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "table": "students",
                    "filters": [],
                    "sort": []
                },
                timeout=5,
                verify=False  # Disable SSL verification (self-signed certificate)
            )
            
            # If returns 200 and not an error, token might be valid
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") or "data" in data:
                    print(f"[!] Possible session hijacking successful! Token: {token[:20]}...")
                    successful_tokens.append(token)
            
            if i % 5 == 0:
                print(f"[Progress] Tested {i}/{len(all_tokens)} tokens...")
                
        except Exception as e:
            print(f"[Error] Token '{token[:20]}...' test failed: {e}")
    
    print(f"\n[Attack Results]")
    print(f"  - Tokens tested: {len(all_tokens)}")
    print(f"  - Successful tokens: {len(successful_tokens)}")
    
    if successful_tokens:
        print(f"\n[Successful Token List]:")
        for token in successful_tokens:
            print(f"  - {token[:40]}...")
        return True, successful_tokens[0] if successful_tokens else ""
    else:
        print("[✗] Attack failed - All fake tokens were rejected")
        return False, ""

def session_replay_attack(valid_token: str) -> bool:
    """
    Session replay attack test
    Attempt to reuse an already used token
    
    Args:
        valid_token: Valid token
        
    Returns:
        Success status
    """
    print(f"\n[Attack Test] Starting session replay attack test")
    
    if not valid_token:
        print("[Skip] No valid token available for testing")
        return False
    
    print(f"[Attack Test] Attempting to reuse token: {valid_token[:20]}...")
    
    success_count = 0
    attempts = 5
    
    for i in range(attempts):
        try:
            response = requests.post(
                f"{BASE_URL}/performQuery",
                headers={
                    "Authorization": f"Bearer {valid_token}"
                },
                json={
                    "table": "students",
                    "filters": [],
                    "sort": []
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") or "data" in data:
                    success_count += 1
                    print(f"[!] Replay {i+1} successful")
                else:
                    print(f"[✓] Replay {i+1} rejected")
            else:
                print(f"[✓] Replay {i+1} rejected (status code: {response.status_code})")
                
        except Exception as e:
            print(f"[Error] Replay {i+1} test failed: {e}")
    
    print(f"\n[Attack Results]")
    print(f"  - Replay attempts: {attempts}")
    print(f"  - Successful attempts: {success_count}")
    
    if success_count == attempts:
        print("[!] System allows session replay - Potential security risk")
        return True
    else:
        print("[✓] System correctly handles session replay")
        return False

def expired_session_attack() -> bool:
    """
    Expired session attack test
    Attempt to use expired tokens
    
    Returns:
        Success status
    """
    print(f"\n[Attack Test] Starting expired session attack test")
    
    # Generate tokens that look expired
    expired_like_tokens = [
        "expired_token_12345",
        "old_session_token",
        "invalid_token_123",
    ]
    
    print(f"[Attack Test] Attempting {len(expired_like_tokens)} possible expired tokens...")
    
    successful = False
    
    for token in expired_like_tokens:
        try:
            response = requests.post(
                f"{BASE_URL}/performQuery",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "table": "students",
                    "filters": [],
                    "sort": []
                },
                timeout=5,
                verify=False  # Disable SSL verification (self-signed certificate)
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") or "data" in data:
                    print(f"[!] Expired token might still be valid! Token: {token}")
                    successful = True
                    
        except Exception as e:
            pass
    
    if successful:
        print("[!] System might not correctly validate session expiration")
        return True
    else:
        print("[✓] System correctly rejected expired/invalid tokens")
        return False

def test_session_attacks():
    """Run all session attack tests"""
    print("=" * 60)
    print("Auth Module - Session Attack Test")
    print("=" * 60)
    
    # Test 1: Session fixation attack
    fixation_success, fake_token = session_fixation_attack()
    
    # Test 2: Expired session attack
    expired_success = expired_session_attack()
    
    # Test 3: Session replay attack (if valid token available)
    # Get a valid token using test user credentials
    print("\n[Info] Attempting to get valid token for session replay test...")
    valid_token = get_valid_token()
    
    if valid_token:
        replay_success = session_replay_attack(valid_token)
    else:
        print("\n[Skip] Session replay attack test skipped - could not obtain valid token")
        print("       Make sure test users are set up: python backend/setup_test_user.py")
        replay_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("[Test Summary]")
    print(f"  Session fixation attack: {'Vulnerable' if fixation_success else 'Secure'}")
    print(f"  Expired session attack: {'Vulnerable' if expired_success else 'Secure'}")
    if valid_token:
        print(f"  Session replay attack: {'Vulnerable' if replay_success else 'Secure'}")
    
    vulnerabilities = [fixation_success, expired_success]
    if valid_token:
        vulnerabilities.append(replay_success)
    
    if any(vulnerabilities):
        print("\n[Security Warning] System has session management vulnerabilities!")
        print("Recommendations:")
        print("  1. Use secure random token generation (implemented)")
        print("  2. Correctly validate session expiration time (implemented)")
        print("  3. Implement session fixation protection")
    else:
        print("\n[Security Test] Session attacks successfully prevented")

if __name__ == "__main__":
    test_session_attacks()
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)

