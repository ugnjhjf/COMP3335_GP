# Auth模块攻击测试 / Auth Module Attack Tests

本目录包含针对auth模块的3个简单攻击测试，用于验证系统的安全防护能力。

This directory contains 3 simple attack tests for the auth module to verify the system's security protection capabilities.

## 测试文件 / Test Files

### 1. `auth_bruteforce_attack.py` - 暴力破解攻击测试
**测试内容:**
- 尝试使用常见弱密码列表暴力破解用户账户
- 测试系统是否有速率限制和账户锁定机制

**运行方式:**
```bash
cd backend/attack
python auth_bruteforce_attack.py
```

**预期结果:**
- 系统应该拒绝所有暴力破解尝试
- 如果成功，说明系统缺少速率限制保护

---

### 2. `auth_sql_injection_attack.py` - SQL注入攻击测试
**测试内容:**
- 在email字段尝试各种SQL注入payload
- 检测系统是否使用参数化查询
- 测试时间盲注、布尔盲注等攻击方式

**运行方式:**
```bash
cd backend/attack
python auth_sql_injection_attack.py
```

**预期结果:**
- 所有SQL注入payload应该被拒绝
- 系统应该使用参数化查询（已实现）
- 不应该返回SQL错误信息

---

### 3. `auth_session_attack.py` - 会话攻击测试
**测试内容:**
- 会话固定攻击：尝试使用可预测的token
- 过期会话攻击：尝试使用过期或无效的token
- 会话重放攻击：重复使用已使用的token

**运行方式:**
```bash
cd backend/attack
python auth_session_attack.py
```

**预期结果:**
- 所有伪造的token应该被拒绝
- 系统应该正确验证会话过期时间
- 会话应该使用安全的随机token生成

---

## 运行前准备 / Prerequisites

1. **确保服务器正在运行**
   ```bash
   cd backend
   python main.py
   ```

2. **安装依赖**
   ```bash
   pip install requests
   ```

3. **修改测试配置**
   - 在测试文件中修改 `BASE_URL` 如果服务器运行在不同端口
   - 修改测试邮箱和密码以匹配实际数据库中的用户

## 注意事项 / Notes

⚠️ **警告: 这些是攻击测试脚本，仅用于安全测试目的**

- 这些测试会向服务器发送大量请求
- 建议在测试环境中运行，不要在生产环境使用
- 测试可能会在日志中产生大量记录
- 某些测试可能需要调整以匹配实际的API端点

## 安全建议 / Security Recommendations

如果测试发现漏洞，建议实施以下安全措施：

1. **暴力破解防护**
   - 实施登录速率限制（rate limiting）
   - 实施账户锁定机制（多次失败后锁定）
   - 使用验证码（CAPTCHA）

2. **SQL注入防护**
   - ✅ 使用参数化查询（已实现）
   - ✅ 输入验证和清理（已实现）
   - 实施WAF（Web应用防火墙）

3. **会话管理**
   - ✅ 使用安全的随机token生成（已实现）
   - ✅ 会话过期验证（已实现）
   - 实施会话固定保护
   - 使用HttpOnly和Secure cookie标志

---

**最后更新:** 2024  
**维护者:** 开发团队

