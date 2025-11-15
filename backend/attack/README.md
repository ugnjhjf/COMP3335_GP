# SQL Security Test Suite
# SQL安全测试套件

## 概述 (Overview)

This directory contains comprehensive SQL injection security tests for the ComputingU database application.

此目录包含针对ComputingU数据库应用程序的全面SQL注入安全测试。

## 文件结构 (File Structure)

```
backend/attack/
├── auth/
│   ├── auth_bruteforce_attack.py      # Brute force attack tests
│   ├── auth_session_attack.py         # Session attack tests
│   ├── auth_sql_injection_attack.py   # Login endpoint SQL injection tests
│   └── README.md                      # Auth module documentation
├── sql/
│   ├── test_query_injection.py        # Query endpoint SQL injection tests
│   ├── test_update_injection.py       # Update endpoint SQL injection tests
│   ├── test_insert_injection.py       # Insert endpoint SQL injection tests
│   ├── test_delete_injection.py       # Delete endpoint SQL injection tests
│   └── test_security_monitoring.py     # Security monitoring tests
├── run_sql_security_tests.py          # Main test runner
├── SQL_SECURITY_TEST_CHANGELOG.md     # Change log (变更日志)
├── SQL_SECURITY_TEST_TUTORIAL_CN.md   # Tutorial in Chinese (中文教程)
├── Jerry_Tutorial_version5_CN.md      # Complete tutorial (完整教程)
└── README.md                          # This file
```

## 快速开始 (Quick Start)

### 运行所有测试 (Run All Tests)

```bash
python backend/attack/run_sql_security_tests.py
```

### 运行特定测试 (Run Specific Test)

```python
# Login endpoint SQL injection test
from attack.auth.auth_sql_injection_attack import test_sql_injection_payloads
test_sql_injection_payloads()

# Query endpoint test
from attack.sql.test_query_injection import test_query_sql_injection
results = test_query_sql_injection("http://127.0.0.1:8000", auth_token)
```

## 设计原则 (Design Principles)

- **一个文件一个函数** (One file per function)
- **单一职责** (Single responsibility)
- **易于维护和扩展** (Easy to maintain and extend)

## 文档 (Documentation)

- **中文教程**: [SQL_SECURITY_TEST_TUTORIAL_CN.md](SQL_SECURITY_TEST_TUTORIAL_CN.md)
- **变更日志**: [SQL_SECURITY_TEST_CHANGELOG.md](SQL_SECURITY_TEST_CHANGELOG.md)

## 测试覆盖 (Test Coverage)

### Auth Module Tests (auth/)
- ✅ Brute force attacks (`auth_bruteforce_attack.py`)
- ✅ Session attacks (`auth_session_attack.py`)
- ✅ Login SQL injection (`auth_sql_injection_attack.py`)

### Endpoint SQL Injection Tests (sql/)
- ✅ Query endpoint (`/performQuery`) - `sql/test_query_injection.py`
- ✅ Update endpoint (`/data/update`) - `sql/test_update_injection.py`
- ✅ Insert endpoint (`/data/insert`) - `sql/test_insert_injection.py`
- ✅ Delete endpoint (`/data/delete`) - `sql/test_delete_injection.py`

### Security Monitoring
- ✅ Security monitoring and logging - `sql/test_security_monitoring.py`

## 注意事项 (Notes)

⚠️ **重要**: 只在测试环境中运行这些测试，不要在生产环境运行！

Important: Only run these tests in a test environment, not in production!

