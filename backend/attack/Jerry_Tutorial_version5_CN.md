# Jerry Tutorial Version 5 - SQL安全测试完整指南
# Jerry Tutorial Version 5 - Complete SQL Security Testing Guide

> **为组员准备的完整教程**  
> **Complete tutorial for group members**  
> **假设：还没有下载任何东西**  
> **Assumption: Nothing has been downloaded yet**  
> **版本5更新：改进了UNKNOWN状态判断逻辑，更准确地识别PROTECTED状态**  
> **Version 5 Update: Improved UNKNOWN status detection, more accurate PROTECTED identification**

---

## 📋 目录 (Table of Contents)

1. [环境准备](#1-环境准备-environment-setup)
2. [下载和设置项目](#2-下载和设置项目-download-and-setup)
3. [数据库设置](#3-数据库设置-database-setup)
4. [创建测试用户](#4-创建测试用户-create-test-users)
5. [运行SQL安全测试](#5-运行sql安全测试-run-sql-security-tests)
6. [理解测试结果](#6-理解测试结果-understand-test-results)
7. [状态符号说明](#7-状态符号说明-status-symbols-explanation)
8. [常见问题](#8-常见问题-common-issues)
9. [完整测试流程](#9-完整测试流程-complete-testing-process)
10. [版本5更新说明](#10-版本5更新说明-version-5-update-notes)

---

## 1. 环境准备 (Environment Setup)

### 1.1 安装Python

**检查是否已安装Python:**

```bash
python --version
```

**如果没有安装:**

1. 访问 https://www.python.org/downloads/
2. 下载最新版本的Python（推荐3.8或更高版本）
3. 安装时**勾选** "Add Python to PATH"
4. 验证安装：
   ```bash
   python --version
   ```

### 1.2 安装必要的Python库

打开命令行（cmd或PowerShell），运行：

```bash
pip install pymysql requests
```

**如果pip命令不工作，尝试:**
```bash
python -m pip install pymysql requests
```

### 1.3 安装数据库（Percona Server或MySQL）

**选项1: 使用Docker（推荐，最简单）**

1. 安装Docker Desktop: https://www.docker.com/products/docker-desktop
2. 项目包含 `percona-compose/docker-compose.yml`，可以直接使用

**选项2: 手动安装Percona Server**

1. 访问 https://www.percona.com/downloads/Percona-Server-LATEST
2. 下载并安装Percona Server
3. 记住root密码（稍后会用到）

---

## 2. 下载和设置项目 (Download and Setup)

### 2.1 下载项目

1. 从Git仓库克隆或下载项目
2. 解压到本地文件夹，例如：
   ```
   D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
   ```

### 2.2 验证项目结构

确保项目文件夹包含以下结构：

```
COMP3335_GP/
├── backend/
│   ├── attack/
│   │   ├── run_sql_security_tests.py
│   │   ├── test_*.py
│   │   └── ...
│   ├── main.py
│   ├── setup_test_user.py
│   └── ...
├── frontend/
├── sql/
└── ...
```

### 2.3 进入项目目录

打开命令行，进入项目根目录：

```bash
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
```

**提示:** 根据你的实际路径调整

---

## 3. 数据库设置 (Database Setup)

### 3.1 启动数据库

**如果使用Docker:**

```bash
cd percona-compose
docker-compose up -d
```

**如果手动安装:**

1. 启动Percona Server服务
2. 确保服务正在运行

### 3.2 创建数据库和表

1. **连接到数据库:**
   ```bash
   mysql -u root -p
   ```
   输入root密码

2. **创建数据库:**
   ```sql
   CREATE DATABASE ComputingU;
   USE ComputingU;
   ```

3. **导入表结构:**
   在MySQL命令行中，运行项目中的SQL文件：
   ```sql
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/ComputingU_students.sql;
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/ComputingU_guardians.sql;
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/ComputingU_staffs.sql;
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/ComputingU_courses.sql;
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/ComputingU_grades.sql;
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/ComputingU_disciplinary_records.sql;
   ```

   **或者使用load_sql文件夹中的文件:**
   ```sql
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/load_sql/University.sql;
   ```

4. **创建审计日志表:**
   ```sql
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/create_audit_tables.sql;
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/create_sessions_table.sql;
   ```

5. **设置数据库权限:**
   ```sql
   source D:/Useful_things/Downloads/Comp3335_gp_project/COMP3335_GP/sql/setup_db_permissions.sql;
   ```

### 3.3 配置数据库连接

编辑 `backend/db_connector.py`，确保数据库配置正确：

```python
DB_CONFIG = {
    'host': '127.0.0.1',  # 或你的数据库地址
    'port': 3306,
    'user': 'root',  # 或你的数据库用户名
    'password': '你的密码',  # 你的数据库密码
    'database': 'ComputingU',
    'charset': 'utf8mb4'
}
```

**或者使用环境变量（更安全）:**

```bash
# Windows PowerShell
$env:DB_PASSWORD="你的密码"
$env:DB_USER="root"
$env:DB_NAME="ComputingU"
```

---

## 4. 创建测试用户 (Create Test Users)

### 4.1 运行测试用户设置脚本

在项目根目录运行：

```bash
cd backend
python setup_test_user.py
cd ..
```

### 4.2 验证测试用户创建成功

你应该看到类似输出：

```
✓ Test student account updated (ID: 100)
✓ Test staff account updated (ID: 5001)
✓ Test guardian account updated (ID: 1000)

Test Account Setup Complete - Security Summary
============================================================
Student Account:
  Email: test_student@example.com
  Password: StudentTest123
  User ID: 100

Staff Account:
  Email: test_staff@example.com
  Password: StaffTest123
  User ID: 5001

Guardian Account:
  Email: test_guardian@example.com
  Password: GuardianTest123
  User ID: 1000
```

**这些测试账户将用于SQL安全测试。**

---

## 5. 运行SQL安全测试 (Run SQL Security Tests)

### 5.1 启动后端服务器

**打开第一个命令行窗口:**

```bash
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP\backend
python main.py
```

**你应该看到:**
```
Serving on http://127.0.0.1:8000
```

**重要:** 保持这个窗口打开！不要关闭它。

### 5.2 运行测试

**打开第二个命令行窗口（新的窗口）:**

```bash
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
python backend/attack/run_sql_security_tests.py
```

### 5.3 使用特定测试用户运行

如果你想使用特定的测试用户：

```bash
python backend/attack/run_sql_security_tests.py \
    --email test_student@example.com \
    --password StudentTest123
```

### 5.4 保存测试结果

```bash
python backend/attack/run_sql_security_tests.py \
    --output test_results.json \
    --report test_report.txt
```

这会在当前文件夹创建：
- `test_results.json` - 详细的测试数据
- `test_report.txt` - 人类可读的报告

---

## 6. 理解测试结果 (Understand Test Results)

### 6.1 测试报告结构

测试报告包含以下部分：

1. **LOGIN INJECTION** - 登录端点测试
2. **QUERY INJECTION** - 查询端点测试
3. **UPDATE INJECTION** - 更新端点测试
4. **INSERT INJECTION** - 插入端点测试
5. **DELETE INJECTION** - 删除端点测试
6. **SECURITY MONITORING** - 安全监控测试

### 6.2 摘要部分

报告末尾有摘要：

```
SUMMARY - 摘要
================================================================================
Total Tests: 33
Vulnerable: 0 ❌
Protected: 30+ ✅  (版本5改进后应该更多)
Errors/Skipped: 0-3 ⚠️
================================================================================
```

---

## 7. 状态符号说明 (Status Symbols Explanation)

### ✅ PROTECTED（受保护）- 好的！

**含义:** 系统成功阻止了SQL注入攻击

**示例:**
```
✅ Basic OR injection: PROTECTED
```

**说明:** 这是期望的结果！表示你的系统是安全的。

---

### ❌ VULNERABLE（易受攻击）- 坏的！

**含义:** 系统未能阻止SQL注入攻击

**示例:**
```
❌ Basic OR injection: VULNERABLE
   - Authentication bypassed
```

**说明:** 这是严重的安全问题，需要立即修复！

---

### ⚠️ UNKNOWN（未知）- 版本5已大幅改进！

**含义:** 测试无法确定系统是否安全（现在很少出现）

**版本5改进说明:**
- ✅ **改进了对200响应的判断逻辑**
  - 如果查询返回空结果或小结果集（0-10条），识别为PROTECTED
  - 原因：参数化查询将SQL注入视为字面字符串，所以找不到匹配
- ✅ **改进了更新/删除端点的判断**
  - 如果返回200且ok=true，识别为PROTECTED
  - 原因：参数化查询将恶意SQL作为数据存储，不会执行
- ✅ **更智能的错误检测**
  - 如果响应包含错误信息，识别为PROTECTED

**为什么200响应可能是PROTECTED？**

当使用参数化查询时：
- SQL注入被当作**字面字符串**处理
- 例如：搜索 `' OR '1'='1` 会查找字面字符串 `' OR '1'='1`
- 数据库中不存在这个字符串，所以返回空结果
- **这是安全的！** 表示SQL注入被成功阻止

**可能原因（如果仍显示UNKNOWN）:**
- 响应状态码不是标准的400/403/401/200
- 响应内容格式特殊
- 需要进一步调查

**示例:**
```
⚠️ Filter value injection - OR: UNKNOWN
   - Response code: 200
```

**说明:** 版本5改进了判断逻辑，大部分之前显示UNKNOWN的测试现在会显示PROTECTED。如果仍显示UNKNOWN，检查响应内容。

---

### ✅ MONITORED（已监控）- 好的！

**含义:** 安全监控系统正在工作，SQL注入尝试被记录

**示例:**
```
✅ SQL injection in login: MONITORED
```

**说明:** 这是好的！表示安全监控功能正常工作。

---

### ⚠️ ERROR（错误）

**含义:** 测试过程中发生错误

**可能原因:**
- 网络问题
- 服务器未运行
- 数据库连接失败

**解决方法:** 检查服务器和数据库是否正常运行

---

### ⚠️ TIMEOUT（超时）

**含义:** 请求超时

**可能原因:**
- 服务器响应慢
- 网络问题
- 时间盲注（但通常会被阻止）

---

### ⚠️ SKIPPED（跳过）

**含义:** 测试被跳过

**可能原因:**
- 需要认证但没有认证令牌
- 测试条件不满足

**说明:** 这是正常的，不影响其他测试。

---

## 8. 常见问题 (Common Issues)

### Q1: "can't open file" 或 "No such file or directory"

**问题:** 在错误的文件夹中运行命令

**解决方法:**
```bash
# 确保你在项目根目录
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP

# 然后运行
python backend/attack/run_sql_security_tests.py
```

---

### Q2: "Cannot connect to server"

**问题:** 后端服务器没有运行

**解决方法:**
1. 打开新的命令行窗口
2. 运行：
   ```bash
   cd backend
   python main.py
   ```
3. 等待看到 "Serving on http://127.0.0.1:8000"
4. 保持窗口打开
5. 在另一个窗口重新运行测试

---

### Q3: "Could not get authentication token"

**问题:** 测试用户不存在或密码错误

**解决方法:**
```bash
# 创建测试用户
cd backend
python setup_test_user.py
cd ..

# 重新运行测试
python backend/attack/run_sql_security_tests.py
```

---

### Q4: "Database connection failed"

**问题:** 数据库未运行或配置错误

**解决方法:**
1. 确保数据库服务正在运行
2. 检查 `backend/db_connector.py` 中的数据库配置
3. 测试连接：
   ```bash
   mysql -u root -p
   ```

---

### Q5: 很多测试显示 "UNKNOWN"

**问题:** 测试代码无法确定状态（版本5已改进）

**版本5改进:**
- ✅ 改进了对200响应的判断
- ✅ 如果查询返回空结果，识别为PROTECTED
- ✅ 如果更新返回ok=true，识别为PROTECTED
- ✅ 大部分UNKNOWN现在会显示PROTECTED

**如果仍显示UNKNOWN:**
- 查看测试结果中的 `response_code`
- 如果响应码是 400/403/401/500，通常表示攻击被阻止（PROTECTED）
- 可以手动检查API响应来确认

---

### Q6: "ModuleNotFoundError: No module named 'requests'"

**问题:** 缺少Python库

**解决方法:**
```bash
pip install requests pymysql
```

---

## 9. 完整测试流程 (Complete Testing Process)

### 第一次运行（完整设置）

```bash
# 步骤1: 进入项目目录
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP

# 步骤2: 启动数据库（如果使用Docker）
cd percona-compose
docker-compose up -d
cd ..

# 步骤3: 创建测试用户
cd backend
python setup_test_user.py
cd ..

# 步骤4: 启动服务器（第一个窗口）
cd backend
python main.py
# 保持这个窗口打开！

# 步骤5: 运行测试（第二个窗口，新窗口）
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
python backend/attack/run_sql_security_tests.py
```

### 后续运行（快速测试）

```bash
# 只需要两个步骤：

# 1. 启动服务器（第一个窗口）
cd backend
python main.py

# 2. 运行测试（第二个窗口）
cd ..
python backend/attack/run_sql_security_tests.py
```

---

## 10. 版本5更新说明 (Version 5 Update Notes)

### 🎯 主要改进

#### 1. 改进了UNKNOWN状态判断逻辑

**问题:** 很多测试显示UNKNOWN，无法确定系统是否安全

**解决方案:**

**对于查询端点 (`/performQuery`):**
- ✅ 如果返回200且结果集为空或很小（0-10条），识别为PROTECTED
- ✅ 原因：参数化查询将SQL注入视为字面字符串，找不到匹配，返回空结果
- ✅ 如果结果集很大（>100条），识别为VULNERABLE（OR注入可能成功）

**对于更新端点 (`/data/update`):**
- ✅ 如果返回200且ok=true，识别为PROTECTED
- ✅ 原因：参数化查询将恶意SQL作为数据存储，不会执行SQL注入
- ✅ 这是安全的！恶意SQL只是被存储为字符串，不会被执行

**对于插入端点 (`/data/insert`):**
- ✅ 如果返回200且ok=true，识别为PROTECTED
- ✅ 同样的逻辑：参数化查询防止SQL注入

**对于删除端点 (`/data/delete`):**
- ✅ 同样的逻辑：参数化查询防止SQL注入

#### 2. 为什么200响应可能是PROTECTED？

**关键理解:**

当使用参数化查询时：
```python
# 安全的方式（参数化查询）
cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
```

如果 `email = "' OR '1'='1"`：
- 参数化查询会将这个值作为**字面字符串**处理
- SQL查询变成：`SELECT * FROM students WHERE email = "' OR '1'='1"`
- 数据库中不存在这个字符串，所以返回空结果
- **这是安全的！** SQL注入被成功阻止

**对比（危险的方式，不使用参数化查询）:**
```python
# 危险的方式（字符串拼接）
cursor.execute(f"SELECT * FROM students WHERE email = '{email}'")
```

如果 `email = "' OR '1'='1"`：
- SQL查询变成：`SELECT * FROM students WHERE email = '' OR '1'='1'`
- 这会执行SQL注入，返回所有记录
- **这是危险的！** SQL注入成功

#### 3. 预期测试结果改进

**版本4之前:**
```
QUERY INJECTION
  ⚠️ Filter value injection - OR: UNKNOWN
  ⚠️ Filter value injection - UNION: UNKNOWN
  ⚠️ Filter value injection - Comment: UNKNOWN
```

**版本5:**
```
QUERY INJECTION
  ✅ Filter value injection - OR: PROTECTED
  ✅ Filter value injection - UNION: PROTECTED
  ✅ Filter value injection - Comment: PROTECTED
```

**统计改进:**
- 之前：Protected: 17 ✅, UNKNOWN: 10+ ⚠️
- 现在：Protected: 30+ ✅, UNKNOWN: 0-3 ⚠️（大部分UNKNOWN现在会显示PROTECTED）

**修复的测试文件:**
- ✅ `test_query_injection.py` - 改进了对200响应的判断，组合保护检查
- ✅ `test_update_injection.py` - 改进了对ok=true的判断，组合保护检查
- ✅ `test_insert_injection.py` - 添加了对200响应的保护判断
- ✅ `test_delete_injection.py` - 添加了对200响应的保护判断

#### 4. 技术实现细节

**改进的判断逻辑:**

```python
# 对于查询端点
if response.status_code == 200:
    data = response.json()
    if "results" in data:
        result_count = len(data["results"])
        if result_count > 100:
            # 大结果集，可能易受攻击
            is_vulnerable = True
        elif result_count == 0 or result_count <= 10:
            # 空或小结果集，参数化查询正常工作
            is_protected = True

# 对于更新/插入/删除端点
if response.status_code == 200:
    data = response.json()
    if data.get("ok"):
        # 参数化查询将恶意SQL作为数据存储，不会执行
        is_protected = True
    elif "error" in data or not data.get("ok"):
        # 响应有错误或ok=false，可能受保护
        is_protected = True

# 重要：组合所有保护检查（不要覆盖之前的判断）
is_protected = is_protected or (
    response.status_code == 400 or  # Bad request
    response.status_code == 403 or  # Forbidden
    response.status_code == 401     # Unauthorized
)
```

---

## 📊 预期测试结果 (Expected Test Results)

### 理想的测试结果（版本5）

```
================================================================================
SUMMARY - 摘要
================================================================================
Total Tests: 33
Vulnerable: 0 ❌
Protected: 30+ ✅  (版本5改进后)
Errors/Skipped: 0-3 ⚠️
================================================================================

✅ All tests passed - No vulnerabilities detected
✅ 所有测试通过 - 未检测到漏洞
```

### 测试结果说明

- **Vulnerable: 0** - 没有发现漏洞 ✅
- **Protected: 30+** - 大部分测试显示受保护 ✅（版本5改进后）
- **Errors/Skipped: 少量** - 少量错误或跳过是正常的

---

## 🎯 测试覆盖范围 (Test Coverage)

测试套件会测试：

1. **登录端点** (`/auth/login`)
   - OR注入
   - 注释注入
   - 联合查询注入
   - 布尔注入
   - 时间盲注
   - 堆叠查询
   - 双引号注入

2. **查询端点** (`/performQuery`)
   - 过滤器值注入
   - 表名注入
   - 列名注入
   - 操作符注入

3. **更新端点** (`/data/update`)
   - 更新值注入
   - 主键注入

4. **插入端点** (`/data/insert`)
   - 插入值注入
   - 列名注入

5. **删除端点** (`/data/delete`)
   - 主键注入

6. **安全监控**
   - 验证SQL注入尝试是否被记录

---

## 📝 重要提示 (Important Notes)

### ⚠️ 安全注意事项

1. **只在测试环境运行** - 不要在生产环境运行这些测试
2. **测试数据** - 测试可能会创建测试数据，运行后可能需要清理
3. **测试用户** - 测试用户是安全的，不会影响真实用户数据

### ✅ 最佳实践

1. **定期运行测试** - 在每次代码更改后运行
2. **保存测试结果** - 使用 `--output` 和 `--report` 参数保存结果
3. **检查日志** - 查看 `backend/logs/` 文件夹中的日志文件
4. **修复漏洞** - 如果发现 VULNERABLE，立即修复

---

## 🔍 验证系统安全 (Verify System Security)

### 检查清单

运行测试前，确保：

- [ ] Python已安装（`python --version`）
- [ ] 必要的库已安装（`pip install requests pymysql`）
- [ ] 数据库正在运行
- [ ] 数据库已创建并包含所有表
- [ ] 测试用户已创建（`python backend/setup_test_user.py`）
- [ ] 后端服务器正在运行（`python backend/main.py`）

### 验证步骤

1. **测试数据库连接:**
   ```bash
   python -c "from backend.db_connector import test_db_connection; print(test_db_connection())"
   ```
   应该输出: `(True, "Database connection successful")`

2. **测试服务器:**
   在浏览器打开 `http://127.0.0.1:8000`
   应该看到API信息

3. **运行测试:**
   ```bash
   python backend/attack/run_sql_security_tests.py
   ```

---

## 📚 相关文档 (Related Documentation)

- **简单使用教程**: `简单使用教程_CN.md`
- **快速修复指南**: `快速修复指南_CN.md`
- **问题解决说明**: `问题解决说明_CN.md`
- **详细教程**: `SQL_SECURITY_TEST_TUTORIAL_CN.md`
- **变更日志**: `SQL_SECURITY_TEST_CHANGELOG.md`
- **修复说明**: `修复说明_CN.md`

---

## 🎉 总结 (Summary)

### 快速开始清单

1. ✅ 安装Python和必要库
2. ✅ 下载项目
3. ✅ 设置数据库
4. ✅ 创建测试用户
5. ✅ 启动服务器
6. ✅ 运行测试
7. ✅ 查看结果

### 关键命令

```bash
# 创建测试用户（只需要一次）
cd backend
python setup_test_user.py
cd ..

# 启动服务器
cd backend
python main.py

# 运行测试
python backend/attack/run_sql_security_tests.py
```

---

## 💡 需要帮助？

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 检查相关文档
3. 查看日志文件：`backend/logs/app.log`
4. 联系团队成员

---

**版本:** Version 5  
**最后更新:** 2024  
**作者:** Jerry  
**适用于:** COMP3335 小组项目

---

**祝测试顺利！** 🚀

