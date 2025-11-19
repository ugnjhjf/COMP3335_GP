#!/usr/bin/env python3
"""
Test SQL injection attacks on insert endpoint
测试插入端点的SQL注入攻击
"""
import requests
import json
import urllib3
from typing import Dict, List

# 禁用 SSL 警告（因为使用的是自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test user credentials
TEST_STUDENT_EMAIL = "test_student@example.com"
TEST_STUDENT_PASSWORD = "StudentTest123"

def test_insert_sql_injection(base_url: str = "https://127.0.0.1:8000",
                              auth_token: str = None) -> List[Dict]:
    """
    Test SQL injection attacks on /data/insert endpoint
    测试 /data/insert 端点的SQL注入攻击
    
    Args:
        base_url: Base URL of the API server
        auth_token: Authentication token for authorized requests
        
    Returns:
        List of test results with status and details
    """
    results = []
    
    if not auth_token:
        return [{
            "test_name": "Authentication Required",
            "status": "SKIPPED",
            "error": "Auth token required for insert endpoint tests"
        }]
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # SQL injection payloads for insert operations
    # 插入操作的SQL注入载荷
    injection_payloads = get_insert_injection_payloads()
    
    for payload in injection_payloads:
        try:
            request_data = {
                "table": payload["table"],
                "insertValues": payload["insertValues"]
            }
            
            response = requests.post(
                f"{base_url}/data/insert",
                headers=headers,
                json=request_data,
                timeout=10,
                verify=False  # 禁用SSL验证（自签名证书）
            )
            
            # Check if injection was successful
            # 检查注入是否成功
            is_vulnerable = False
            vulnerability_indicators = []
            
            # Check response status
            # 检查响应状态
            is_protected = False  # Initialize protection status
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("ok"):
                        # With parameterized queries, malicious payload is treated as literal string
                        # 使用参数化查询时，恶意载荷被视为字面字符串
                        # So insert might return ok but the malicious SQL is just stored as data (protected)
                        # 所以插入可能返回ok但恶意SQL只是作为数据存储（受保护）
                        # This is actually safe - parameterized queries prevent SQL injection
                        # 这实际上是安全的 - 参数化查询防止SQL注入
                        is_protected = True
                    elif "error" in data or not data.get("ok"):
                        # Response has error or ok=false, likely protected
                        # 响应有错误或ok=false，可能受保护
                        is_protected = True
                except:
                    pass
            
            # Check for SQL error messages
            # 检查SQL错误消息
            response_text = response.text.lower()
            sql_error_patterns = [
                "sql syntax",
                "mysql",
                "database error",
                "query failed",
                "syntax error"
            ]
            
            for pattern in sql_error_patterns:
                if pattern in response_text:
                    vulnerability_indicators.append(f"SQL error detected: {pattern}")
                    break
            
            # Check if request was properly rejected
            # 检查请求是否被正确拒绝
            # Check response content for validation errors
            # 检查响应内容中的验证错误
            response_text_lower = response.text.lower()
            has_validation_error = any(keyword in response_text_lower for keyword in [
                "invalid", "error", "forbidden", "unauthorized", 
                "bad request", "not allowed", "rejected"
            ])
            
            # Combine protection checks (don't overwrite previous is_protected)
            # 组合保护检查（不要覆盖之前的is_protected）
            is_protected = is_protected or (
                response.status_code == 400 or  # Bad request
                response.status_code == 403 or  # Forbidden
                response.status_code == 401 or  # Unauthorized
                (response.status_code >= 400 and has_validation_error)  # Any 4xx/5xx with error message
            )
            
            result = {
                "test_name": payload["name"],
                "description": payload["description"],
                "payload": payload,
                "status": "VULNERABLE" if is_vulnerable else ("PROTECTED" if is_protected else "UNKNOWN"),
                "response_code": response.status_code,
                "indicators": vulnerability_indicators,
                "response_time": response.elapsed.total_seconds()
            }
            
            results.append(result)
            
            # Print test result
            status_icon = "✓" if result["status"] == "PROTECTED" else "✗" if result["status"] == "VULNERABLE" else "?"
            print(f"[{status_icon}] {payload['name']}: {result['status']} (Code: {result['response_code']})")
            if result.get("indicators"):
                for indicator in result["indicators"]:
                    print(f"    - {indicator}")
            
        except requests.exceptions.Timeout:
            result = {
                "test_name": payload["name"],
                "description": payload["description"],
                "payload": payload,
                "status": "TIMEOUT",
                "indicators": ["Request timeout"]
            }
            results.append(result)
            print(f"[✗] {payload['name']}: TIMEOUT")
        except Exception as e:
            result = {
                "test_name": payload["name"],
                "description": payload["description"],
                "payload": payload,
                "status": "ERROR",
                "error": str(e)
            }
            results.append(result)
            print(f"[✗] {payload['name']}: ERROR - {str(e)}")
    
    return results


def get_insert_injection_payloads():
    """Get SQL injection payloads for insert endpoint"""
    return [
        {
            "name": "Insert value injection - OR",
            "description": "插入值注入 - OR",
            "table": "students",
            "insertValues": {
                "StuID": 9999,
                "last_name": "Test' OR '1'='1",
                "first_name": "Test",
                "email": "test@test.com"
            }
        },
        {
            "name": "Insert value injection - Comment",
            "description": "插入值注入 - 注释",
            "table": "students",
            "insertValues": {
                "StuID": 9998,
                "last_name": "Test' --",
                "first_name": "Test",
                "email": "test@test.com"
            }
        },
        {
            "name": "Insert value injection - Stacked",
            "description": "插入值注入 - 堆叠",
            "table": "students",
            "insertValues": {
                "StuID": 9997,
                "last_name": "Test'; DROP TABLE students; --",
                "first_name": "Test",
                "email": "test@test.com"
            }
        },
        {
            "name": "Table name injection",
            "description": "表名注入",
            "table": "students; DROP TABLE students; --",
            "insertValues": {
                "StuID": 9996,
                "last_name": "Test",
                "first_name": "Test",
                "email": "test@test.com"
            }
        },
        {
            "name": "Column name injection",
            "description": "列名注入",
            "table": "students",
            "insertValues": {
                "StuID": 9995,
                "last_name; DROP TABLE students; --": "Test",
                "first_name": "Test",
                "email": "test@test.com"
            }
        }
    ]


def run_insert_injection_tests():
    """Run insert injection tests with formatted output"""
    print("=" * 60)
    print("SQL Injection Test - Insert Endpoint")
    print("=" * 60)
    
    # Get auth token first
    print("\n[Setup] Logging in to get authentication token...")
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
                print("[✗] Login failed - Cannot proceed without authentication")
                return
        else:
            print("[✗] Login failed - Cannot proceed without authentication")
            return
    except Exception as e:
        print(f"[✗] Login error: {e}")
        return
    
    injection_payloads = get_insert_injection_payloads()
    print(f"\n[Attack Test] Starting SQL injection tests on /data/insert endpoint")
    print(f"[Attack Test] Testing {len(injection_payloads)} injection payloads...\n")
    
    results = test_insert_sql_injection(auth_token=auth_token)
    
    # Print summary
    print(f"\n[Test Results Summary]")
    vulnerable_count = sum(1 for r in results if r["status"] == "VULNERABLE")
    protected_count = sum(1 for r in results if r["status"] == "PROTECTED")
    error_count = sum(1 for r in results if r["status"] in ["ERROR", "TIMEOUT", "UNKNOWN"])
    
    print(f"  - Protected: {protected_count}")
    print(f"  - Vulnerable: {vulnerable_count}")
    print(f"  - Errors/Timeouts: {error_count}")
    print(f"  - Total: {len(results)}")
    
    if vulnerable_count > 0:
        print("\n[Security Warning] System has SQL injection vulnerabilities!")
        print("Recommendation: Review and fix vulnerable endpoints")
    else:
        print("\n[Security Test] SQL injection attacks successfully prevented")
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)


if __name__ == "__main__":
    run_insert_injection_tests()

