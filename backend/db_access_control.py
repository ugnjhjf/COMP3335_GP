#!/usr/bin/env python3
"""
Database access control module to prevent direct database access
"""
import os
from typing import Optional, Dict
from logger_config import app_logger, log_security_event
from auth import validate_session

# Database user configuration
# Application should use limited-privilege database users
DB_APP_USER = os.getenv('DB_APP_USER', 'app_user')
DB_APP_PASSWORD = os.getenv('DB_APP_PASSWORD', '')

# Track all database access
_access_log = []

def require_authentication(func):
    """
    Decorator to require authentication for database operations
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        # Check if authentication token is provided
        # This should be passed from the request handler
        token = kwargs.get('token') or (args[0] if args else None)
        
        if not token:
            log_security_event('unauthorized_db_access', {
                'function': func.__name__,
                'error': 'No authentication token provided'
            })
            raise PermissionError("Authentication required for database access")
        
        # Validate session
        session = validate_session(token)
        if not session:
            log_security_event('unauthorized_db_access', {
                'function': func.__name__,
                'error': 'Invalid or expired session'
            })
            raise PermissionError("Invalid or expired session")
        
        # Add user info to kwargs
        kwargs['user_id'] = session.get('user_id')
        kwargs['user_role'] = session.get('role')
        
        return func(*args, **kwargs)
    
    return wrapper

def log_database_access(operation: str, table: str, user_id: Optional[str] = None,
                        user_role: Optional[str] = None, sql: Optional[str] = None,
                        ip_address: Optional[str] = None):
    """
    Log all database access for audit trail
    
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
        'sql': sql[:500] if sql else None,  # Limit SQL length
        'ip_address': ip_address,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    _access_log.append(access_record)
    
    # Log to file
    app_logger.info(f"DB_ACCESS: {access_record}")
    
    # Also log to security log
    log_security_event('database_access', access_record, user_id, ip_address)

def check_database_user_permissions():
    """
    Check if database user has appropriate permissions
    
    Returns:
        True if permissions are correct, False otherwise
    """
    try:
        from db_query import db_query
        
        # Check current database user
        result = db_query("SELECT USER() as current_user, DATABASE() as current_db")
        if result:
            current_user = result[0].get('current_user', '')
            current_db = result[0].get('current_db', '')
            
            app_logger.info(f"Database user: {current_user}, Database: {current_db}")
            
            # Check if user is application user
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
    
    Args:
        user_id: User ID
        operation: Operation type
        table: Table name
        ip_address: IP address
        
    Returns:
        True if access is anomalous, False otherwise
    """
    # Check for rapid successive access
    recent_access = [a for a in _access_log[-100:] if a.get('user_id') == user_id]
    
    if len(recent_access) > 50:  # More than 50 accesses in recent history
        log_security_event('anomalous_access', {
            'user_id': user_id,
            'operation': operation,
            'table': table,
            'reason': 'too_many_requests',
            'count': len(recent_access)
        }, user_id, ip_address)
        return True
    
    # Check for access to multiple tables rapidly
    unique_tables = set(a.get('table') for a in recent_access[-20:])
    if len(unique_tables) > 10:  # Accessing more than 10 different tables
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
    
    Args:
        limit: Number of records to return
        
    Returns:
        List of access records
    """
    return _access_log[-limit:]

