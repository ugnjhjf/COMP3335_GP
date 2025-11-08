# 项目要求检查清单 / Project Requirements Checklist

## 📋 项目要求分析 / Requirements Analysis

### ✅ 已实现的要求 / Implemented Requirements:

1. ✅ **SQL注入防护** (Section 5.4.a.i)
   - 状态：已实现参数化查询和输入验证
   - 位置：`db_query.py`, `api_handler.py`, `security.py`

2. ✅ **密码存储** (Section 5.4.a.ii)
   - 状态：已升级到bcrypt
   - 位置：`auth.py`

3. ✅ **角色权限控制** (Section 2)
   - 状态：已实现基于角色的访问控制
   - 位置：`privilege_controller.py`

4. ✅ **数据修改日志** (Section 5.5.b)
   - 状态：已实现基础日志
   - 位置：`logger.py`, `logger_config.py`

---

### ❌ 仍需实现的要求 / Missing Requirements:

#### 🔴 关键要求（必须实现）/ Critical Requirements:

1. **敏感数据加密** (Section 5.3)
   - **要求：** 使用TDE或MySQL加密函数（AES_ENCRYPT）
   - **要求：** 密钥不能存储在数据库中
   - **要求：** 密钥管理，角色和密钥匹配
   - **当前状态：** ❌ 未实现
   - **需要加密的字段：**
     - `students.identification_number` (身份证号)
     - `students.address` (地址)
     - `staffs.identification_number` (身份证号)
     - `staffs.address` (地址)
     - `guardians.address` (地址，如果有)

2. **访问监控增强** (Section 5.5.a)
   - **要求：** 记录不当访问
   - **要求：** 记录SQL注入尝试
   - **要求：** 记录策略违反
   - **当前状态：** ⚠️ 部分实现（需要增强）

3. **防止跳过登录直接访问数据库** (用户额外要求)
   - **要求：** 防止攻击者绕过登录直接访问数据库
   - **当前状态：** ❌ 未实现
   - **需要实现：**
     - 数据库用户权限限制
     - 强制认证检查
     - 审计日志记录所有数据库访问
     - 防止直接SQL执行

---

## 🎯 需要实现的改进 / Required Improvements

### 1. 敏感数据加密 (Section 5.3) - 🔴 高优先级

#### 1.1 识别敏感字段
根据项目要求，以下字段需要加密：
- `students.identification_number` - 身份证号
- `students.address` - 地址
- `staffs.identification_number` - 身份证号
- `staffs.address` - 地址

#### 1.2 实现方案
- **使用MySQL的AES_ENCRYPT/AES_DECRYPT函数**
- **密钥存储在应用层（环境变量或密钥文件）**
- **不同角色使用不同密钥（密钥管理）**

#### 1.3 需要创建的文件
- `backend/data_encryption.py` - 数据加密/解密模块
- `sql/migrate_to_encrypted.sql` - 数据迁移脚本
- `backend/key_management.py` - 密钥管理模块

---

### 2. 访问监控增强 (Section 5.5.a) - 🔴 高优先级

#### 2.1 SQL注入尝试检测
- 检测可疑SQL模式（如 `' OR '1'='1`, `; DROP TABLE`, `UNION SELECT`）
- 记录所有SQL注入尝试
- 记录IP地址、用户ID、时间戳

#### 2.2 策略违反检测
- 检测未授权访问尝试
- 检测权限提升尝试
- 检测数据范围违反（如学生访问其他学生数据）

#### 2.3 需要创建的文件
- `backend/security_monitor.py` - 安全监控模块
- `sql/create_audit_tables.sql` - 审计表创建脚本

---

### 3. 防止跳过登录直接访问数据库 - 🔴 高优先级

#### 3.1 数据库用户权限限制
- 应用层数据库用户只能通过应用访问
- 限制直接SQL执行权限
- 使用存储过程或视图限制访问

#### 3.2 强制认证检查
- 所有数据库操作必须通过认证
- 记录所有数据库访问（包括失败的）
- 检测异常访问模式

#### 3.3 审计日志
- 记录所有数据库连接
- 记录所有SQL执行
- 记录访问来源（IP、用户、时间）

#### 3.4 需要创建的文件
- `backend/db_access_control.py` - 数据库访问控制
- `sql/setup_db_permissions.sql` - 数据库权限设置脚本
- `backend/audit_logger.py` - 审计日志模块

---

## 📝 详细实现计划 / Implementation Plan

### Phase 1: 敏感数据加密 (1-2周)

1. **创建加密模块** (`backend/data_encryption.py`)
   - 实现AES加密/解密函数
   - 密钥管理（从环境变量或文件加载）
   - 角色密钥映射

2. **修改数据库查询** (`backend/db_query.py`)
   - 查询时自动解密敏感字段
   - 插入/更新时自动加密敏感字段

3. **数据迁移** (`sql/migrate_to_encrypted.sql`)
   - 迁移现有数据到加密格式
   - 验证数据完整性

4. **密钥管理** (`backend/key_management.py`)
   - 不同角色使用不同密钥
   - 密钥轮换支持

---

### Phase 2: 访问监控增强 (1周)

1. **SQL注入检测** (`backend/security_monitor.py`)
   - 检测可疑SQL模式
   - 记录SQL注入尝试
   - 自动阻止可疑请求

2. **策略违反检测**
   - 检测未授权访问
   - 检测数据范围违反
   - 记录所有违反事件

3. **审计表** (`sql/create_audit_tables.sql`)
   - `audit_log` - 审计日志表
   - `security_events` - 安全事件表
   - `access_violations` - 访问违反表

---

### Phase 3: 防止直接数据库访问 (1-2周)

1. **数据库权限设置** (`sql/setup_db_permissions.sql`)
   - 创建应用层数据库用户
   - 限制直接SQL执行权限
   - 只允许通过应用访问

2. **访问控制模块** (`backend/db_access_control.py`)
   - 强制认证检查
   - 记录所有数据库访问
   - 检测异常访问模式

3. **审计日志** (`backend/audit_logger.py`)
   - 记录所有数据库连接
   - 记录所有SQL执行
   - 记录访问来源

---

## 🔧 技术实现细节 / Technical Details

### 1. 敏感数据加密实现

#### 使用MySQL AES_ENCRYPT/AES_DECRYPT
```sql
-- 加密
INSERT INTO students (identification_number, ...) 
VALUES (AES_ENCRYPT('123456789', 'encryption_key'), ...)

-- 解密
SELECT AES_DECRYPT(identification_number, 'encryption_key') as identification_number, ...
FROM students
```

#### 密钥管理
- 密钥存储在环境变量或密钥文件中
- 不同角色使用不同密钥
- 密钥轮换支持

---

### 2. SQL注入检测实现

#### 检测模式
```python
SQL_INJECTION_PATTERNS = [
    r"('|(\\')|(;)|(--)|(/\*)|(\*/)|(xp_)|(exec)|(execute)|(union)|(select)|(drop)|(delete)|(insert)|(update)|(alter)|(create))",
    r"(\bor\b.*=.*)|(\band\b.*=.*)",
    r"(;.*drop)|(;.*delete)|(;.*truncate)",
    r"(union.*select)|(select.*union)",
]
```

#### 检测流程
1. 检查所有用户输入
2. 匹配可疑模式
3. 记录安全事件
4. 阻止可疑请求

---

### 3. 数据库访问控制实现

#### 数据库用户权限
```sql
-- 创建应用层用户（只读权限）
CREATE USER 'app_readonly'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT ON ComputingU.* TO 'app_readonly'@'localhost';

-- 创建应用层用户（读写权限）
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.* TO 'app_user'@'localhost';

-- 禁止直接执行DDL
REVOKE CREATE, DROP, ALTER ON *.* FROM 'app_user'@'localhost';
```

#### 强制认证检查
- 所有数据库操作必须通过认证
- 记录所有数据库访问
- 检测异常访问模式

---

## 📊 优先级排序 / Priority Ranking

| 优先级 | 功能 | 项目要求 | 难度 | 时间 |
|--------|------|---------|------|------|
| 🔴 P0 | 敏感数据加密 | Section 5.3 | 高 | 1-2周 |
| 🔴 P0 | 访问监控增强 | Section 5.5.a | 中 | 1周 |
| 🔴 P0 | 防止直接数据库访问 | 用户要求 | 中 | 1-2周 |
| 🟡 P1 | 密钥管理 | Section 5.3.c | 中 | 3天 |
| 🟡 P1 | 审计日志增强 | Section 5.5.b | 低 | 3天 |

---

## ✅ 完成标准 / Completion Criteria

### 敏感数据加密
- [ ] 所有敏感字段已加密存储
- [ ] 查询时自动解密
- [ ] 插入/更新时自动加密
- [ ] 密钥不存储在数据库中
- [ ] 不同角色使用不同密钥

### 访问监控
- [ ] SQL注入尝试被检测和记录
- [ ] 策略违反被检测和记录
- [ ] 不当访问被检测和记录
- [ ] 所有安全事件记录到审计表

### 防止直接数据库访问
- [ ] 数据库用户权限已限制
- [ ] 所有数据库访问通过认证
- [ ] 所有数据库访问记录到审计日志
- [ ] 异常访问模式被检测

---

## 📚 相关文档 / Related Documentation

- 项目要求文档
- `IMPROVEMENTS_NEEDED.md` - 改进需求
- `SECURITY_FIXES_SUMMARY.md` - 安全修复总结

