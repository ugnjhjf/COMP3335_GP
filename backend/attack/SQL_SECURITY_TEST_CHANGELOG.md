# SQL Security Test Suite - Change Log
# SQL安全测试套件 - 变更日志

## 变更日期: 2024

### 新增文件 (New Files)

#### 1. `backend/attack/test_login_injection.py`
**功能:** 测试登录端点的SQL注入攻击  
**Function:** Test SQL injection attacks on login endpoint

**主要函数:**
- `test_login_sql_injection(base_url: str) -> List[Dict]`
  - 测试多种SQL注入载荷在登录端点
  - Tests various SQL injection payloads on login endpoint
  - 包括: OR注入、注释注入、联合查询注入、布尔注入、时间盲注、堆叠查询、双引号注入
  - Includes: OR injection, comment injection, union injection, boolean injection, time-based injection, stacked queries, double quote injection

**变更原因:**
- 登录端点是SQL注入攻击的常见目标
- Login endpoint is a common target for SQL injection attacks
- 需要验证参数化查询是否正确实现
- Need to verify parameterized queries are correctly implemented

---

#### 2. `backend/attack/test_query_injection.py`
**功能:** 测试查询端点的SQL注入攻击  
**Function:** Test SQL injection attacks on query endpoint

**主要函数:**
- `test_query_sql_injection(base_url: str, auth_token: str) -> List[Dict]`
  - 测试查询过滤器中的SQL注入
  - Tests SQL injection in query filters
  - 包括: 过滤器值注入、表名注入、列名注入、操作符注入、LIKE注入、IN注入
  - Includes: filter value injection, table name injection, column name injection, operator injection, LIKE injection, IN injection

**变更原因:**
- 查询端点处理用户输入的表名、列名和过滤值
- Query endpoint handles user input for table names, column names, and filter values
- 需要验证表名和列名的白名单验证是否有效
- Need to verify whitelist validation for table and column names is effective

---

#### 3. `backend/attack/test_update_injection.py`
**功能:** 测试更新端点的SQL注入攻击  
**Function:** Test SQL injection attacks on update endpoint

**主要函数:**
- `test_update_sql_injection(base_url: str, auth_token: str) -> List[Dict]`
  - 测试更新操作中的SQL注入
  - Tests SQL injection in update operations
  - 包括: 更新值注入、表名注入、列名注入、主键注入
  - Includes: update value injection, table name injection, column name injection, primary key injection

**变更原因:**
- 更新操作可能被恶意利用来修改或删除数据
- Update operations could be maliciously exploited to modify or delete data
- 需要验证更新值是否使用参数化查询
- Need to verify update values use parameterized queries

---

#### 4. `backend/attack/test_insert_injection.py`
**功能:** 测试插入端点的SQL注入攻击  
**Function:** Test SQL injection attacks on insert endpoint

**主要函数:**
- `test_insert_sql_injection(base_url: str, auth_token: str) -> List[Dict]`
  - 测试插入操作中的SQL注入
  - Tests SQL injection in insert operations
  - 包括: 插入值注入、表名注入、列名注入
  - Includes: insert value injection, table name injection, column name injection

**变更原因:**
- 插入操作可能被利用来注入恶意数据
- Insert operations could be exploited to inject malicious data
- 需要验证列名验证和转义是否有效
- Need to verify column name validation and escaping is effective

---

#### 5. `backend/attack/test_delete_injection.py`
**功能:** 测试删除端点的SQL注入攻击  
**Function:** Test SQL injection attacks on delete endpoint

**主要函数:**
- `test_delete_sql_injection(base_url: str, auth_token: str) -> List[Dict]`
  - 测试删除操作中的SQL注入
  - Tests SQL injection in delete operations
  - 包括: 主键注入、表名注入、键列名注入
  - Includes: primary key injection, table name injection, key column name injection

**变更原因:**
- 删除操作是最危险的，可能被利用来删除整个表
- Delete operations are most dangerous, could be exploited to delete entire tables
- 需要验证主键验证是否有效
- Need to verify primary key validation is effective

---

#### 6. `backend/attack/test_security_monitoring.py`
**功能:** 测试安全监控和日志记录功能  
**Function:** Test security monitoring and logging functionality

**主要函数:**
- `test_security_monitoring(base_url: str, auth_token: str) -> List[Dict]`
  - 测试安全监控是否检测并记录SQL注入尝试
  - Tests if security monitoring detects and logs SQL injection attempts
  - 检查日志文件是否记录安全事件
  - Checks if log files record security events

**变更原因:**
- 项目要求记录所有SQL注入尝试
- Project requirements specify logging all SQL injection attempts
- 需要验证安全监控模块是否正常工作
- Need to verify security monitoring module works correctly

---

#### 7. `backend/attack/run_sql_security_tests.py`
**功能:** SQL安全测试主运行程序  
**Function:** Main SQL security test runner

**主要函数:**
- `get_auth_token(base_url: str, email: str, password: str) -> str`
  - 获取用于测试的认证令牌
  - Get authentication token for testing

- `run_all_tests(base_url: str, test_email: str, test_password: str) -> Dict`
  - 运行所有SQL安全测试
  - Run all SQL security tests
  - 整合所有测试函数
  - Integrates all test functions

- `generate_report(results: Dict) -> str`
  - 生成人类可读的测试报告
  - Generate human-readable test report
  - 统计漏洞数量
  - Count vulnerabilities

**变更原因:**
- 需要一个统一的测试运行程序
- Need a unified test runner
- 方便自动化测试和CI/CD集成
- Convenient for automated testing and CI/CD integration

---

### 设计原则 (Design Principles)

#### 一个文件一个函数原则 (One File Per Function Principle)

所有测试函数都遵循"一个文件一个函数"原则：
All test functions follow the "one file per function" principle:

1. **每个测试文件只包含一个主要测试函数**
   - Each test file contains only one main test function
   - 例如: `test_login_injection.py` 只包含 `test_login_sql_injection()`
   - Example: `test_login_injection.py` only contains `test_login_sql_injection()`

2. **函数职责单一**
   - Single responsibility for each function
   - 每个函数只测试一个端点的SQL注入
   - Each function only tests SQL injection for one endpoint

3. **易于维护和扩展**
   - Easy to maintain and extend
   - 添加新测试只需创建新文件
   - Adding new tests only requires creating new files

---

### 测试覆盖范围 (Test Coverage)

#### 测试的端点 (Tested Endpoints)
1. `/auth/login` - 登录端点
2. `/performQuery` - 查询端点
3. `/data/update` - 更新端点
4. `/data/insert` - 插入端点
5. `/data/delete` - 删除端点

#### 测试的注入类型 (Tested Injection Types)
1. **OR注入** - `' OR '1'='1`
2. **注释注入** - `' --` 或 `' /*`
3. **联合查询注入** - `' UNION SELECT ...`
4. **布尔注入** - `' OR 1=1 --`
5. **时间盲注** - `' OR SLEEP(5) --`
6. **堆叠查询** - `'; DROP TABLE ...`
7. **表名注入** - 恶意表名
8. **列名注入** - 恶意列名
9. **操作符注入** - 恶意操作符

---

### 使用方法 (Usage)

#### 基本用法 (Basic Usage)
```bash
# 运行所有测试
# Run all tests
python backend/attack/run_sql_security_tests.py

# 指定API URL
# Specify API URL
python backend/attack/run_sql_security_tests.py --url http://localhost:8000

# 指定测试用户凭据
# Specify test user credentials
python backend/attack/run_sql_security_tests.py --email test@test.com --password test123

# 保存结果到文件
# Save results to file
python backend/attack/run_sql_security_tests.py --output results.json --report report.txt
```

#### 单独运行测试 (Run Individual Tests)
```python
from attack.test_login_injection import test_login_sql_injection

results = test_login_sql_injection("http://127.0.0.1:8000")
for result in results:
    print(f"{result['test_name']}: {result['status']}")
```

---

### 测试结果说明 (Test Results Explanation)

#### 状态码 (Status Codes)
- **VULNERABLE** - 检测到漏洞，注入成功
- **PROTECTED** - 受到保护，注入被阻止
- **UNKNOWN** - 状态未知
- **ERROR** - 测试出错
- **TIMEOUT** - 请求超时
- **SKIPPED** - 测试被跳过

#### 漏洞指标 (Vulnerability Indicators)
- `Authentication bypassed` - 认证被绕过
- `SQL error detected` - SQL错误被检测到
- `Time-based injection detected` - 检测到基于时间的注入
- `Unexpected large result set` - 意外的大的结果集

---

### 相关文件 (Related Files)

- `backend/security.py` - 安全验证函数
- `backend/security_monitor.py` - 安全监控模块
- `backend/api_handler.py` - API请求处理
- `backend/db_query.py` - 数据库查询函数
- `backend/CHANGELOG.md` - 主变更日志

---

### 注意事项 (Notes)

1. **测试环境**
   - 确保在测试环境中运行，不要在生产环境运行
   - Ensure running in test environment, not production

2. **测试数据**
   - 测试可能会创建测试数据，运行后需要清理
   - Tests may create test data, need cleanup after running

3. **认证令牌**
   - 某些测试需要有效的认证令牌
   - Some tests require valid authentication tokens
   - 确保测试用户有适当的权限
   - Ensure test users have appropriate permissions

4. **日志文件**
   - 测试会检查日志文件，确保日志目录存在
   - Tests check log files, ensure log directory exists

---

### 未来改进 (Future Improvements)

1. 添加更多注入载荷类型
2. 添加自动化漏洞扫描
3. 集成到CI/CD流程
4. 添加性能测试
5. 添加渗透测试报告生成

---

**最后更新:** 2024  
**Last Updated:** 2024

