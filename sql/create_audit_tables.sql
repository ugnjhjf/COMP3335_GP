-- Create audit log table for comprehensive database access monitoring
-- 创建审计日志表用于全面的数据库访问监控
-- Required for Section 5.5: Access monitoring
-- 第5.5节要求：访问监控

CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(50),
    user_role VARCHAR(50),
    ip_address VARCHAR(45),  -- IPv6 support - 支持IPv6
    sql_statement TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_user_role (user_role),
    INDEX idx_timestamp (timestamp),
    INDEX idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create security events table for SQL injection attempts and policy violations
-- 创建安全事件表用于SQL注入尝试和策略违反
-- Required for Section 5.5.a: Inappropriate access, SQL injection attempts, policy violations
-- 第5.5.a节要求：不当访问、SQL注入尝试、策略违反

CREATE TABLE IF NOT EXISTS security_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,  -- sql_injection_attempt, policy_violation, unauthorized_access
    user_id VARCHAR(50),
    user_role VARCHAR(50),
    ip_address VARCHAR(45),
    details TEXT,
    severity VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_severity (severity),
    INDEX idx_timestamp (timestamp),
    INDEX idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create access violations table for policy violations
-- 创建访问违反表用于策略违反
-- Required for Section 5.5.a: Policy violations
-- 第5.5.a节要求：策略违反

CREATE TABLE IF NOT EXISTS access_violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    user_role VARCHAR(50),
    ip_address VARCHAR(45),
    attempted_action VARCHAR(50),  -- read, write, delete
    resource VARCHAR(100),  -- table name or resource
    violation_type VARCHAR(100),  -- unauthorized_access, privilege_escalation, data_range_violation
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_violation_type (violation_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

