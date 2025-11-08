# SQL安全测试 - 超简单使用教程
# SQL Security Test - Super Simple Tutorial

> 适合没有太多计算背景的用户  
> For users without much computing background

---

## 📖 这是什么？(What is this?)

这是一个**测试工具**，用来检查你的数据库系统是否安全，防止坏人通过SQL注入攻击你的系统。

This is a **testing tool** to check if your database system is secure and prevents bad people from attacking your system through SQL injection.

---

## 🚀 快速开始 (Quick Start)

### 步骤 1: 打开命令行 (Open Command Line)

**Windows用户:**
1. 按 `Win + R` 键
2. 输入 `cmd` 或 `powershell`
3. 按回车

**或者:**
1. 在文件夹中，按住 `Shift` 键
2. 右键点击空白处
3. 选择"在此处打开PowerShell窗口"

### 步骤 2: 进入项目文件夹 (Go to Project Folder)

在命令行中输入（根据你的实际路径调整）：

```bash
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
```

**提示:** 如果路径有空格，用引号包起来：
```bash
cd "D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP"
```

### 步骤 3: 确保服务器正在运行 (Make Sure Server is Running)

**打开一个新的命令行窗口**，运行：

```bash
cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP\backend
python main.py
```

你应该看到类似这样的信息：
```
Serving on http://127.0.0.1:8000
```

**重要:** 让这个窗口保持打开状态！不要关闭它。

### 步骤 4: 创建测试用户（第一次需要）(Create Test Users - First Time Only)

在**原来的命令行窗口**中（不是运行服务器的那个），输入：

```bash
cd backend
python setup_test_user.py
cd ..
```

**这只需要运行一次！** 这会创建测试用的账户。

你应该看到：
```
✓ Test student account updated (ID: 100)
✓ Test staff account updated (ID: 5001)
✓ Test guardian account updated (ID: 1000)
```

### 步骤 5: 运行测试 (Run Tests)

在**原来的命令行窗口**中，输入：

```bash
python backend/attack/run_sql_security_tests.py
```

**注意:** 如果你已经创建了测试用户，可以直接运行测试，跳过步骤4。

---

## ❌ 常见错误和解决方法 (Common Errors & Solutions)

### 错误 1: "can't open file" 或 "No such file or directory"

**问题:** 你在错误的文件夹中运行命令

**解决方法:**
1. 确保你在项目根目录（`COMP3335_GP` 文件夹）
2. 检查路径是否正确

**检查方法:**
```bash
# 查看当前文件夹
dir    # Windows
# 或
ls     # PowerShell

# 你应该看到 backend 文件夹
```

### 错误 2: "Cannot connect to server" 或 "无法连接到服务器

**问题:** 服务器没有运行

**解决方法:**
1. 打开一个新的命令行窗口
2. 进入 `backend` 文件夹
3. 运行 `python main.py`
4. 等待看到 "Serving on http://127.0.0.1:8000"
5. 然后回到原来的窗口重新运行测试

### 错误 3: "Could not get authentication token" 或 "Password must be at least 8 characters long"

**问题:** 测试需要登录，但没有测试用户，或者默认密码不符合要求

**解决方法 1: 创建测试用户（推荐）**

```bash
# 在项目根目录运行
cd backend
python setup_test_user.py
cd ..
python backend/attack/run_sql_security_tests.py
```

这会创建以下测试账户：
- 学生: `test_student@example.com` / `StudentTest123`
- 员工: `test_staff@example.com` / `StaffTest123`
- 监护人: `test_guardian@example.com` / `GuardianTest123`

**解决方法 2: 使用现有账户运行测试**

```bash
python backend/attack/run_sql_security_tests.py \
    --email test_student@example.com \
    --password StudentTest123
```

**注意:** 
- 即使没有认证令牌，测试仍然会运行，只是部分测试会被跳过
- 登录端点测试不需要认证，仍然会运行
- 建议创建测试用户以获得完整的测试结果

### 错误 4: "TypeError" 或其他Python错误

**问题:** 代码有bug（已经修复）

**解决方法:**
1. 确保你使用的是最新版本的代码
2. 如果还有错误，检查错误信息中的行号
3. 报告错误给开发人员

---

## 📊 理解测试结果 (Understanding Test Results)

### 测试状态说明

#### ✅ PROTECTED（受保护）- 这是好的！
- 系统成功阻止了攻击
- 你的系统是安全的
- 示例: `✅ Basic OR injection: PROTECTED`

#### ❌ VULNERABLE（易受攻击）- 这是坏的！
- 系统没有阻止攻击
- 需要立即修复
- 示例: `❌ Basic OR injection: VULNERABLE`

#### ⚠️ ERROR（错误）
- 测试过程中出错了
- 可能是网络问题或服务器问题

#### ⚠️ SKIPPED（跳过）
- 测试被跳过了
- 通常是因为没有登录

### 示例输出

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

**如果看到这个，说明你的系统是安全的！** 🎉

---

## 🔧 完整测试流程 (Complete Testing Process)

### 第一次运行测试

1. **打开第一个命令行窗口**（运行服务器）
   ```bash
   cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP\backend
   python main.py
   ```
   保持这个窗口打开，你应该看到 "Serving on http://127.0.0.1:8000"

2. **打开第二个命令行窗口**（运行测试）
   ```bash
   # 进入项目根目录
   cd D:\Useful_things\Downloads\Comp3335_gp_project\COMP3335_GP
   
   # 创建测试用户（第一次需要，只需要运行一次）
   cd backend
   python setup_test_user.py
   
   # 回到项目根目录
   cd ..
   
   # 运行测试
   python backend/attack/run_sql_security_tests.py
   ```

3. **查看结果**
   - 如果所有测试显示 "PROTECTED"，说明系统安全 ✅
   - 如果有 "VULNERABLE"，需要修复 ❌
   - 如果看到 "✓ Successfully authenticated"，说明认证成功 ✅

### 后续运行测试

如果你已经创建了测试用户，只需要：

1. **运行服务器**（第一个窗口）
2. **运行测试**（第二个窗口）
   ```bash
   python backend/attack/run_sql_security_tests.py
   ```

### 保存测试结果

```bash
python backend/attack/run_sql_security_tests.py --output 测试结果.json --report 测试报告.txt
```

这会在当前文件夹创建两个文件：
- `测试结果.json` - 详细的测试数据（JSON格式）
- `测试报告.txt` - 人类可读的报告

---

## 💡 小贴士 (Tips)

### 1. 使用Tab键自动补全
在命令行中输入文件名时，按 `Tab` 键可以自动补全文件名，避免输入错误。

### 2. 复制粘贴路径
- 在文件资源管理器中，点击地址栏可以复制路径
- 在命令行中右键可以粘贴

### 3. 检查服务器是否运行
在浏览器中打开 `http://127.0.0.1:8000`，如果能看到响应，说明服务器正在运行。

### 4. 查看日志
如果测试有问题，可以查看日志文件：
- `backend/logs/app.log` - 应用日志
- `backend/logs/database.log` - 数据库日志

---

## 🆘 需要帮助？(Need Help?)

### 检查清单

运行测试前，确保：

- [ ] 你在正确的文件夹中（`COMP3335_GP`）
- [ ] 服务器正在运行（`python backend/main.py`）
- [ ] 数据库已配置并运行
- [ ] Python已安装（运行 `python --version` 检查）

### 常见问题

**Q: 我不知道我在哪个文件夹？**  
A: 在命令行输入 `cd` 然后按回车，会显示当前路径。或者输入 `dir`（Windows）或 `ls`（PowerShell）查看当前文件夹内容。

**Q: 如何停止服务器？**  
A: 在运行服务器的命令行窗口中按 `Ctrl + C`

**Q: 测试需要多长时间？**  
A: 通常1-2分钟，取决于网络速度和服务器响应时间。

**Q: 可以多次运行测试吗？**  
A: 可以！测试是安全的，不会破坏数据。

---

## 📝 总结 (Summary)

1. **打开两个命令行窗口**
   - 一个运行服务器
   - 一个运行测试

2. **运行测试命令**
   ```bash
   python backend/attack/run_sql_security_tests.py
   ```

3. **查看结果**
   - ✅ PROTECTED = 安全
   - ❌ VULNERABLE = 需要修复

4. **如果需要，创建测试用户**
   ```bash
   python backend/setup_test_user.py
   ```

就是这么简单！🎉

---

**最后更新:** 2024  
**Last Updated:** 2024

