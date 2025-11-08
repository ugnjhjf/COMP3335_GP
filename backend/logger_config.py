#!/usr/bin/env python3
"""
Structured logging configuration module
结构化日志配置模块
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Configure logging - 配置日志
LOG_DIR = os.getenv('LOG_DIR', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Create log directory if it doesn't exist - 如果日志目录不存在则创建
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name='app', log_file=LOG_FILE, level=LOG_LEVEL):
    """
    Setup structured logger with file rotation
    设置带文件轮转的结构化日志记录器
    
    Args:
        name: Logger name
        log_file: Log file path
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Prevent duplicate handlers - 防止重复处理器
    if logger.handlers:
        return logger
    
    # File handler with rotation - 带轮转的文件处理器
    # Max 10MB per file, keep 5 backup files - 每个文件最大10MB，保留5个备份文件
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level, logging.INFO))
    
    # Console handler for development - 开发环境的控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console - 只输出警告和错误到控制台
    
    # Formatter with timestamp and details - 带时间戳和详细信息的格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger - 创建默认日志记录器
app_logger = setup_logger('app')

def log_security_event(event_type, details, user_id=None, ip_address=None):
    """
    Log security-related events
    记录安全相关事件
    
    Args:
        event_type: Type of security event (e.g., 'login_attempt', 'sql_injection_attempt')
        details: Event details dictionary
        user_id: User ID if applicable
        ip_address: IP address if available
    """
    security_logger = setup_logger('security', os.path.join(LOG_DIR, 'security.log'))
    log_data = {
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'ip_address': ip_address,
        'details': details
    }
    security_logger.warning(f"SECURITY_EVENT: {log_data}")

def log_database_operation(operation, table, user_id, role, sql=None):
    """
    Log database operations for audit trail
    记录数据库操作以进行审计追踪
    
    Args:
        operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        user_id: User ID
        role: User role
        sql: SQL statement (optional)
    """
    db_logger = setup_logger('database', os.path.join(LOG_DIR, 'database.log'))
    log_data = {
        'operation': operation,
        'table': table,
        'user_id': user_id,
        'role': role,
        'timestamp': datetime.now().isoformat(),
        'sql': sql
    }
    db_logger.info(f"DB_OPERATION: {log_data}")

