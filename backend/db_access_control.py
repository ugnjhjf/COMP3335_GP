#!/usr/bin/env python3
"""
Database access control module to prevent direct database access
数据库访问控制模块，防止直接数据库访问
"""
import os
from typing import Optional, Dict
from logger_config import app_logger, log_security_event
from auth import validate_session

# Database user configuration - 数据库用户配置
# Application should use limited-privilege database users
# 应用程序应使用有限权限的数据库用户
DB_APP_USER = os.getenv('DB_APP_USER', 'app_user')
DB_APP_PASSWORD = os.getenv('DB_APP_PASSWORD', '')

# Track all database access - 跟踪所有数据库访问
_access_log = []

def require_authentication(func):
    """
    Decorator to require authentication for database operations
    装饰器：要求数据库操作必须认证
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        # Check if authentication token is provided - 检查是否提供认证令牌
        # This should be passed from the request handler
        # 这应该从请求处理器传递
        token = kwargs.get('token') or (args[0] if args else None)
        
        if not token:
            log_security_event('unauthorized_db_access', {
                'function': func.__name__,
                'error': 'No authentication token provided'
            })
            raise PermissionError("Authentication required for database access")
        
        # Validate session - 验证会话
        session = validate_session(token)
        if not session:
            log_security_event('unauthorized_db_access', {
                'function': func.__name__,
                'error': 'Invalid or expired session'
            })
            raise PermissionError("Invalid or expired session")
        
        # Add user info to kwargs - 添加用户信息到kwargs
        kwargs['user_id'] = session.get('user_id')
        kwargs['user_role'] = session.get('role')
        
        return func(*args, **kwargs)
    
    return wrapper

def log_database_access(operation: str, table: str, user_id: Optional[str] = None,
                        user_role: Optional[str] = None, sql: Optional[str] = None,
                        ip_address: Optional[str] = None):
    """
    Log all database access for audit trail
    记录所有数据库访问以进行审计追踪
    
    Args:
        operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        user_id: User ID
        user_role: User role
        sql: SQL statement
        ip_address: IP address
    """
    access_record = {
        'operation': operation,
        'table': table,
        'user_id': user_id,
        'user_role': user_role,
        'sql': sql[:500] if sql else None,  # Limit SQL length - 限制SQL长度
        'ip_address': ip_address,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    _access_log.append(access_record)
    
    # Log to file - 记录到文件
    app_logger.info(f"DB_ACCESS: {access_record}")
    
    # Also log to security log - 同时记录到安全日志
    log_security_event('database_access', access_record, user_id, ip_address)

def check_database_user_permissions():
    """
    Check if database user has appropriate permissions
    检查数据库用户是否具有适当的权限
    
    Returns:
        True if permissions are correct, False otherwise
    """
    try:
        from db_query import db_query
        
        # Check current database user - 检查当前数据库用户
        result = db_query("SELECT USER() as current_user, DATABASE() as current_db")
        if result:
            current_user = result[0].get('current_user', '')
            current_db = result[0].get('current_db', '')
            
            app_logger.info(f"Database user: {current_user}, Database: {current_db}")
            
            # Check if user is application user - 检查用户是否为应用用户
            if DB_APP_USER and DB_APP_USER not in current_user:
                app_logger.warning(f"Database user {current_user} is not the expected application user {DB_APP_USER}")
                return False
            
            return True
    except Exception as e:
        app_logger.error(f"Error checking database user permissions: {e}")
        return False
    
    return False

def detect_anomalous_access(user_id: str, operation: str, table: str, 
                           ip_address: Optional[str] = None) -> bool:
    """
    Detect anomalous database access patterns
    检测异常的数据库访问模式
    
    Args:
        user_id: User ID
        operation: Operation type
        table: Table name
        ip_address: IP address
        
    Returns:
        True if access is anomalous, False otherwise
    """
    # Check for rapid successive access - 检查快速连续访问
    recent_access = [a for a in _access_log[-100:] if a.get('user_id') == user_id]
    
    if len(recent_access) > 50:  # More than 50 accesses in recent history - 最近历史中超过50次访问
        log_security_event('anomalous_access', {
            'user_id': user_id,
            'operation': operation,
            'table': table,
            'reason': 'too_many_requests',
            'count': len(recent_access)
        }, user_id, ip_address)
        return True
    
    # Check for access to multiple tables rapidly - 检查快速访问多个表
    unique_tables = set(a.get('table') for a in recent_access[-20:])
    if len(unique_tables) > 10:  # Accessing more than 10 different tables - 访问超过10个不同的表
        log_security_event('anomalous_access', {
            'user_id': user_id,
            'operation': operation,
            'table': table,
            'reason': 'too_many_tables',
            'unique_tables': len(unique_tables)
        }, user_id, ip_address)
        return True
    
    return False

def get_access_log(limit: int = 100) -> list:
    """
    Get recent database access log
    获取最近的数据库访问日志
    
    Args:
        limit: Number of records to return
        
    Returns:
        List of access records
    """
    return _access_log[-limit:]

