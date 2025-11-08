# 快速修复指南 - 认证令牌问题
# Quick Fix Guide - Authentication Token Issue

## 🔧 问题 (Problem)

运行测试时看到：
```
✗ Server returned status code: 400
  Error message: Password must be at least 8 characters long
✗ Could not get authentication token - some tests will be skipped
```

## ✅ 解决方法 (Solution)

### 方法 1: 创建测试用户（推荐）

**步骤:**

1. **打开命令行，进入项目根目录**
   ```bash
   cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
   ```

2. **进入backend文件夹并运行设置脚本**
   ```bash
   cd backend
   python setup_test_user.py
   ```

3. **你应该看到类似这样的输出:**
   ```
   ✓ Test student account updated (ID: 100)
   ✓ Test staff account updated (ID: 5001)
   ✓ Test guardian account updated (ID: 1000)
   ```

4. **回到项目根目录，重新运行测试**
   ```bash
   cd ..
   python backend/attack/run_sql_security_tests.py
   ```

**现在应该可以成功获取认证令牌了！** ✅

---

### 方法 2: 使用现有测试用户凭据

如果你已经运行过 `setup_test_user.py`，可以直接使用测试用户：

```bash
python backend/attack/run_sql_security_tests.py \
    --email test_student@example.com \
    --password StudentTest123
```

**可用的测试账户:**

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 学生 | `test_student@example.com` | `StudentTest123` |
| 员工 | `test_staff@example.com` | `StaffTest123` |
| 监护人 | `test_guardian@example.com` | `GuardianTest123` |

---

## 📝 完整步骤示例 (Complete Step-by-Step Example)

### 第一次运行测试

```bash
# 步骤 1: 进入项目根目录
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP

# 步骤 2: 创建测试用户（只需要运行一次）
cd backend
python setup_test_user.py
cd ..

# 步骤 3: 运行测试
python backend/attack/run_sql_security_tests.py
```

### 后续运行测试

```bash
# 直接运行即可（测试用户已创建）
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
python backend/attack/run_sql_security_tests.py
```

---

## 🎯 预期结果 (Expected Result)

修复后，你应该看到：

```
Step 1: Getting authentication token...
步骤1: 获取认证令牌...
✓ Successfully authenticated as test_student@example.com

Test 1: Testing login endpoint SQL injection...
测试1: 测试登录端点SQL注入...
  Completed: 7 tests

Test 2: Testing query endpoint SQL injection...
测试2: 测试查询端点SQL注入...
  Completed: 8 tests

Test 3: Testing update endpoint SQL injection...
测试3: 测试更新端点SQL注入...
  Completed: 6 tests

... (所有测试都会运行，不会被跳过)
```

---

## ❓ 常见问题 (FAQ)

### Q: 为什么需要测试用户？

**A:** 部分测试需要登录才能进行，就像测试"只有登录用户才能访问"的功能。测试用户让我们可以安全地测试这些功能，而不会影响真实用户数据。

### Q: 测试用户会影响我的真实数据吗？

**A:** 不会！`setup_test_user.py` 只会修改特定的测试账户（ID: 100, 5001, 1000），不会影响其他用户或系统功能。

### Q: 我可以使用自己的账户吗？

**A:** 可以！使用 `--email` 和 `--password` 参数：

```bash
python backend/attack/run_sql_security_tests.py \
    --email your@email.com \
    --password YourPassword123
```

**注意:** 确保密码符合要求（至少8个字符，包含字母和数字）。

### Q: 如果 setup_test_user.py 报错怎么办？

**A:** 可能的原因：
1. **数据库未运行** - 确保Percona Server/MySQL正在运行
2. **测试用户不存在** - 脚本会跳过不存在的用户，这是正常的
3. **数据库连接失败** - 检查 `backend/db_connector.py` 中的数据库配置

---

## 🔍 验证测试用户是否创建成功

运行以下命令验证：

```bash
cd backend
python -c "from db_query import db_query; result = db_query('SELECT StuID, email FROM students WHERE StuID = 100'); print('Student:', result[0] if result else 'Not found')"
```

应该看到：
```
Student: {'StuID': 100, 'email': 'test_student@example.com'}
```

---

## 📊 测试结果说明

### 有认证令牌时

- ✅ 所有测试都会运行
- ✅ 可以测试所有端点的SQL注入
- ✅ 完整的测试覆盖

### 没有认证令牌时

- ⚠️ 登录端点测试仍然运行（不需要认证）
- ⚠️ 其他端点测试被跳过（需要认证）
- ⚠️ 仍然可以看到系统的基本安全状态

**建议:** 创建测试用户以获得完整的测试结果。

---

## 🎉 总结

1. **运行一次** `python backend/setup_test_user.py` 创建测试用户
2. **然后运行** `python backend/attack/run_sql_security_tests.py` 进行完整测试
3. **或者使用** `--email` 和 `--password` 参数指定现有用户

就这么简单！🚀

---

**最后更新:** 2024

