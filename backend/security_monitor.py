#!/usr/bin/env python3
"""
Security monitoring module for detecting SQL injection attempts and policy violations
"""
import re
from typing import Dict, Optional, List
from logger_config import log_security_event, app_logger

# SQL injection patterns
SQL_INJECTION_PATTERNS = [
    # Common SQL injection patterns
    r"('|(\\')|(;)|(--)|(/\*)|(\*/))",  # SQL comments and quotes
    r"(xp_|exec|execute|sp_)",  # Stored procedure calls
    r"(union|select|insert|update|delete|drop|alter|create|truncate)",  # SQL keywords
    r"(\bor\b.*=.*)|(\band\b.*=.*)",  # OR/AND injection
    r"(;.*drop)|(;.*delete)|(;.*truncate)",  # Command chaining
    r"(union.*select)|(select.*union)",  # Union injection
    r"(\bor\b\s+1\s*=\s*1)|(\band\b\s+1\s*=\s*1)",  # Boolean injection
    r"(sleep|benchmark|waitfor)",  # Time-based injection
]

# Policy violation patterns
POLICY_VIOLATION_PATTERNS = [
    r"(access.*denied|unauthorized|forbidden)",  # Access violations
    r"(privilege.*escalation|permission.*bypass)",  # Privilege escalation
]

def detect_sql_injection(input_str: str) -> bool:
    """
    Detect SQL injection attempts in input string
    
    Args:
        input_str: Input string to check
        
    Returns:
        True if SQL injection detected, False otherwise
    """
    if not input_str or not isinstance(input_str, str):
        return False
    
    input_lower = input_str.lower()
    
    # Check against SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, input_lower, re.IGNORECASE):
            return True
    
    return False

def detect_policy_violation(action: str, user_role: str, resource: str) -> bool:
    """
    Detect policy violations based on role and resource
    
    Args:
        action: Action attempted (read, write, delete)
        user_role: User role
        resource: Resource being accessed
        
    Returns:
        True if policy violation detected, False otherwise
    """
    # Define allowed actions per role
    role_permissions = {
        'student': {
            'read': ['students', 'grades', 'disciplinary_records'],
            'write': ['students'],  # Only own data
            'delete': []
        },
        'guardian': {
            'read': ['guardians', 'grades', 'disciplinary_records'],
            'write': ['guardians'],  # Only own data
            'delete': []
        },
        'aro': {
            'read': ['grades'],
            'write': ['grades'],
            'delete': ['grades']
        },
        'dro': {
            'read': ['disciplinary_records'],
            'write': ['disciplinary_records'],
            'delete': ['disciplinary_records']
        },
        'root': {
            'read': ['*'],  # All tables
            'write': ['*'],
            'delete': ['*']
        }
    }
    
    permissions = role_permissions.get(user_role.lower(), {})
    allowed_resources = permissions.get(action, [])
    
    # Check if resource is allowed
    if '*' in allowed_resources:
        return False  # Root has access to all
    
    if resource.lower() not in [r.lower() for r in allowed_resources]:
        return True  # Policy violation
    
    return False

def log_sql_injection_attempt(input_str: str, user_id: Optional[str] = None, 
                             ip_address: Optional[str] = None, sql: Optional[str] = None):
    """
    Log SQL injection attempt
    
    Args:
        input_str: Suspicious input string
        user_id: User ID if available
        ip_address: IP address if available
        sql: SQL statement if available
    """
    details = {
        'input': input_str[:200],  # Limit length
        'sql': sql[:200] if sql else None,
        'detected_patterns': []
    }
    
    # Identify which patterns matched
    input_lower = input_str.lower()
    for i, pattern in enumerate(SQL_INJECTION_PATTERNS):
        if re.search(pattern, input_lower, re.IGNORECASE):
            details['detected_patterns'].append(f"pattern_{i}")
    
    log_security_event('sql_injection_attempt', details, user_id, ip_address)
    app_logger.warning(f"SQL injection attempt detected: user={user_id}, input={input_str[:100]}")

def log_policy_violation(action: str, user_role: str, resource: str, 
                        user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Log policy violation
    
    Args:
        action: Action attempted
        user_role: User role
        resource: Resource being accessed
        user_id: User ID if available
        ip_address: IP address if available
    """
    details = {
        'action': action,
        'user_role': user_role,
        'resource': resource,
        'violation_type': 'unauthorized_access'
    }
    
    log_security_event('policy_violation', details, user_id, ip_address)
    app_logger.warning(f"Policy violation detected: user={user_id}, role={user_role}, action={action}, resource={resource}")

def validate_input_for_sql_injection(input_data: Dict, user_id: Optional[str] = None, 
                                    ip_address: Optional[str] = None) -> tuple[bool, List[str]]:
    """
    Validate all input data for SQL injection attempts
    
    Args:
        input_data: Dictionary of input data
        user_id: User ID if available
        ip_address: IP address if available
        
    Returns:
        Tuple (is_safe, detected_patterns)
    """
    detected_patterns = []
    
    for key, value in input_data.items():
        if isinstance(value, str):
            if detect_sql_injection(value):
                detected_patterns.append(f"{key}: {value[:100]}")
                log_sql_injection_attempt(value, user_id, ip_address)
        elif isinstance(value, dict):
            # Recursively check nested dictionaries
            is_safe, nested_patterns = validate_input_for_sql_injection(value, user_id, ip_address)
            if not is_safe:
                detected_patterns.extend(nested_patterns)
        elif isinstance(value, list):
            # Check list items
            for item in value:
                if isinstance(item, str) and detect_sql_injection(item):
                    detected_patterns.append(f"{key}[list]: {item[:100]}")
                    log_sql_injection_attempt(item, user_id, ip_address)
    
    return len(detected_patterns) == 0, detected_patterns

