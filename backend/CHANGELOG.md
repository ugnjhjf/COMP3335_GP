# 代码更改日志 / Code Changelog

**项目:** COMP3335_GP Backend  
**最后更新:** 2024  
**维护者:** 开发团队

---

## 更改记录 / Change History

### 2024 - 后端代码评估与安全增强

#### 🔧 修复的Bug / Bug Fixes

##### 1. 连接池Bug修复 (logger.py)
**日期:** 2024  
**文件:** `backend/logger.py`  
**问题:** 使用 `conn.close()` 直接关闭连接，导致连接池无法正常工作  
**修复:** 改为使用 `return_db_connection(conn)` 将连接返回到连接池  
**影响:** 修复后连接池可以正常工作，提高性能和资源利用率

**更改详情:**
```python
# 修改前:
from db_connector import get_db_connection
conn.close()

# 修改后:
from db_connector import get_db_connection, return_db_connection
return_db_connection(conn)
```

**相关文件:**
- `backend/logger.py` (第2行, 第17行)

---

#### 🔒 安全增强 / Security Enhancements

##### 2. SQL注入防护增强 (security.py)
**日期:** 2024  
**文件:** `backend/security.py`  
**目的:** 增强SQL注入防护，添加标识符转义和白名单验证功能  
**新增功能:**
- `escape_identifier()`: 安全转义SQL标识符（表名/列名）
- `validate_table_name_whitelist()`: 基于白名单验证表名（更安全）

**新增代码:**
```python
def escape_identifier(identifier):
    """转义SQL标识符以防止注入"""
    # 验证并转义标识符
    
def validate_table_name_whitelist(table_name, allowed_tables=None):
    """根据白名单验证表名（更安全）"""
    # 先验证格式，再检查白名单
```

**相关文件:**
- `backend/security.py` (第197-244行)

---

##### 3. API端点SQL注入防护增强 (api_handler.py)
**日期:** 2024  
**文件:** `backend/api_handler.py`  
**目的:** 在所有API端点中使用白名单验证，增强SQL注入防护  
**更改内容:**
1. 导入新的安全函数
2. 在 `/performQuery` 端点使用白名单验证
3. 在 `/data/update` 端点使用白名单验证
4. 在 `/data/delete` 端点使用白名单验证
5. 在 `/data/insert` 端点使用白名单验证并转义列名

**更改详情:**
```python
# 修改前:
if not validate_table_name(table):
    return json_response(self, 400, {"error": "Invalid table name"})
if table not in ROLE_TABLES.get(auth["role"], []):
    return json_response(self, 403, {"error": "Forbidden"})

# 修改后:
allowed_tables = ROLE_TABLES.get(auth["role"], [])
if not validate_table_name_whitelist(table, allowed_tables):
    return json_response(self, 400, {"error": "Invalid table name"})
if table not in allowed_tables:
    return json_response(self, 403, {"error": "Forbidden"})
```

**INSERT端点额外增强:**
```python
# 验证并转义列名（增强SQL注入防护）
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

**相关文件:**
- `backend/api_handler.py` (第16-19行, 第171-177行, 第338-346行, 第402-410行, 第456-475行)

---

#### 📝 文档添加 / Documentation Added

##### 4. 后端代码评估报告 (英文)
**日期:** 2024  
**文件:** `backend/BACKEND_EVALUATION_REPORT.md`  
**内容:** 完整的后端代码评估报告，包括：
- 运行评估
- 安全分析（10种攻击向量）
- 关键问题总结
- 攻击防护矩阵
- 优先级建议

**相关文件:**
- `backend/BACKEND_EVALUATION_REPORT.md`

---

##### 5. 后端代码评估报告 (中文)
**日期:** 2024  
**文件:** `backend/BACKEND_EVALUATION_REPORT_CN.md`  
**内容:** 完整的中文版后端代码评估报告

**相关文件:**
- `backend/BACKEND_EVALUATION_REPORT_CN.md`

---

##### 6. 代码更改日志 (本文件)
**日期:** 2024  
**文件:** `backend/CHANGELOG.md`  
**内容:** 记录所有代码更改，便于团队协作

**相关文件:**
- `backend/CHANGELOG.md` (本文件)

---

## SQL注入防护说明 / SQL Injection Protection Notes

### 当前防护措施 / Current Protection Measures

#### ✅ 已实现的防护 / Implemented Protections

1. **参数化查询** (Parameterized Queries)
   - 所有用户输入的值都使用参数化查询
   - 位置: `api_handler.py` 所有查询操作
   - 状态: ✅ 已实现

2. **表名验证** (Table Name Validation)
   - 使用正则表达式验证表名格式
   - 只允许字母数字和下划线
   - 位置: `security.py:validate_table_name()`
   - 状态: ✅ 已实现

3. **列名验证** (Column Name Validation)
   - 使用正则表达式验证列名格式
   - 只允许字母数字、下划线和反引号
   - 位置: `security.py:validate_column_name()`
   - 状态: ✅ 已实现

4. **白名单验证** (Whitelist Validation) ⭐ 新增
   - 基于角色的表名白名单验证
   - 双重验证：格式验证 + 白名单检查
   - 位置: `security.py:validate_table_name_whitelist()`
   - 状态: ✅ 已实现

5. **标识符转义** (Identifier Escaping) ⭐ 新增
   - 安全转义表名和列名
   - 使用反引号转义
   - 位置: `security.py:escape_identifier()`
   - 状态: ✅ 已实现

#### ⚠️ 为什么需要这些措施？/ Why These Measures?

**问题:** MySQL不支持参数化表名和列名  
**解决方案:** 
1. 验证格式（防止特殊字符）
2. 白名单验证（只允许已知的表名）
3. 转义标识符（使用反引号）

**示例攻击场景:**
```sql
-- 恶意输入: table_name = "students; DROP TABLE students; --"
-- 如果直接拼接: SELECT * FROM students; DROP TABLE students; --
-- 防护措施:
-- 1. 格式验证: 拒绝（包含分号和空格）
-- 2. 白名单验证: 拒绝（不在允许列表中）
-- 3. 转义: `students; DROP TABLE students; --` (即使通过验证也会被转义)
```

#### 🔍 防护层级 / Protection Layers

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

---

## 建议的后续改进 / Recommended Future Improvements

### 🔴 高优先级 / High Priority

1. **集成CSRF防护**
   - 状态: ❌ 未实现
   - 优先级: P0
   - 说明: CSRF防护模块存在但未在API中使用
   - 建议: 在所有状态改变操作中验证CSRF令牌

2. **实现速率限制**
   - 状态: ❌ 未实现
   - 优先级: P1
   - 说明: 登录端点无速率限制，易受暴力破解攻击
   - 建议: 实现每IP每分钟最多5次登录尝试

### 🟡 中优先级 / Medium Priority

3. **移除开发跟踪**
   - 状态: ⚠️ 部分完成
   - 优先级: P1
   - 说明: 某些地方仍使用 `traceback.print_exc()`
   - 建议: 移除或根据DEBUG模式条件启用

4. **配置生产环境CORS**
   - 状态: ⚠️ 需要配置
   - 优先级: P1
   - 说明: 默认允许所有来源（仅开发环境）
   - 建议: 在生产环境中设置 `CORS_ALLOWED_ORIGINS`

### 🟢 低优先级 / Low Priority

5. **启用数据库会话**
   - 状态: ⚠️ 可选
   - 优先级: P2
   - 说明: 默认使用内存存储，重启后丢失
   - 建议: 设置 `USE_DB_SESSIONS=true`

---

## 测试建议 / Testing Recommendations

### SQL注入测试 / SQL Injection Testing

建议测试以下场景：

1. **表名注入测试**
   ```python
   # 测试用例
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
   # 测试用例
   test_cases = [
       "name; DROP TABLE students; --",
       "name' OR '1'='1",
       "name UNION SELECT password FROM users",
   ]
   # 预期结果: 所有测试用例都应被拒绝
   ```

3. **值注入测试**
   ```python
   # 测试用例
   test_cases = [
       "'; DROP TABLE students; --",
       "' OR '1'='1",
       "1' UNION SELECT * FROM passwords--",
   ]
   # 预期结果: 参数化查询应防止所有注入
   ```

---

## 协作说明 / Collaboration Notes

### 对于团队成员 / For Team Members

**重要更改摘要:**
1. ✅ 修复了连接池bug - 所有使用数据库连接的地方现在都正确使用连接池
2. ✅ 增强了SQL注入防护 - 添加了白名单验证和标识符转义
3. ✅ 创建了评估报告 - 详细说明了代码的安全状态

**需要了解的内容:**
- 所有表名现在都经过白名单验证（基于角色）
- INSERT操作中的列名现在都经过验证和转义
- 连接池现在在所有地方都正确工作

**下一步行动:**
- 查看评估报告了解当前安全状态
- 考虑实现CSRF防护（高优先级）
- 考虑实现速率限制（高优先级）

---

## 版本历史 / Version History

| 版本 | 日期 | 更改摘要 |
|------|------|---------|
| 1.0.0 | 2024 | 初始评估和修复 |
| | | - 修复连接池bug |
| | | - 增强SQL注入防护 |
| | | - 添加评估报告 |

---

**最后更新:** 2024  
**维护者:** 开发团队  
**联系方式:** 通过项目仓库

