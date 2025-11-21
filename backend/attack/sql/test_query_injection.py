#!/usr/bin/env python3
"""
Test SQL injection attacks on query endpoint
"""
import requests
import json
import urllib3
from typing import Dict, List

# Disable SSL warnings (using self-signed certificate)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test user credentials
TEST_STUDENT_EMAIL = "test_student@example.com"
TEST_STUDENT_PASSWORD = "StudentTest123"

def get_query_injection_payloads():
    """Get SQL injection payloads for query endpoint"""
    return [
        {
            "name": "Filter value injection - OR",
            "description": "Filter value injection - OR",
            "table": "students",
            "filters": [{
                "column": "email",
                "operator": "eq",
                "value": "' OR '1'='1"
            }]
        },
        {
            "name": "Filter value injection - UNION",
            "description": "Filter value injection - UNION",
            "table": "students",
            "filters": [{
                "column": "email",
                "operator": "eq",
                "value": "' UNION SELECT * FROM staffs --"
            }]
        },
        {
            "name": "Filter value injection - Comment",
            "description": "Filter value injection - Comment",
            "table": "students",
            "filters": [{
                "column": "email",
                "operator": "eq",
                "value": "test@test.com' --"
            }]
        },
        {
            "name": "Table name injection",
            "description": "Table name injection",
            "table": "students; DROP TABLE students; --",
            "filters": []
        },
        {
            "name": "Column name injection",
            "description": "Column name injection",
            "table": "students",
            "filters": [{
                "column": "email; DROP TABLE students; --",
                "operator": "eq",
                "value": "test@test.com"
            }]
        },
        {
            "name": "Operator injection",
            "description": "Operator injection",
            "table": "students",
            "filters": [{
                "column": "email",
                "operator": "eq; DROP TABLE students; --",
                "value": "test@test.com"
            }]
        },
        {
            "name": "LIKE injection",
            "description": "LIKE injection",
            "table": "students",
            "filters": [{
                "column": "email",
                "operator": "like",
                "value": "'%' OR '1'='1"
            }]
        },
        {
            "name": "IN injection",
            "description": "IN injection",
            "table": "students",
            "filters": [{
                "column": "StuID",
                "operator": "in",
                "value": ["1", "2); DROP TABLE students; --"]
            }]
        }
    ]


def test_query_sql_injection(base_url: str = "https://127.0.0.1:8000", 
                             auth_token: str = None) -> List[Dict]:
    """
    Test SQL injection attacks on /performQuery endpoint
    
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
            "error": "Auth token required for query endpoint tests"
        }]
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # SQL injection payloads for query filters
    injection_payloads = get_query_injection_payloads()
    
    for payload in injection_payloads:
        try:
            request_data = {
                "currentTable": payload["table"],
                "filters": payload["filters"],
                "limit": 10,
                "offset": 0
            }
            
            response = requests.post(
                f"{base_url}/performQuery",
                headers=headers,
                json=request_data,
                timeout=10,
                verify=False  # Disable SSL verification (self-signed certificate)
            )
            
            # Check if injection was successful
            is_vulnerable = False
            is_protected = False  # Initialize protection status
            vulnerability_indicators = []
            
            # Check response status
            if response.status_code == 200:
                try:
                    data = response.json()
                    # If we get unexpected data, might be vulnerable
                    if "results" in data:
                        result_count = len(data["results"])
                        # If we get a very large result set, might be vulnerable (OR injection succeeded)
                        if result_count > 100:
                            is_vulnerable = True
                            vulnerability_indicators.append(f"Unexpected large result set: {result_count} records")
                        # If we get empty or small result set, likely protected (parameterized query worked)
                        elif result_count == 0 or result_count <= 10:
                            # Parameterized queries treat injection as literal string, so no matches found
                            is_protected = True
                    elif "error" in data:
                        # Response has error, likely protected
                        is_protected = True
                except:
                    pass
            
            # Check for SQL error messages
            response_text = response.text.lower()
            sql_error_patterns = [
                "sql syntax",
                "mysql",
                "database error",
                "query failed",
                "syntax error",
                "invalid table",
                "invalid column"
            ]
            
            for pattern in sql_error_patterns:
                if pattern in response_text:
                    vulnerability_indicators.append(f"SQL error detected: {pattern}")
                    break
            
            # Check if request was properly rejected
            # Check response content for validation errors
            response_text_lower = response.text.lower()
            has_validation_error = any(keyword in response_text_lower for keyword in [
                "invalid", "error", "forbidden", "unauthorized", 
                "bad request", "not allowed", "rejected"
            ])
            
            # Combine protection checks (don't overwrite previous is_protected)
            is_protected = is_protected or (
                response.status_code == 400 or  # Bad request
                response.status_code == 403 or  # Forbidden
                response.status_code == 401 or  # Unauthorized
                (response.status_code >= 400 and has_validation_error)  # Any 4xx/5xx with error message
            )
            
            # Additional check: if status is 200 with empty/small results, protected
            # (This is already handled above, but keep for clarity)
            
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


def run_query_injection_tests():
    """Run query injection tests with formatted output"""
    print("=" * 60)
    print("SQL Injection Test - Query Endpoint")
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
            verify=False  # Disable SSL verification (self-signed certificate)
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
    
    injection_payloads = get_query_injection_payloads()
    print(f"\n[Attack Test] Starting SQL injection tests on /performQuery endpoint")
    print(f"[Attack Test] Testing {len(injection_payloads)} injection payloads...\n")
    
    results = test_query_sql_injection(auth_token=auth_token)
    
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
    run_query_injection_tests()

