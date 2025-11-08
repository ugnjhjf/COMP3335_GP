# 项目完成度检查清单 / Project Completion Checklist

**项目:** COMP3335_GP  
**日期:** 2024  
**目的:** 确保项目按要求完成，便于团队协作

---

## 📋 项目要求对照 / Requirements Checklist

### Section 3: Objectives / 目标

#### ✅ 1. 数据库设计 (Design a database for a university, ComputingU)

**状态:** ✅ **已完成**

- [x] 6个表已设计
  - [x] `students` - 学生表
  - [x] `guardians` - 监护人表
  - [x] `staffs` - 员工表
  - [x] `courses` - 课程表
  - [x] `grades` - 成绩表
  - [x] `disciplinary_records` - 纪律记录表

**验证方法:**
```bash
# 检查SQL文件是否存在
ls sql/ComputingU_*.sql
```

---

#### ✅ 2. 数据安全 (Data in this database should be secured)

##### 2.a 敏感数据加密 (Sensitive data should be encrypted)

**状态:** ✅ **模块已创建，需要集成**

- [x] 加密模块已创建 (`backend/data_encryption.py`)
- [x] 识别敏感字段：
  - [x] `students.identification_number` - 身份证号
  - [x] `students.address` - 地址
  - [x] `staffs.identification_number` - 身份证号
  - [x] `staffs.address` - 地址
- [x] 使用MySQL AES_ENCRYPT/AES_DECRYPT函数
- [x] 密钥管理（不同角色使用不同密钥）
- [ ] ⚠️ **需要集成到数据库查询中**
- [ ] ⚠️ **需要数据迁移到加密格式**

**需要完成:**
1. 在 `db_query.py` 中集成加密/解密
2. 在 `api_handler.py` 中处理加密数据
3. 运行数据迁移脚本

**验证方法:**
```sql
-- 检查数据是否加密
SELECT identification_number FROM students LIMIT 1;
-- 应该看到加密后的二进制数据
```

---

##### 2.b 基于角色的访问控制 (Access control based on job roles)

**状态:** ✅ **已实现**

- [x] 角色权限控制 (`backend/privilege_controller.py`)
- [x] 最小权限原则实现
- [x] 4个角色已定义：
  - [x] `student` - 学生
  - [x] `guardian` - 监护人
  - [x] `aro` - 学术记录官
  - [x] `dro` - 纪律记录官
- [x] 表级权限控制
- [x] 列级权限控制
- [x] 数据范围过滤（自己/子女/全部）

**验证方法:**
- 测试不同角色访问不同表
- 测试学生只能访问自己的数据

---

#### ✅ 3. Web界面 (Simple web interface)

##### 3.a 登录功能 (enables users to log in)

**状态:** ✅ **已实现**

- [x] 登录端点 (`/auth/login`)
- [x] SQL注入防护
- [x] 密码安全存储（bcrypt）
- [x] 会话管理（token-based）

**验证方法:**
```bash
# 测试登录
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

##### 3.b 允许的操作 (enables users to perform allowed operations)

**状态:** ✅ **已实现**

- [x] 查询操作 (`/performQuery`)
- [x] 更新操作 (`/data/update`)
- [x] 删除操作 (`/data/delete`)
- [x] 插入操作 (`/data/insert`)
- [x] 外键显示名称（JOIN查询）
- [x] 防止未授权操作

**验证方法:**
- 测试不同角色的操作权限
- 测试外键是否正确显示名称

---

##### 3.c SQL注入防护 (SQL injections should be prevented)

**状态:** ✅ **已实现并增强**

- [x] 参数化查询
- [x] 输入验证
- [x] 表名/列名验证
- [x] 白名单验证 ⭐ 新增
- [x] 标识符转义 ⭐ 新增
- [x] SQL注入检测模块 (`backend/security_monitor.py`)
- [ ] ⚠️ **需要在API端点中集成SQL注入检测**

**需要完成:**
在 `api_handler.py` 中集成SQL注入检测：
```python
from security_monitor import validate_input_for_sql_injection

# 在接收用户输入后
is_safe, detected_patterns = validate_input_for_sql_injection(data, user_id, ip_address)
if not is_safe:
    return json_response(self, 400, {"error": "Invalid input detected"})
```

---

### Section 5: Requirements / 要求

#### ✅ 1. 使用Percona Server作为DBMS

**状态:** ✅ **已配置**

- [x] Docker Compose配置 (`percona-compose/docker-compose.yml`)
- [x] 数据库连接配置 (`backend/db_connector.py`)

**验证方法:**
```bash
# 启动数据库
cd percona-compose
docker-compose up -d

# 测试连接
python backend/main.py
```

---

#### ✅ 2. 表设计 (Design the tables)

**状态:** ✅ **已完成**

- [x] 所有表已创建
- [x] 示例用户已创建
- [x] DBMS账户配置（应用层用户）

**验证方法:**
```sql
-- 检查表是否存在
SHOW TABLES;

-- 检查示例用户
SELECT * FROM students LIMIT 5;
```

---

#### ✅ 3. 敏感数据保护 (Sensitive data should be protected)

**状态:** ⚠️ **模块已创建，需要集成**

- [x] 识别敏感字段
- [x] 加密模块已创建
- [x] 密钥管理（环境变量）
- [x] 不同角色使用不同密钥
- [ ] ⚠️ **需要集成到查询中**
- [ ] ⚠️ **需要数据迁移**

**需要完成:**
1. 集成加密/解密到 `db_query.py`
2. 数据迁移到加密格式
3. 测试加密/解密功能

---

#### ✅ 4. Web界面 (Simple web interface)

**状态:** ✅ **已实现**

- [x] 登录功能
- [x] SQL注入防护
- [x] 密码安全存储
- [x] 允许的操作
- [x] 外键显示名称
- [x] 防止未授权操作

**验证方法:**
- 打开 `frontend/index.html`
- 测试所有功能

---

#### ✅ 5. 访问监控 (Access to database should be monitored)

**状态:** ⚠️ **模块已创建，需要集成**

##### 5.a 记录不当访问、SQL注入尝试、策略违反

**状态:** ⚠️ **模块已创建，需要集成**

- [x] SQL注入检测模块 (`backend/security_monitor.py`)
- [x] 策略违反检测模块
- [x] 审计日志模块 (`backend/audit_logger.py`)
- [x] 审计表SQL脚本 (`sql/create_audit_tables.sql`)
- [ ] ⚠️ **需要在API端点中集成**
- [ ] ⚠️ **需要运行SQL脚本创建审计表**

**需要完成:**
1. 运行 `sql/create_audit_tables.sql` 创建审计表
2. 在 `api_handler.py` 中集成SQL注入检测
3. 在 `api_handler.py` 中集成审计日志

**验证方法:**
```sql
-- 检查审计表是否存在
SHOW TABLES LIKE '%audit%';
SHOW TABLES LIKE '%security%';

-- 检查是否有记录
SELECT * FROM security_events LIMIT 10;
```

---

##### 5.b 记录数据修改 (Any modifications to the data should be logged)

**状态:** ✅ **已实现**

- [x] 数据修改日志 (`backend/logger.py`)
- [x] `dataUpdateLog` 表
- [x] 所有UPDATE/DELETE/INSERT操作记录

**验证方法:**
```sql
-- 检查数据修改日志
SELECT * FROM dataUpdateLog ORDER BY timestamp DESC LIMIT 10;
```

---

## 🎯 需要完成的任务 / Tasks to Complete

### 🔴 高优先级（必须完成）/ High Priority (Must Complete)

#### 1. 集成敏感数据加密

**文件:** `backend/db_query.py`, `backend/api_handler.py`

**需要做:**
1. 在查询时自动解密敏感字段
2. 在插入/更新时自动加密敏感字段
3. 测试加密/解密功能

**代码示例:**
```python
# 在 db_query.py 中
from data_encryption import is_sensitive_field, decrypt_field_sql

# 查询时解密
if is_sensitive_field(table_name, field_name):
    # 使用解密SQL
    sql = f"SELECT {decrypt_field_sql(field_name, role)}, ... FROM {table}"
```

---

#### 2. 集成SQL注入检测

**文件:** `backend/api_handler.py`

**需要做:**
1. 在所有接收用户输入的端点中检测SQL注入
2. 记录SQL注入尝试
3. 阻止可疑请求

**代码示例:**
```python
from security_monitor import validate_input_for_sql_injection

# 在 do_POST 方法中
data = read_json(self) or {}
is_safe, detected_patterns = validate_input_for_sql_injection(
    data, 
    user_id=auth.get("personId") if auth else None,
    ip_address=self.client_address[0]
)
if not is_safe:
    return json_response(self, 400, {"error": "Invalid input detected"})
```

---

#### 3. 集成审计日志

**文件:** `backend/api_handler.py`, `backend/db_query.py`

**需要做:**
1. 记录所有数据库操作
2. 记录所有登录尝试
3. 记录所有安全事件

**代码示例:**
```python
from audit_logger import log_audit_event, log_sql_execution

# 记录SQL执行
log_sql_execution('SELECT', 'students', user_id, user_role, sql, ip_address)
```

---

#### 4. 运行数据库脚本

**需要做:**
1. 运行 `sql/create_audit_tables.sql` 创建审计表
2. 运行 `sql/setup_db_permissions.sql` 设置数据库权限（如果存在）
3. 验证表已创建

**命令:**
```bash
mysql -u root -p ComputingU < sql/create_audit_tables.sql
```

---

#### 5. 数据迁移到加密格式

**需要做:**
1. 创建数据迁移脚本
2. 迁移现有数据到加密格式
3. 验证数据完整性

**代码示例:**
```sql
-- 迁移脚本示例
UPDATE students 
SET identification_number = AES_ENCRYPT(identification_number, 'encryption_key')
WHERE identification_number IS NOT NULL;
```

---

### 🟡 中优先级（建议完成）/ Medium Priority (Recommended)

#### 6. 配置环境变量

**需要做:**
1. 设置加密密钥
2. 设置数据库用户
3. 配置其他环境变量

**环境变量:**
```bash
# 加密密钥
export ENCRYPTION_KEY_STUDENT="your_student_key_here"
export ENCRYPTION_KEY_GUARDIAN="your_guardian_key_here"
export ENCRYPTION_KEY_ARO="your_aro_key_here"
export ENCRYPTION_KEY_DRO="your_dro_key_here"
export ENCRYPTION_KEY_ROOT="your_root_key_here"

# 数据库用户
export DB_APP_USER="app_user"
export DB_APP_PASSWORD="your_secure_password_here"
```

---

#### 7. 测试所有功能

**需要做:**
1. 测试SQL注入防护
2. 测试加密/解密功能
3. 测试审计日志记录
4. 测试角色权限控制
5. 测试数据修改日志

---

## 📊 完成度评估 / Completion Assessment

### ✅ 已完成（约70%）:

1. ✅ 数据库设计 - 100%
2. ✅ 角色权限控制 - 100%
3. ✅ SQL注入防护 - 100%（代码层面）
4. ✅ 密码安全存储 - 100%
5. ✅ Web界面 - 100%
6. ✅ 数据修改日志 - 100%
7. ✅ 安全模块创建 - 100%

### ⚠️ 需要集成（约20%）:

1. ⚠️ 敏感数据加密集成 - 0%
2. ⚠️ SQL注入检测集成 - 0%
3. ⚠️ 审计日志集成 - 0%

### ⚠️ 需要配置（约10%）:

1. ⚠️ 运行数据库脚本 - 0%
2. ⚠️ 数据迁移 - 0%
3. ⚠️ 环境变量配置 - 0%

---

## 🎯 完成步骤 / Completion Steps

### Step 1: 运行数据库脚本（5分钟）

```bash
# 创建审计表
mysql -u root -p ComputingU < sql/create_audit_tables.sql

# 验证表已创建
mysql -u root -p ComputingU -e "SHOW TABLES LIKE '%audit%';"
```

---

### Step 2: 集成SQL注入检测（30分钟）

**文件:** `backend/api_handler.py`

在 `do_POST` 方法开始处添加：
```python
from security_monitor import validate_input_for_sql_injection

# 在读取JSON数据后
data = read_json(self) or {}
if data:
    is_safe, detected_patterns = validate_input_for_sql_injection(
        data,
        user_id=auth.get("personId") if auth else None,
        ip_address=self.client_address[0]
    )
    if not is_safe:
        return json_response(self, 400, {"error": "Invalid input detected"})
```

---

### Step 3: 集成审计日志（30分钟）

**文件:** `backend/api_handler.py`, `backend/db_query.py`

在关键位置添加审计日志：
```python
from audit_logger import log_audit_event, log_sql_execution

# 在登录后
log_audit_event('login', {'email': email}, user_id, user_role, ip_address)

# 在SQL执行后
log_sql_execution('SELECT', table, user_id, user_role, sql, ip_address)
```

---

### Step 4: 集成敏感数据加密（1-2小时）

**文件:** `backend/db_query.py`, `backend/api_handler.py`

需要修改查询逻辑以支持加密/解密。

---

### Step 5: 数据迁移（30分钟）

创建并运行数据迁移脚本。

---

### Step 6: 测试（1小时）

测试所有功能，确保一切正常工作。

---

## 📝 团队协作建议 / Team Collaboration Suggestions

### 任务分配建议 / Task Assignment

1. **成员A:** 集成SQL注入检测和审计日志
2. **成员B:** 集成敏感数据加密
3. **成员C:** 数据迁移和测试
4. **成员D:** 文档和最终检查

### 协作工具 / Collaboration Tools

1. **版本控制:** 使用Git分支，每个功能一个分支
2. **代码审查:** 合并前进行代码审查
3. **测试:** 每个功能完成后进行测试
4. **文档:** 更新文档记录所有更改

---

## ✅ 最终检查清单 / Final Checklist

在提交项目前，确保：

- [ ] 所有数据库表已创建
- [ ] 所有敏感数据已加密
- [ ] SQL注入防护已集成并测试
- [ ] 审计日志已集成并测试
- [ ] 所有角色权限已测试
- [ ] 数据修改日志正常工作
- [ ] 所有功能已测试
- [ ] 文档已更新
- [ ] 代码已审查
- [ ] 环境变量已配置

---

## 📚 相关文档 / Related Documentation

- `PROJECT_REQUIREMENTS_CHECKLIST.md` - 项目要求检查清单
- `REQUIREMENTS_FULFILLMENT_SUMMARY.md` - 要求完成总结
- `BACKEND_EVALUATION_REPORT_CN.md` - 后端评估报告（中文）
- `CHANGELOG.md` - 代码更改日志

---

**最后更新:** 2024  
**维护者:** 开发团队



