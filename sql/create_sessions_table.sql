-- Create sessions table for session persistence
-- 创建sessions表用于会话持久化
-- This table is required when USE_DB_SESSIONS=true
-- 当USE_DB_SESSIONS=true时需要此表

CREATE TABLE IF NOT EXISTS sessions (
    token VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expires_at (expires_at),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

