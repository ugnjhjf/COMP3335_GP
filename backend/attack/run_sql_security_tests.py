#!/usr/bin/env python3
"""
Main SQL security test runner
SQL安全测试主运行程序

This script runs comprehensive SQL injection tests against the API
此脚本对API运行全面的SQL注入测试
"""
import sys
import os
import json
import requests
from datetime import datetime
from typing import Dict, List

# Add parent directory to path for imports
# 将父目录添加到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test functions
# 导入测试函数
from attack.sql.test_query_injection import test_query_sql_injection
from attack.sql.test_update_injection import test_update_sql_injection
from attack.sql.test_insert_injection import test_insert_sql_injection
from attack.sql.test_delete_injection import test_delete_sql_injection
from attack.sql.test_security_monitoring import test_security_monitoring

def get_auth_token(base_url: str, email: str = None, password: str = None) -> str:
    """
    Get authentication token for testing
    获取用于测试的认证令牌
    
    Args:
        base_url: Base URL of the API server
        email: User email (optional, uses default test user)
        password: User password (optional, uses default test password)
        
    Returns:
        Authentication token or None
    """
    # Default test credentials (adjust as needed)
    # 默认测试凭据（根据需要调整）
    # Use credentials from setup_test_user.py if available
    # 如果可用，使用 setup_test_user.py 创建的凭据
    test_email = email or "test_student@example.com"
    test_password = password or "StudentTest123"
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("token"):
                print(f"✓ Successfully authenticated as {test_email}")
                return data["token"]
            else:
                error_msg = data.get('error', 'Unknown error')
                print(f"✗ Authentication failed: {error_msg}")
                if "password" in error_msg.lower() or "8 characters" in error_msg.lower():
                    print("\n  💡 The default test user may not exist yet.")
                    print("     Run 'python backend/setup_test_user.py' to create test users.")
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'No error message')
                print(f"  Error message: {error_msg}")
                
                # Provide helpful hints for common errors
                # 为常见错误提供有用的提示
                if response.status_code == 400:
                    if "password" in error_msg.lower() and "8 characters" in error_msg.lower():
                        print("\n  💡 Password validation failed. The test user may not exist.")
                        print("     Run 'python backend/setup_test_user.py' to create test users with valid passwords.")
                    elif "email" in error_msg.lower():
                        print("\n  💡 Email validation failed. Check the email format.")
                elif response.status_code == 401:
                    print("\n  💡 Invalid credentials. The test user may not exist.")
                    print("     Run 'python backend/setup_test_user.py' to create test users.")
            except:
                print(f"  Response: {response.text[:100]}")
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {base_url}")
        print("  Make sure the server is running: python backend/main.py")
    except requests.exceptions.Timeout:
        print(f"✗ Request to {base_url} timed out")
    except Exception as e:
        print(f"✗ Error getting auth token: {e}")
    
    print("\n💡 Tips to fix authentication:")
    print("   1. Create test users first:")
    print("      python backend/setup_test_user.py")
    print("\n   2. Then run tests again, or use specific credentials:")
    print("      python backend/attack/run_sql_security_tests.py \\")
    print("          --email test_student@example.com \\")
    print("          --password StudentTest123")
    print("\n⚠️  Some tests will be skipped without authentication")
    print("   (Login injection tests are in auth/auth_sql_injection_attack.py)")
    
    return None

def run_all_tests(base_url: str = "http://127.0.0.1:8000",
                  test_email: str = None,
                  test_password: str = None) -> Dict:
    """
    Run all SQL security tests
    运行所有SQL安全测试
    
    Args:
        base_url: Base URL of the API server
        test_email: Test user email
        test_password: Test user password
        
    Returns:
        Dictionary containing all test results
    """
    print("=" * 80)
    print("SQL Security Test Suite - SQL安全测试套件")
    print("=" * 80)
    print(f"Target URL: {base_url}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Get authentication token
    # 获取认证令牌
    print("Step 1: Getting authentication token...")
    print("步骤1: 获取认证令牌...")
    auth_token = get_auth_token(base_url, test_email, test_password)
    if auth_token:
        print("✓ Authentication token obtained")
        print("✓ 已获取认证令牌")
    else:
        print("✗ Could not get authentication token - some tests will be skipped")
        print("✗ 无法获取认证令牌 - 部分测试将被跳过")
    print()
    
    all_results = {
        "test_time": datetime.now().isoformat(),
        "base_url": base_url,
        "tests": {}
    }
    
    # Note: Login injection tests are now in auth/auth_sql_injection_attack.py
    # 注意：登录注入测试现在在 auth/auth_sql_injection_attack.py 中
    
    # Test 1: Query injection
    # 测试1: 查询注入
    if auth_token:
        print("Test 1: Testing query endpoint SQL injection...")
        print("测试1: 测试查询端点SQL注入...")
        query_results = test_query_sql_injection(base_url, auth_token)
        all_results["tests"]["query_injection"] = query_results
        print(f"  Completed: {len(query_results)} tests")
        print(f"  完成: {len(query_results)} 个测试")
    else:
        print("Test 1: Skipped (no auth token)")
        print("测试1: 已跳过（无认证令牌）")
        all_results["tests"]["query_injection"] = []
    print()
    
    # Test 2: Update injection
    # 测试2: 更新注入
    if auth_token:
        print("Test 2: Testing update endpoint SQL injection...")
        print("测试2: 测试更新端点SQL注入...")
        update_results = test_update_sql_injection(base_url, auth_token)
        all_results["tests"]["update_injection"] = update_results
        print(f"  Completed: {len(update_results)} tests")
        print(f"  完成: {len(update_results)} 个测试")
    else:
        print("Test 2: Skipped (no auth token)")
        print("测试2: 已跳过（无认证令牌）")
        all_results["tests"]["update_injection"] = []
    print()
    
    # Test 3: Insert injection
    # 测试3: 插入注入
    if auth_token:
        print("Test 3: Testing insert endpoint SQL injection...")
        print("测试3: 测试插入端点SQL注入...")
        insert_results = test_insert_sql_injection(base_url, auth_token)
        all_results["tests"]["insert_injection"] = insert_results
        print(f"  Completed: {len(insert_results)} tests")
        print(f"  完成: {len(insert_results)} 个测试")
    else:
        print("Test 3: Skipped (no auth token)")
        print("测试3: 已跳过（无认证令牌）")
        all_results["tests"]["insert_injection"] = []
    print()
    
    # Test 4: Delete injection
    # 测试4: 删除注入
    if auth_token:
        print("Test 4: Testing delete endpoint SQL injection...")
        print("测试4: 测试删除端点SQL注入...")
        delete_results = test_delete_sql_injection(base_url, auth_token)
        all_results["tests"]["delete_injection"] = delete_results
        print(f"  Completed: {len(delete_results)} tests")
        print(f"  完成: {len(delete_results)} 个测试")
    else:
        print("Test 4: Skipped (no auth token)")
        print("测试4: 已跳过（无认证令牌）")
        all_results["tests"]["delete_injection"] = []
    print()
    
    # Test 5: Security monitoring
    # 测试5: 安全监控
    print("Test 5: Testing security monitoring...")
    print("测试5: 测试安全监控...")
    monitoring_results = test_security_monitoring(base_url, auth_token)
    all_results["tests"]["security_monitoring"] = monitoring_results
    print(f"  Completed: {len(monitoring_results)} tests")
    print(f"  完成: {len(monitoring_results)} 个测试")
    print()
    
    return all_results

def generate_report(results: Dict) -> str:
    """
    Generate a human-readable test report
    生成人类可读的测试报告
    
    Args:
        results: Test results dictionary
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("SQL Security Test Report - SQL安全测试报告")
    report.append("=" * 80)
    report.append(f"Test Time: {results['test_time']}")
    report.append(f"Target: {results['base_url']}")
    report.append("=" * 80)
    report.append("")  # Empty line
    
    # Count vulnerabilities
    # 统计漏洞
    total_tests = 0
    vulnerable_tests = 0
    protected_tests = 0
    error_tests = 0
    
    for test_category, test_results in results["tests"].items():
        report.append(f"\n{test_category.upper().replace('_', ' ')}")
        report.append("-" * 80)
        
        for test in test_results:
            total_tests += 1
            status = test.get("status", "UNKNOWN")
            
            if status == "VULNERABLE":
                vulnerable_tests += 1
                report.append(f"  ❌ {test.get('test_name', 'Unknown')}: VULNERABLE")
                if test.get("indicators"):
                    for indicator in test["indicators"]:
                        report.append(f"     - {indicator}")
            elif status == "PROTECTED":
                protected_tests += 1
                report.append(f"  ✅ {test.get('test_name', 'Unknown')}: PROTECTED")
            elif status == "MONITORED":
                protected_tests += 1  # MONITORED is a good status
                report.append(f"  ✅ {test.get('test_name', 'Unknown')}: MONITORED")
            elif status in ["ERROR", "TIMEOUT", "SKIPPED"]:
                error_tests += 1
                report.append(f"  ⚠️  {test.get('test_name', 'Unknown')}: {status}")
                if test.get("error"):
                    report.append(f"     - {test['error']}")
            else:
                # UNKNOWN status - might need investigation
                error_tests += 1
                report.append(f"  ⚠️  {test.get('test_name', 'Unknown')}: {status}")
                if test.get("response_code"):
                    report.append(f"     - Response code: {test['response_code']}")
    
    # Summary
    # 摘要
    report.append("\n" + "=" * 80)
    report.append("SUMMARY - 摘要")
    report.append("=" * 80)
    report.append(f"Total Tests: {total_tests}")
    report.append(f"Vulnerable: {vulnerable_tests} ❌")
    report.append(f"Protected: {protected_tests} ✅")
    report.append(f"Errors/Skipped: {error_tests} ⚠️")
    report.append("=" * 80)
    
    if vulnerable_tests > 0:
        report.append("\n⚠️  WARNING: Vulnerabilities detected!")
        report.append("⚠️  警告: 检测到漏洞！")
    else:
        report.append("\n✅ All tests passed - No vulnerabilities detected")
        report.append("✅ 所有测试通过 - 未检测到漏洞")
    
    return "\n".join(report)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SQL Security Test Suite")
    parser.add_argument("--url", default="http://127.0.0.1:8000",
                       help="Base URL of the API server")
    parser.add_argument("--email", help="Test user email")
    parser.add_argument("--password", help="Test user password")
    parser.add_argument("--output", help="Output JSON file for results")
    parser.add_argument("--report", help="Output report file")
    
    args = parser.parse_args()
    
    # Run tests
    # 运行测试
    results = run_all_tests(args.url, args.email, args.password)
    
    # Generate report
    # 生成报告
    report = generate_report(results)
    print("\n" + report)
    
    # Save results
    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {args.output}")
    
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {args.report}")
    
    # Exit code based on vulnerabilities
    # 根据漏洞设置退出代码
    vulnerable_count = sum(
        sum(1 for t in tests if t.get("status") == "VULNERABLE")
        for tests in results["tests"].values()
    )
    
    sys.exit(1 if vulnerable_count > 0 else 0)

if __name__ == "__main__":
    main()

