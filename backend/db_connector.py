#!/usr/bin/env python3
import pymysql
import os
from logger_config import app_logger

# =========================
# Database configuration
# =========================
# Use environment variables for sensitive data
# Fallback to default values for backward compatibility
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'ComputingU'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

# Role-based DBMS user mapping
# Passwords are hardcoded for development/test (as per plan option b)
DBMS_USERS = {
    'auth': {'user': 'auth_user', 'password': 'auth_user_password'},  # For login authentication only
    'student': {'user': 'student', 'password': 'student_password'},
    'guardian': {'user': 'guardian', 'password': 'guardian_password'},
    'aro': {'user': 'aro', 'password': 'aro_password'},
    'dro': {'user': 'dro', 'password': 'dro_password'}
}

def _create_connection(role=None):
    """
    Create a new database connection using role-specific DBMS user
    
    Args:
        role: User role (auth, student, guardian, aro, dro). If None, defaults to 'student'
    
    Returns:
        Database connection object
    """
    # Default to 'student' if role is not provided or invalid
    if role not in DBMS_USERS:
        role = 'student'
        app_logger.warning(f"Invalid role provided, defaulting to 'student'")
    
    dbms_user = DBMS_USERS[role]
    
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=dbms_user['user'],
        password=dbms_user['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def get_db_connection(role=None):
    """
    Get database connection using role-specific DBMS user
    
    Args:
        role: User role (auth, student, guardian, aro, dro). If None, defaults to 'student'
    
    Returns:
        Database connection object
    """
    try:
        conn = _create_connection(role)
        return conn
    except Exception as e:
        app_logger.error(f"Error creating database connection for role {role}: {e}")
        raise

def test_db_connection(role='student'):
    """
    Test if database connection is successful
    
    Args:
        role: User role to test connection with (defaults to 'student'). Can be 'auth', 'student', 'guardian', 'aro', or 'dro'
    """
    try:
        conn = get_db_connection(role)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        return True, f"Database connection successful for role '{role}'"
    except Exception as e:
        return False, f"Database connection failed for role '{role}': {str(e)}"
