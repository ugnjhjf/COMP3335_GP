# 安全增强说明文档 / Security Enhancements Documentation

## 新增文件 / New Files

### 1. `backend/security.py` - 安全模块
新增的安全模块，提供以下功能：

#### 新增函数 / New Functions:

1. **`load_private_key(key_path=None)`**
   - 功能：从文件或环境变量加载RSA私钥
   - 用途：用于解密前端发送的加密密码

2. **`decrypt_password(encrypted_password_base64)`**
   - 功能：解密RSA-OAEP加密的密码
   - 用途：处理前端发送的加密密码

3. **`validate_email(email)`**
   - 功能：验证邮箱格式
   - 用途：防止无效邮箱输入

4. **`validate_password(password)`**
   - 功能：验证密码强度（至少8字符，包含字母和数字）
   - 用途：确保密码符合安全要求

5. **`sanitize_input(input_str, max_length=1000)`**
   - 功能：清理用户输入，移除危险字符
   - 用途：防止注入攻击

6. **`validate_table_name(table_name)`**
   - 功能：验证表名格式（只允许字母数字和下划线）
   - 用途：防止SQL注入

7. **`validate_column_name(column_name)`**
   - 功能：验证列名格式
   - 用途：防止SQL注入

8. **`get_allowed_origins()`**
   - 功能：从环境变量获取允许的CORS源
   - 用途：可配置的CORS策略

9. **`is_origin_allowed(origin)`**
   - 功能：检查请求源是否允许
   - 用途：CORS验证

10. **`get_public_key_pem()`**
    - 功能：获取RSA公钥的PEM格式
    - 用途：提供给前端用于密码加密

---

## 修改的文件 / Modified Files

### 1. `backend/api_handler.py`

#### 修改内容 / Changes:

1. **导入安全模块** (第15-18行)
   - 添加：`from security import ...`
   - 功能：引入安全验证函数

2. **CORS配置增强** (第23-34行)
   - 修改：`do_OPTIONS()` 方法
   - 功能：支持可配置的CORS源，添加 `X-Key-Id` 和 `Access-Control-Allow-Credentials` 头

3. **新增公钥端点** (第66-76行)
   - 添加：`/auth/public-key` GET端点
   - 功能：返回RSA公钥供前端加密密码使用

4. **登录端点增强** (第72-110行)
   - 修改：`/auth/login` POST端点
   - 新增功能：
     - 支持 `encryptedPassword` 字段
     - 邮箱格式验证
     - 密码强度验证
     - 输入清理
   - 向后兼容：如果解密失败，回退到明文密码

5. **查询端点增强** (第135-151行)
   - 修改：`/performQuery` POST端点
   - 新增：表名验证

6. **过滤器验证增强** (第229-241行)
   - 修改：过滤器处理循环
   - 新增：列名验证

7. **排序验证增强** (第282-297行)
   - 修改：排序处理循环
   - 新增：列名验证

8. **更新端点增强** (第305-318行)
   - 修改：`/data/update` POST端点
   - 新增：表名验证

9. **删除端点增强** (第366-378行)
   - 修改：`/data/delete` POST端点
   - 新增：表名验证

10. **插入端点增强** (第415-428行)
    - 修改：`/data/insert` POST端点
    - 新增：表名验证

---

### 2. `backend/communicator.py`

#### 修改内容 / Changes:

1. **导入安全模块** (第3-4行)
   - 添加：`from security import get_allowed_origins, is_origin_allowed`

2. **CORS配置增强** (第12-19行)
   - 修改：`json_response()` 函数
   - 功能：
     - 根据请求Origin动态设置CORS头
     - 添加 `X-Key-Id` 支持
     - 添加 `Access-Control-Allow-Credentials` 头

3. **文本响应CORS增强** (第32-39行)
   - 修改：`text_response()` 函数
   - 功能：与 `json_response()` 相同的CORS增强

---

### 3. `backend/db_connector.py`

#### 修改内容 / Changes:

1. **导入os模块** (第3行)
   - 添加：`import os`

2. **数据库配置改为环境变量** (第10-17行)
   - 修改：`DB_CONFIG` 字典
   - 功能：
     - 从环境变量读取数据库配置
     - 保持默认值以向后兼容
   - 环境变量：
     - `DB_HOST` (默认: '127.0.0.1')
     - `DB_PORT` (默认: '3306')
     - `DB_USER` (默认: 'root')
     - `DB_PASSWORD` (默认: 'supersecurepassword')
     - `DB_NAME` (默认: 'ComputingU')
     - `DB_CHARSET` (默认: 'utf8mb4')

---

## 环境变量配置 / Environment Variables

### 必需的环境变量（生产环境）/ Required for Production:

1. **`DB_PASSWORD`** - 数据库密码（不应使用默认值）
2. **`CORS_ALLOWED_ORIGINS`** - 允许的CORS源（逗号分隔，例如：`https://example.com,https://app.example.com`）
3. **`RSA_PRIVATE_KEY_PATH`** - RSA私钥文件路径（默认：`backend/keys/private_key.pem`）
4. **`RSA_KEY_ID`** - RSA密钥ID（可选，用于密钥轮换）

### 可选的环境变量 / Optional:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`, `DB_CHARSET` - 数据库配置

---

## 使用说明 / Usage

### 1. 生成RSA密钥对 / Generate RSA Key Pair

```bash
# 创建密钥目录
mkdir -p backend/keys

# 生成私钥
openssl genrsa -out backend/keys/private_key.pem 2048

# 生成公钥（可选，用于验证）
openssl rsa -in backend/keys/private_key.pem -pubout -out backend/keys/public_key.pem
```

### 2. 设置环境变量 / Set Environment Variables

```bash
# Linux/Mac
export DB_PASSWORD="your_secure_password"
export CORS_ALLOWED_ORIGINS="https://yourdomain.com"
export RSA_PRIVATE_KEY_PATH="backend/keys/private_key.pem"

# Windows
set DB_PASSWORD=your_secure_password
set CORS_ALLOWED_ORIGINS=https://yourdomain.com
set RSA_PRIVATE_KEY_PATH=backend/keys/private_key.pem
```

### 3. 运行服务器 / Run Server

代码会自动检测环境变量，如果未设置则使用默认值（保持向后兼容）。

---

## 安全改进总结 / Security Improvements Summary

### ✅ 已实现 / Implemented:

1. **RSA密码加密支持** - 前端可以加密密码传输
2. **输入验证** - 邮箱、密码、表名、列名验证
3. **输入清理** - 移除危险字符
4. **可配置CORS** - 通过环境变量控制允许的源
5. **环境变量配置** - 敏感信息不再硬编码
6. **表名/列名验证** - 额外的SQL注入防护层

### ⚠️ 注意事项 / Notes:

1. **向后兼容** - 所有修改都保持向后兼容，现有代码仍可运行
2. **默认值** - 如果未设置环境变量，使用默认值（开发环境）
3. **RSA密钥** - 如果未找到私钥，RSA解密功能将被禁用，但系统仍可运行（使用明文密码）
4. **CORS** - 默认允许所有源（`*`），生产环境应设置 `CORS_ALLOWED_ORIGINS`

---

## 代码注释说明 / Code Comments

所有新增的代码都包含中文和英文注释，格式为：
```python
# English comment - 中文注释
```

这些注释不会影响代码运行，仅用于说明功能。

