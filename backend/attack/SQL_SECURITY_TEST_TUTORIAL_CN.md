# SQL安全测试使用教程
# SQL Security Testing Tutorial (Chinese)

## 目录 (Table of Contents)

1. [简介](#简介)
2. [环境准备](#环境准备)
3. [测试套件结构](#测试套件结构)
4. [运行测试](#运行测试)
5. [理解测试结果](#理解测试结果)
6. [测试数据库和验证安全保护](#测试数据库和验证安全保护)
7. [常见问题](#常见问题)
8. [最佳实践](#最佳实践)

---

## 简介

本教程将指导您如何使用SQL安全测试套件来测试您的数据库应用程序，验证SQL注入防护措施是否有效。

### 测试套件功能

- ✅ 测试所有API端点的SQL注入漏洞
- ✅ 验证参数化查询是否正确实现
- ✅ 检查表名和列名的白名单验证
- ✅ 验证安全监控和日志记录
- ✅ 生成详细的测试报告

---

## 环境准备

### 1. 确保后端服务器正在运行

```bash
# 进入后端目录
cd backend

# 启动服务器
python main.py
```

服务器应该运行在 `http://127.0.0.1:8000`（默认端口）

### 2. 确保数据库已配置并运行

确保Percona Server（或MySQL）正在运行，并且：
- 数据库 `ComputingU` 已创建
- 所有表已创建（students, guardians, staffs, courses, grades, disciplinary_records）
- 测试用户已创建

### 3. 安装Python依赖

```bash
# 确保已安装requests库
pip install requests
```

---

## 测试套件结构

测试套件遵循"一个文件一个函数"原则，结构如下：

```
backend/attack/
├── auth/
│   ├── auth_bruteforce_attack.py      # 暴力破解攻击测试
│   ├── auth_session_attack.py         # 会话攻击测试
│   ├── auth_sql_injection_attack.py   # 登录端点SQL注入测试
│   └── README.md                      # Auth模块文档
├── sql/
│   ├── test_query_injection.py        # 查询端点测试
│   ├── test_update_injection.py       # 更新端点测试
│   ├── test_insert_injection.py       # 插入端点测试
│   ├── test_delete_injection.py       # 删除端点测试
│   └── test_security_monitoring.py     # 安全监控测试
├── run_sql_security_tests.py          # 主测试运行程序
├── SQL_SECURITY_TEST_CHANGELOG.md     # 变更日志
├── SQL_SECURITY_TEST_TUTORIAL_CN.md   # 本教程
└── Jerry_Tutorial_version5_CN.md     # 完整教程
```

### 每个测试文件的功能

1. **auth/auth_sql_injection_attack.py**
   - 测试登录端点的SQL注入
   - 包括：OR注入、注释注入、联合查询注入、时间盲注等

2. **auth/auth_bruteforce_attack.py**
   - 测试暴力破解攻击防护
   - 测试常见弱密码列表

3. **auth/auth_session_attack.py**
   - 测试会话管理安全性
   - 包括：会话固定、会话重放、过期会话攻击

4. **sql/test_query_injection.py**
   - 测试查询端点的SQL注入
   - 包括：过滤器注入、表名注入、列名注入等

5. **sql/test_update_injection.py**
   - 测试更新端点的SQL注入
   - 包括：更新值注入、主键注入等

6. **sql/test_insert_injection.py**
   - 测试插入端点的SQL注入
   - 包括：插入值注入、列名注入等

7. **sql/test_delete_injection.py**
   - 测试删除端点的SQL注入
   - 包括：主键注入、表名注入等

8. **sql/test_security_monitoring.py**
   - 测试安全监控是否正常工作
   - 检查日志文件是否记录安全事件

---

## 运行测试

### 方法1: 运行完整测试套件（推荐）

```bash
# 基本用法
python backend/attack/run_sql_security_tests.py

# 指定API URL
python backend/attack/run_sql_security_tests.py --url http://localhost:8000

# 指定测试用户凭据
python backend/attack/run_sql_security_tests.py \
    --email test@test.com \
    --password test123

# 保存结果到文件
python backend/attack/run_sql_security_tests.py \
    --output results.json \
    --report report.txt
```

### 方法2: 单独运行特定测试

```python
# 示例：只测试登录端点SQL注入
from attack.auth.auth_sql_injection_attack import test_sql_injection_payloads
test_sql_injection_payloads()

# 示例：测试查询端点
from attack.sql.test_query_injection import test_query_sql_injection
results = test_query_sql_injection("http://127.0.0.1:8000", auth_token)
for result in results:
    print(f"{result['test_name']}: {result['status']}")
```

### 方法3: 在Python脚本中使用

```python
import sys
sys.path.insert(0, 'backend')

from attack.run_sql_security_tests import run_all_tests, generate_report

# 运行所有测试
results = run_all_tests(
    base_url="http://127.0.0.1:8000",
    test_email="test@test.com",
    test_password="test123"
)

# 生成报告
report = generate_report(results)
print(report)
```

---

## 理解测试结果

### 测试状态说明

#### ✅ PROTECTED（受保护）
- 表示系统成功阻止了SQL注入攻击
- 这是期望的结果
- 示例：
  ```
  ✅ Basic OR injection: PROTECTED
  ```

#### ❌ VULNERABLE（易受攻击）
- 表示系统未能阻止SQL注入攻击
- 这是严重的安全问题，需要立即修复
- 示例：
  ```
  ❌ Basic OR injection: VULNERABLE
     - Authentication bypassed
  ```

#### ⚠️ ERROR（错误）
- 测试过程中发生错误
- 可能是网络问题或服务器问题
- 需要检查服务器状态

#### ⚠️ TIMEOUT（超时）
- 请求超时
- 可能是时间盲注的迹象
- 需要进一步调查

#### ⚠️ SKIPPED（跳过）
- 测试被跳过
- 通常是因为缺少认证令牌

### 测试报告示例

```
================================================================================
SQL Security Test Report - SQL安全测试报告
================================================================================
Test Time: 2024-01-01T12:00:00
Target: http://127.0.0.1:8000
================================================================================

LOGIN INJECTION
--------------------------------------------------------------------------------
  ✅ Basic OR injection: PROTECTED
  ✅ Comment injection: PROTECTED
  ✅ Union injection: PROTECTED
  ✅ Boolean injection: PROTECTED
  ✅ Time-based injection: PROTECTED
  ✅ Stacked queries: PROTECTED
  ✅ Double quote injection: PROTECTED

QUERY INJECTION
--------------------------------------------------------------------------------
  ✅ Filter value injection - OR: PROTECTED
  ✅ Filter value injection - UNION: PROTECTED
  ✅ Table name injection: PROTECTED
  ✅ Column name injection: PROTECTED

================================================================================
SUMMARY - 摘要
================================================================================
Total Tests: 20
Vulnerable: 0 ❌
Protected: 20 ✅
Errors/Skipped: 0 ⚠️
================================================================================

✅ All tests passed - No vulnerabilities detected
✅ 所有测试通过 - 未检测到漏洞
```

---

## 测试数据库和验证安全保护

### 步骤1: 验证数据库连接

首先，确保数据库连接正常：

```bash
# 测试数据库连接
python -c "from backend.db_connector import test_db_connection; print(test_db_connection())"
```

应该输出：`(True, "Database connection successful")`

### 步骤2: 验证表结构

确保所有必需的表都存在：

```python
from backend.db_query import db_query

tables = db_query("SHOW TABLES")
print("Existing tables:")
for table in tables:
    print(f"  - {list(table.values())[0]}")
```

应该看到：
- students
- guardians
- staffs
- courses
- grades
- disciplinary_records

### 步骤3: 验证安全保护措施

#### 3.1 验证参数化查询

检查代码中是否使用参数化查询：

```python
# ✅ 正确：使用参数化查询
cur.execute("SELECT * FROM students WHERE email = %s", (email,))

# ❌ 错误：字符串拼接（易受SQL注入攻击）
cur.execute(f"SELECT * FROM students WHERE email = '{email}'")
```

#### 3.2 验证表名白名单

检查 `api_handler.py` 中的表名验证：

```python
# 应该看到类似代码
allowed_tables = ROLE_TABLES.get(auth["role"], [])
if not validate_table_name_whitelist(table, allowed_tables):
    return json_response(self, 400, {"error": "Invalid table name"})
```

#### 3.3 验证列名验证

检查列名是否被验证：

```python
# 应该看到类似代码
if not validate_column_name(col):
    return json_response(self, 400, {"error": f"Invalid column name: {col}"})
```

### 步骤4: 运行安全测试

```bash
# 运行完整测试套件
python backend/attack/run_sql_security_tests.py --output test_results.json
```

### 步骤5: 检查安全日志

测试后，检查日志文件是否记录了安全事件：

```bash
# 查看应用日志
tail -n 50 backend/logs/app.log

# 查看数据库日志
tail -n 50 backend/logs/database.log

# 查看安全日志（如果存在）
tail -n 50 backend/logs/security.log
```

应该看到类似的安全事件记录：
```
2024-01-01 12:00:00 - security - WARNING - SECURITY_EVENT: {'event_type': 'sql_injection_attempt', ...}
```

### 步骤6: 验证角色权限

测试不同角色的访问控制：

```python
# 测试学生角色
# 学生应该只能访问自己的数据
student_token = get_auth_token("student@test.com", "password")

# 测试ARO角色
# ARO应该只能访问grades表
aro_token = get_auth_token("aro@test.com", "password")

# 测试DRO角色
# DRO应该只能访问disciplinary_records表
dro_token = get_auth_token("dro@test.com", "password")
```

### 步骤7: 验证数据加密

检查敏感数据是否已加密：

```python
from backend.db_query import db_query

# 检查identification_number是否加密
result = db_query("SELECT identification_number FROM students LIMIT 1")
if result:
    id_number = result[0]['identification_number']
    # 加密的数据通常以特定格式存储
    # 检查是否符合加密格式
    print(f"ID Number format: {id_number[:20]}...")
```

---

## 常见问题

### Q1: 测试显示"Authentication Required"错误

**A:** 某些测试需要有效的认证令牌。解决方法：
1. 确保测试用户已创建
2. 使用 `--email` 和 `--password` 参数提供凭据
3. 检查用户是否有适当的权限

### Q2: 所有测试都显示"ERROR"状态

**A:** 可能的原因：
1. 后端服务器未运行
2. 数据库连接失败
3. API端点URL不正确

解决方法：
```bash
# 检查服务器是否运行
curl http://127.0.0.1:8000/

# 检查数据库连接
python -c "from backend.db_connector import test_db_connection; print(test_db_connection())"
```

### Q3: 测试显示"VULNERABLE"但系统应该安全

**A:** 可能的原因：
1. 测试误报（检查响应内容）
2. 安全措施未正确实现
3. 测试载荷过于复杂

解决方法：
1. 检查测试结果的详细指标
2. 手动验证漏洞是否真实存在
3. 检查代码中的安全措施实现

### Q4: 如何测试特定端点？

**A:** 可以单独导入和运行特定测试：

```python
from attack.test_login_injection import test_login_sql_injection

results = test_login_sql_injection("http://127.0.0.1:8000")
```

### Q5: 测试后如何清理测试数据？

**A:** 测试可能会创建测试数据。清理方法：

```python
from backend.db_query import db_execute

# 删除测试数据（根据实际情况调整）
db_execute("DELETE FROM students WHERE StuID >= 9990")
```

---

## 最佳实践

### 1. 定期运行测试

- 在每次代码更改后运行测试
- 在部署到生产环境前运行测试
- 设置自动化测试（CI/CD）

### 2. 测试不同角色

- 测试所有用户角色（student, guardian, aro, dro, root）
- 验证每个角色的权限是否正确实施

### 3. 检查日志

- 定期检查安全日志
- 监控SQL注入尝试
- 分析攻击模式

### 4. 保持测试更新

- 添加新的注入载荷
- 更新测试以匹配新的API端点
- 关注新的SQL注入技术

### 5. 文档化测试结果

- 保存测试报告
- 记录修复的漏洞
- 跟踪安全改进

---

## 总结

本SQL安全测试套件提供了全面的测试工具来验证您的数据库应用程序的安全性。通过定期运行这些测试，您可以：

1. ✅ 及时发现SQL注入漏洞
2. ✅ 验证安全措施的有效性
3. ✅ 确保符合项目安全要求
4. ✅ 提高整体系统安全性

### 下一步

1. 运行完整测试套件
2. 检查测试结果
3. 修复发现的漏洞
4. 验证安全日志记录
5. 设置自动化测试

---

**需要帮助？**

- 查看变更日志：`SQL_SECURITY_TEST_CHANGELOG.md`
- 检查代码注释
- 参考项目文档

**最后更新:** 2024

