# 代码更改总结 / Code Changes Summary

**项目:** COMP3335_GP Backend  
**日期:** 2024  
**目的:** 记录所有代码更改，便于团队协作

---

## 📋 更改总览 / Changes Overview

本次评估和修复共进行了以下更改：

### ✅ 已完成的更改 / Completed Changes

1. **修复连接池Bug** ✅
2. **增强SQL注入防护** ✅
3. **创建评估报告** ✅
4. **创建更改日志** ✅

---

## 🔧 详细更改列表 / Detailed Changes List

### 1. 修复连接池Bug (logger.py)

**文件:** `backend/logger.py`  
**问题:** 使用 `conn.close()` 直接关闭连接，导致连接池无法正常工作  
**修复:** 改为使用 `return_db_connection(conn)` 将连接返回到连接池

**更改前:**
```python
from db_connector import get_db_connection
# ...
conn.close()
```

**更改后:**
```python
from db_connector import get_db_connection, return_db_connection
# ...
return_db_connection(conn)
```

**影响:** 
- ✅ 连接池现在可以正常工作
- ✅ 提高性能和资源利用率
- ✅ 防止连接泄漏

---

### 2. 增强SQL注入防护 (security.py)

**文件:** `backend/security.py`  
**目的:** 添加更强大的SQL注入防护功能

#### 2.1 新增函数: `escape_identifier()`

**功能:** 安全转义SQL标识符（表名/列名）  
**位置:** `backend/security.py` 第197-222行

```python
def escape_identifier(identifier):
    """
    Escape SQL identifier (table/column name) to prevent injection
    转义SQL标识符（表名/列名）以防止注入
    """
    # 1. 验证标识符格式
    # 2. 使用反引号转义
    # 3. 返回转义后的标识符
```

**用途:** 在构建SQL查询时安全地转义表名和列名

#### 2.2 新增函数: `validate_table_name_whitelist()`

**功能:** 基于白名单验证表名（更安全）  
**位置:** `backend/security.py` 第224-244行

```python
def validate_table_name_whitelist(table_name, allowed_tables=None):
    """
    Validate table name against whitelist (more secure)
    根据白名单验证表名（更安全）
    """
    # 1. 先验证格式
    # 2. 再检查白名单
    # 3. 双重验证确保安全
```

**用途:** 在API端点中验证表名，确保只允许已知的表名

**优势:**
- ✅ 双重验证（格式 + 白名单）
- ✅ 基于角色的访问控制
- ✅ 防止未知表名访问

---

### 3. 增强API端点SQL注入防护 (api_handler.py)

**文件:** `backend/api_handler.py`  
**目的:** 在所有API端点中使用白名单验证和标识符转义

#### 3.1 导入新函数

**位置:** `backend/api_handler.py` 第16-20行

**更改前:**
```python
from security import (
    decrypt_password, validate_email, validate_password, 
    sanitize_input, validate_table_name, validate_column_name
)
```

**更改后:**
```python
from security import (
    decrypt_password, validate_email, validate_password, 
    sanitize_input, validate_table_name, validate_column_name,
    validate_table_name_whitelist, escape_identifier  # 新增
)
```

#### 3.2 更新 `/performQuery` 端点

**位置:** `backend/api_handler.py` 第172-179行

**更改前:**
```python
if not validate_table_name(table):
    return json_response(self, 400, {"error": "Invalid table name"})
if table not in ROLE_TABLES.get(auth["role"], []):
    return json_response(self, 403, {"error": "Forbidden"})
```

**更改后:**
```python
allowed_tables = ROLE_TABLES.get(auth["role"], [])
if not validate_table_name_whitelist(table, allowed_tables):
    return json_response(self, 400, {"error": "Invalid table name"})
if table not in allowed_tables:
    return json_response(self, 403, {"error": "Forbidden"})
```

**改进:**
- ✅ 使用白名单验证（更安全）
- ✅ 双重验证确保表名安全

#### 3.3 更新 `/data/update` 端点

**位置:** `backend/api_handler.py` 第338-346行

**更改:** 与 `/performQuery` 相同，使用白名单验证

#### 3.4 更新 `/data/delete` 端点

**位置:** `backend/api_handler.py` 第402-410行

**更改:** 与 `/performQuery` 相同，使用白名单验证

#### 3.5 更新 `/data/insert` 端点（额外增强）

**位置:** `backend/api_handler.py` 第459-485行

**更改1: 白名单验证**
```python
allowed_tables = ROLE_TABLES.get(auth["role"], [])
if not validate_table_name_whitelist(table, allowed_tables):
    return json_response(self, 400, {"ok": False, "error": "Invalid table name"})
```

**更改2: 列名验证和转义** ⭐ 新增
```python
# 验证并转义列名
escaped_columns = []
for col in updateValueColumns:
    if not validate_column_name(col):
        return json_response(self, 400, {"ok": False, "error": f"Invalid column name: {col}"})
    escaped_col = escape_identifier(col)
    if not escaped_col:
        return json_response(self, 400, {"ok": False, "error": f"Invalid column name: {col}"})
    escaped_columns.append(escaped_col)

# 使用转义后的列名构建SQL
ColumnsStr = ', '.join(escaped_columns)
```

**改进:**
- ✅ 表名白名单验证
- ✅ 列名验证和转义
- ✅ 双重防护确保安全

---

## 🔒 SQL注入防护说明 / SQL Injection Protection Notes

### 为什么需要这些措施？/ Why These Measures?

**问题:** MySQL不支持参数化表名和列名  
**解决方案:** 多层防护机制

### 防护层级 / Protection Layers

```
用户输入
  ↓
1. 输入清理 (sanitize_input)
  ↓
2. 格式验证 (validate_table_name/validate_column_name)
  ↓
3. 白名单验证 (validate_table_name_whitelist) ⭐ 新增
  ↓
4. 标识符转义 (escape_identifier) ⭐ 新增
  ↓
5. 参数化查询 (参数值)
  ↓
安全执行
```

### 防护措施对比 / Protection Comparison

| 措施 | 之前 | 现在 |
|------|------|------|
| 表名验证 | ✅ 格式验证 | ✅ 格式验证 + 白名单验证 |
| 列名验证 | ✅ 格式验证 | ✅ 格式验证 + 转义 |
| 值验证 | ✅ 参数化查询 | ✅ 参数化查询（不变） |

### 示例攻击场景 / Attack Scenarios

#### 场景1: 表名注入

**恶意输入:**
```python
table_name = "students; DROP TABLE students; --"
```

**防护措施:**
1. ✅ 格式验证: 拒绝（包含分号和空格）
2. ✅ 白名单验证: 拒绝（不在允许列表中）
3. ✅ 即使通过验证也会被转义

**结果:** 攻击被阻止 ✅

#### 场景2: 列名注入

**恶意输入:**
```python
column_name = "name; DROP TABLE students; --"
```

**防护措施:**
1. ✅ 格式验证: 拒绝（包含分号和空格）
2. ✅ 转义: 即使通过验证也会被转义为 `` `name; DROP TABLE students; --` ``

**结果:** 攻击被阻止 ✅

#### 场景3: 值注入

**恶意输入:**
```python
value = "'; DROP TABLE students; --"
```

**防护措施:**
1. ✅ 参数化查询: 值被安全绑定，不会执行

**结果:** 攻击被阻止 ✅

---

## 📝 新增文件 / New Files

### 1. BACKEND_EVALUATION_REPORT.md

**位置:** `backend/BACKEND_EVALUATION_REPORT.md`  
**内容:** 完整的后端代码评估报告（英文）  
**包括:**
- 运行评估
- 安全分析（10种攻击向量）
- 关键问题总结
- 攻击防护矩阵
- 优先级建议

### 2. BACKEND_EVALUATION_REPORT_CN.md

**位置:** `backend/BACKEND_EVALUATION_REPORT_CN.md`  
**内容:** 完整的中文版后端代码评估报告

### 3. CHANGELOG.md

**位置:** `backend/CHANGELOG.md`  
**内容:** 详细的代码更改日志  
**包括:**
- 所有更改的详细说明
- SQL注入防护说明
- 测试建议
- 协作说明

### 4. CHANGES_SUMMARY_CN.md (本文件)

**位置:** `backend/CHANGES_SUMMARY_CN.md`  
**内容:** 代码更改总结（中文）  
**目的:** 快速了解所有更改

---

## 🎯 对团队成员的建议 / Recommendations for Team Members

### 需要了解的内容 / What You Need to Know

1. **连接池修复**
   - 所有使用数据库连接的地方现在都正确使用连接池
   - 不再需要手动关闭连接

2. **SQL注入防护增强**
   - 所有表名现在都经过白名单验证（基于角色）
   - INSERT操作中的列名现在都经过验证和转义
   - 多层防护确保安全

3. **评估报告**
   - 详细说明了代码的安全状态
   - 包含改进建议

### 下一步行动 / Next Steps

1. **查看评估报告**
   - 了解当前安全状态
   - 查看改进建议

2. **考虑实现CSRF防护** (高优先级)
   - CSRF防护模块存在但未使用
   - 需要集成到API端点

3. **考虑实现速率限制** (高优先级)
   - 登录端点无速率限制
   - 易受暴力破解攻击

---

## 📊 更改统计 / Change Statistics

| 类别 | 数量 |
|------|------|
| 修复的Bug | 1 |
| 新增安全功能 | 2 |
| 更新的API端点 | 4 |
| 新增文件 | 4 |
| 修改的文件 | 3 |

---

## ✅ 测试建议 / Testing Recommendations

### SQL注入测试

建议测试以下场景：

1. **表名注入测试**
   ```python
   test_cases = [
       "students; DROP TABLE students; --",
       "students' OR '1'='1",
       "../../etc/passwd",
       "students UNION SELECT * FROM passwords",
   ]
   # 预期结果: 所有测试用例都应被拒绝
   ```

2. **列名注入测试**
   ```python
   test_cases = [
       "name; DROP TABLE students; --",
       "name' OR '1'='1",
       "name UNION SELECT password FROM users",
   ]
   # 预期结果: 所有测试用例都应被拒绝
   ```

3. **值注入测试**
   ```python
   test_cases = [
       "'; DROP TABLE students; --",
       "' OR '1'='1",
       "1' UNION SELECT * FROM passwords--",
   ]
   # 预期结果: 参数化查询应防止所有注入
   ```

---

## 📞 联系信息 / Contact Information

如有问题或需要更多信息，请查看：
- `backend/CHANGELOG.md` - 详细更改日志
- `backend/BACKEND_EVALUATION_REPORT_CN.md` - 完整评估报告
- `backend/BACKEND_EVALUATION_REPORT.md` - 英文评估报告

---

**最后更新:** 2024  
**维护者:** 开发团队



