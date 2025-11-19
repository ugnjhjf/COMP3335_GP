#!/usr/bin/env python3
"""
Test security monitoring and logging functionality
测试安全监控和日志记录功能
"""
import requests
import json
import time
import urllib3
from typing import Dict, List
import os

# 禁用 SSL 警告（因为使用的是自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test user credentials
TEST_STUDENT_EMAIL = "test_student@example.com"
TEST_STUDENT_PASSWORD = "StudentTest123"

def test_security_monitoring(base_url: str = "https://127.0.0.1:8000",
                             auth_token: str = None) -> List[Dict]:
    """
    Test if security monitoring detects and logs SQL injection attempts
    测试安全监控是否检测并记录SQL注入尝试
    
    Args:
        base_url: Base URL of the API server
        auth_token: Authentication token for authorized requests
        
    Returns:
        List of test results with status and details
    """
    results = []
    
    # Test payloads that should trigger security monitoring
    # 应该触发安全监控的测试载荷
    test_payloads = [
        {
            "name": "SQL injection in login",
            "description": "登录中的SQL注入",
            "endpoint": "/auth/login",
            "method": "POST",
            "payload": {
                "email": "' OR '1'='1",
                "password": "test"
            }
        },
        {
            "name": "SQL injection in query",
            "description": "查询中的SQL注入",
            "endpoint": "/performQuery",
            "method": "POST",
            "payload": {
                "currentTable": "students",
                "filters": [{
                    "column": "email",
                    "operator": "eq",
                    "value": "' OR '1'='1"
                }]
            },
            "requires_auth": True
        }
    ]
    
    # Check log files after tests
    # 测试后检查日志文件
    log_files = [
        "backend/logs/app.log",
        "backend/logs/database.log"
    ]
    
    for test in test_payloads:
        try:
            # Send malicious request
            # 发送恶意请求
            if test["method"] == "POST":
                headers = {"Content-Type": "application/json"}
                if test.get("requires_auth") and auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"
                
                response = requests.post(
                    f"{base_url}{test['endpoint']}",
                    headers=headers,
                    json=test["payload"],
                    timeout=5,
                    verify=False  # 禁用SSL验证（自签名证书）
                )
            
            # Wait a bit for logging
            # 等待日志记录
            time.sleep(0.5)
            
            # Check if logs were created/updated
            # 检查日志是否被创建/更新
            log_indicators = []
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        # Check file modification time
                        # 检查文件修改时间
                        mtime = os.path.getmtime(log_file)
                        if time.time() - mtime < 10:  # Modified in last 10 seconds
                            log_indicators.append(f"{log_file} was recently modified")
                        
                        # Check file content for security events
                        # 检查文件内容中的安全事件
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if "sql_injection" in content.lower() or "security" in content.lower():
                                log_indicators.append(f"Security event found in {log_file}")
                    except Exception as e:
                        pass
            
            result = {
                "test_name": test["name"],
                "description": test["description"],
                "status": "MONITORED" if log_indicators else "NOT_MONITORED",
                "log_indicators": log_indicators,
                "response_code": response.status_code if 'response' in locals() else None
            }
            
            results.append(result)
            
            # Print test result
            status_icon = "✓" if result["status"] == "MONITORED" else "✗"
            print(f"[{status_icon}] {test['name']}: {result['status']}")
            if result.get("log_indicators"):
                for indicator in result["log_indicators"]:
                    print(f"    - {indicator}")
            
        except Exception as e:
            result = {
                "test_name": test["name"],
                "description": test["description"],
                "status": "ERROR",
                "error": str(e)
            }
            results.append(result)
            print(f"[✗] {test['name']}: ERROR - {str(e)}")
    
    return results


def run_security_monitoring_tests():
    """Run security monitoring tests with formatted output"""
    print("=" * 60)
    print("Security Monitoring Test")
    print("=" * 60)
    
    # Get auth token first (for authenticated tests)
    print("\n[Setup] Logging in to get authentication token...")
    auth_token = None
    try:
        login_response = requests.post(
            "https://127.0.0.1:8000/auth/login",
            json={
                "email": TEST_STUDENT_EMAIL,
                "password": TEST_STUDENT_PASSWORD
            },
            timeout=5,
            verify=False  # 禁用SSL验证（自签名证书）
        )
        if login_response.status_code == 200:
            data = login_response.json()
            if data.get("ok") and data.get("token"):
                auth_token = data.get("token")
                print(f"[✓] Login successful, token obtained")
            else:
                print("[!] Login failed - Some tests may be skipped")
        else:
            print("[!] Login failed - Some tests may be skipped")
    except Exception as e:
        print(f"[!] Login error: {e} - Some tests may be skipped")
    
    print(f"\n[Attack Test] Starting security monitoring tests")
    print(f"[Attack Test] Testing security event logging...\n")
    
    results = test_security_monitoring(auth_token=auth_token)
    
    # Print summary
    print(f"\n[Test Results Summary]")
    monitored_count = sum(1 for r in results if r["status"] == "MONITORED")
    not_monitored_count = sum(1 for r in results if r["status"] == "NOT_MONITORED")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"  - Monitored: {monitored_count}")
    print(f"  - Not Monitored: {not_monitored_count}")
    print(f"  - Errors: {error_count}")
    print(f"  - Total: {len(results)}")
    
    if not_monitored_count > 0:
        print("\n[Security Warning] Some security events are not being monitored!")
        print("Recommendation: Review and enhance security monitoring")
    else:
        print("\n[Security Test] Security monitoring is working correctly")
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)


if __name__ == "__main__":
    run_security_monitoring_tests()

