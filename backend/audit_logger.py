#!/usr/bin/env python3
"""
Audit logging module for comprehensive database access monitoring
审计日志模块，用于全面的数据库访问监控
"""
from typing import Optional, Dict
from datetime import datetime
from logger_config import app_logger, log_security_event
from db_query import db_execute

# Audit log table name - 审计日志表名
AUDIT_LOG_TABLE = 'audit_log'

def log_audit_event(event_type: str, details: Dict, user_id: Optional[str] = None,
                   user_role: Optional[str] = None, ip_address: Optional[str] = None,
                   sql: Optional[str] = None):
    """
    Log audit event to database
    将审计事件记录到数据库
    
    Args:
        event_type: Type of event (login, query, update, delete, etc.)
        details: Event details dictionary
        user_id: User ID
        user_role: User role
        ip_address: IP address
        sql: SQL statement if applicable
    """
    try:
        # Insert into audit log table - 插入到审计日志表
        db_execute(
            f"""
            INSERT INTO {AUDIT_LOG_TABLE} 
            (event_type, user_id, user_role, ip_address, sql_statement, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                event_type,
                user_id,
                user_role,
                ip_address,
                sql[:1000] if sql else None,  # Limit SQL length - 限制SQL长度
                str(details)[:500] if details else None,  # Limit details length - 限制详情长度
            )
        )
        
        # Also log to file - 同时记录到文件
        app_logger.info(f"AUDIT: {event_type} - user={user_id}, role={user_role}, ip={ip_address}")
        
    except Exception as e:
        # Fallback to file logging if database fails - 如果数据库失败则回退到文件日志
        app_logger.error(f"Failed to log audit event to database: {e}")
        log_security_event(event_type, details, user_id, ip_address)

def log_database_connection(user_id: Optional[str] = None, user_role: Optional[str] = None,
                          ip_address: Optional[str] = None, success: bool = True):
    """
    Log database connection attempts
    记录数据库连接尝试
    
    Args:
        user_id: User ID
        user_role: User role
        ip_address: IP address
        success: Whether connection was successful
    """
    event_type = 'db_connection_success' if success else 'db_connection_failure'
    details = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    log_audit_event(event_type, details, user_id, user_role, ip_address)

def log_sql_execution(operation: str, table: str, user_id: Optional[str] = None,
                     user_role: Optional[str] = None, sql: Optional[str] = None,
                     ip_address: Optional[str] = None, success: bool = True):
    """
    Log SQL execution
    记录SQL执行
    
    Args:
        operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        user_id: User ID
        user_role: User role
        sql: SQL statement
        ip_address: IP address
        success: Whether execution was successful
    """
    event_type = f'sql_{operation.lower()}' + ('_success' if success else '_failure')
    details = {
        'operation': operation,
        'table': table,
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    log_audit_event(event_type, details, user_id, user_role, ip_address, sql)

def log_unauthorized_access(attempted_action: str, user_id: Optional[str] = None,
                           user_role: Optional[str] = None, ip_address: Optional[str] = None,
                           resource: Optional[str] = None):
    """
    Log unauthorized access attempts
    记录未授权访问尝试
    
    Args:
        attempted_action: Action that was attempted
        user_id: User ID
        user_role: User role
        ip_address: IP address
        resource: Resource that was accessed
    """
    details = {
        'attempted_action': attempted_action,
        'resource': resource,
        'timestamp': datetime.now().isoformat()
    }
    
    log_audit_event('unauthorized_access', details, user_id, user_role, ip_address)
    log_security_event('unauthorized_access', details, user_id, ip_address)

