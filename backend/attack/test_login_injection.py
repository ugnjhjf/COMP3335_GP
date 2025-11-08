#!/usr/bin/env python3
"""
Test SQL injection attacks on login endpoint
测试登录端点的SQL注入攻击
"""
import requests
import json
from typing import Dict, List, Tuple

def test_login_sql_injection(base_url: str = "http://127.0.0.1:8000") -> List[Dict]:
    """
    Test SQL injection attacks on /auth/login endpoint
    测试 /auth/login 端点的SQL注入攻击
    
    Args:
        base_url: Base URL of the API server
        
    Returns:
        List of test results with status and details
    """
    results = []
    
    # SQL injection payloads for login
    # 登录SQL注入载荷
    injection_payloads = [
        {
            "name": "Basic OR injection",
            "description": "基础OR注入",
            "email": "' OR '1'='1",
            "password": "anything"
        },
        {
            "name": "Comment injection",
            "description": "注释注入",
            "email": "admin' --",
            "password": "anything"
        },
        {
            "name": "Union injection",
            "description": "联合查询注入",
            "email": "' UNION SELECT NULL, NULL, NULL --",
            "password": "anything"
        },
        {
            "name": "Boolean injection",
            "description": "布尔注入",
            "email": "' OR 1=1 --",
            "password": "anything"
        },
        {
            "name": "Time-based injection",
            "description": "基于时间的注入",
            "email": "' OR SLEEP(5) --",
            "password": "anything"
        },
        {
            "name": "Stacked queries",
            "description": "堆叠查询",
            "email": "'; DROP TABLE students; --",
            "password": "anything"
        },
        {
            "name": "Double quote injection",
            "description": "双引号注入",
            "email": '" OR "1"="1',
            "password": "anything"
        }
    ]
    
    for payload in injection_payloads:
        try:
            response = requests.post(
                f"{base_url}/auth/login",
                json={
                    "email": payload["email"],
                    "password": payload["password"]
                },
                timeout=10
            )
            
            # Check if injection was successful
            # 检查注入是否成功
            is_vulnerable = False
            vulnerability_indicators = []
            
            # Check response status
            # 检查响应状态
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("ok") and data.get("token"):
                        is_vulnerable = True
                        vulnerability_indicators.append("Authentication bypassed")
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
            
            # Check response time for time-based injection
            # 检查基于时间注入的响应时间
            if "sleep" in payload["email"].lower() and response.elapsed.total_seconds() > 4:
                vulnerability_indicators.append("Time-based injection detected")
            
            result = {
                "test_name": payload["name"],
                "description": payload["description"],
                "payload": payload["email"],
                "status": "VULNERABLE" if is_vulnerable else "PROTECTED",
                "response_code": response.status_code,
                "indicators": vulnerability_indicators,
                "response_time": response.elapsed.total_seconds()
            }
            
            results.append(result)
            
        except requests.exceptions.Timeout:
            results.append({
                "test_name": payload["name"],
                "description": payload["description"],
                "payload": payload["email"],
                "status": "TIMEOUT",
                "indicators": ["Request timeout - possible time-based injection"]
            })
        except Exception as e:
            results.append({
                "test_name": payload["name"],
                "description": payload["description"],
                "payload": payload["email"],
                "status": "ERROR",
                "error": str(e)
            })
    
    return results

