-- Setup database permissions to prevent direct database access
-- 设置数据库权限以防止直接数据库访问
-- Required for preventing attackers from skipping login and accessing database directly
-- 防止攻击者跳过登录直接访问数据库

-- Create application user with limited privileges
-- 创建具有有限权限的应用用户
-- This user can only access database through the application
-- 此用户只能通过应用程序访问数据库

-- Read-only user for queries - 用于查询的只读用户
CREATE USER IF NOT EXISTS 'app_readonly'@'localhost' IDENTIFIED BY 'app_readonly_password_change_me';
GRANT SELECT ON ComputingU.* TO 'app_readonly'@'localhost';

-- Read-write user for application operations - 用于应用操作的读写用户
CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'app_user_password_change_me';
GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.* TO 'app_user'@'localhost';

-- Revoke dangerous privileges - 撤销危险权限
REVOKE CREATE, DROP, ALTER, INDEX, TRIGGER, CREATE VIEW, SHOW VIEW, 
       CREATE ROUTINE, ALTER ROUTINE, EXECUTE, CREATE TEMPORARY TABLES,
       LOCK TABLES, REFERENCES, RELOAD, SHUTDOWN, PROCESS, FILE, 
       SUPER, REPLICATION CLIENT, REPLICATION SLAVE, CREATE USER,
       EVENT, TRIGGER ON *.* FROM 'app_user'@'localhost';

-- Revoke dangerous privileges from readonly user - 从只读用户撤销危险权限
REVOKE CREATE, DROP, ALTER, INDEX, TRIGGER, CREATE VIEW, SHOW VIEW,
       CREATE ROUTINE, ALTER ROUTINE, EXECUTE, CREATE TEMPORARY TABLES,
       LOCK TABLES, REFERENCES, RELOAD, SHUTDOWN, PROCESS, FILE,
       SUPER, REPLICATION CLIENT, REPLICATION SLAVE, CREATE USER,
       EVENT, TRIGGER, INSERT, UPDATE, DELETE ON *.* FROM 'app_readonly'@'localhost';

-- Grant access to audit tables - 授予审计表访问权限
GRANT SELECT, INSERT ON ComputingU.audit_log TO 'app_user'@'localhost';
GRANT SELECT, INSERT ON ComputingU.security_events TO 'app_user'@'localhost';
GRANT SELECT, INSERT ON ComputingU.access_violations TO 'app_user'@'localhost';

-- Grant access to sessions table if using database sessions - 如果使用数据库会话则授予会话表访问权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ComputingU.sessions TO 'app_user'@'localhost';

-- Grant access to dataUpdateLog table - 授予dataUpdateLog表访问权限
GRANT SELECT, INSERT ON ComputingU.dataUpdateLog TO 'app_user'@'localhost';

-- Flush privileges - 刷新权限
FLUSH PRIVILEGES;

-- Note: Change passwords in production environment
-- 注意：在生产环境中更改密码
-- Use environment variables to store passwords securely
-- 使用环境变量安全存储密码

