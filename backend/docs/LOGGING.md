3. 登录操作日志记录 (backend/auth.py 和 backend/api_handler.py)
记录的事件：
发送登录请求：发送登录请求: email={email}
登录成功：登录成功: email={email}, user_type={type}
登录失败：登录失败: email={email}, 原因=账号或密码错误
登录拒绝：
登录拒绝: 原因=邮箱缺失
登录拒绝: email={email}, 原因=密码缺失
登录拒绝: email={email}, 原因=邮箱格式无效
登录拒绝: email={email}, 原因=密码格式无效
登录拒绝: email={email}, 原因=输入清理失败
登录错误：登录错误: email={email}, 错误={error}
SQL注入尝试：SQL注入尝试: email={email}, 位置=登录
会话创建：会话创建成功: user_id={id}, role={role}
4. 数据库访问监控日志 (backend/api_handler.py)
记录的事件：
查询请求：数据库查询请求: table={table}
查询成功：数据库查询成功: table={table}, 返回行数={count}
未授权访问：未授权访问: 操作=查询, 原因=Token错误或缺失
策略违反：策略违反: 操作=查询, 表名={table}, 原因=无效表名
不当访问：不当访问: 操作=查询, 表名={table}, 原因=访问被拒绝
5. 数据修改日志 (backend/api_handler.py)
记录的事件：
UPDATE 操作：
数据更新请求: table={table}
数据更新成功: table={table}, 受影响行数={count}
数据更新失败: table={table}, 错误={error}
DELETE 操作：
数据删除请求: table={table}
数据删除成功: table={table}, 受影响行数={count}
数据删除失败: table={table}, 错误={error}
INSERT 操作：
数据插入请求: table={table}
数据插入成功: table={table}, 受影响行数={count}
数据插入失败: table={table}, 错误={error}
6. 安全事件日志
记录的事件：
SQL注入尝试：SQL注入尝试: email={email}, 位置=登录
策略违反：策略违反: 操作={action}, 表名={table}, 原因={reason}
不当访问：不当访问: 操作={action}, 表名={table}, 原因=访问被拒绝
未授权访问：未授权访问: 操作={action}, 原因=Token错误或缺失
日志内容示例
accountLog 表中的 logContent 字段会包含如下内容：
发送登录请求: email=alice.student@university.edu
登录成功: email=alice.student@university.edu, user_type=student
登录失败: email=test@example.com, 原因=账号或密码错误
登录拒绝: email=test@example.com, 原因=邮箱格式无效
未授权访问: 操作=查询, 原因=Token错误或缺失
SQL注入尝试: email=admin' OR '1'='1, 位置=登录
策略违反: 操作=查询, 表名=students, 原因=无效表名
不当访问: 操作=查询, 表名=grades, 原因=访问被拒绝
数据库查询成功: table=students, 返回行数=10
数据更新成功: table=students, 受影响行数=1
数据删除成功: table=grades, 受影响行数=1
数据插入成功: table=students, 受影响行数=1
数据修改记录
数据修改操作同时记录在：
accountLog 表：记录操作请求和结果（中文描述）
dataUpdateLog 表：记录 SQL 语句（保持不变）
所有用户操作现在都会被记录到 accountLog 表中，满足监控和审计要求。