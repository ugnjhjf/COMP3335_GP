#!/usr/bin/env python3
import pymysql
import os
import threading
from queue import Queue, Empty
from logger_config import app_logger

# =========================
# Database configuration - 数据库配置
# =========================
# Use environment variables for sensitive data - 使用环境变量存储敏感数据
# Fallback to default values for backward compatibility - 回退到默认值以保持向后兼容
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'supersecurepassword'),  # Should be set via environment variable - 应通过环境变量设置
    'database': os.getenv('DB_NAME', 'ComputingU'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

# Connection pool configuration - 连接池配置
POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '5'))  # seconds

# Connection pool - 连接池
_connection_pool = None
_pool_lock = threading.Lock()

def _create_connection():
    """
    Create a new database connection
    创建新的数据库连接
    """
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def _init_connection_pool():
    """
    Initialize connection pool
    初始化连接池
    """
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = Queue(maxsize=POOL_SIZE)
                # Pre-populate pool with connections - 预填充连接池
                for _ in range(POOL_SIZE):
                    try:
                        conn = _create_connection()
                        _connection_pool.put(conn)
                    except Exception as e:
                        app_logger.error(f"Failed to create connection for pool: {e}")
                app_logger.info(f"Connection pool initialized with {_connection_pool.qsize()} connections")

def get_db_connection():
    """
    Get database connection from pool
    从连接池获取数据库连接
    
    Returns:
        Database connection object
    """
    # Initialize pool if needed - 如果需要则初始化连接池
    _init_connection_pool()
    
    try:
        # Get connection from pool with timeout - 从连接池获取连接（带超时）
        conn = _connection_pool.get(timeout=POOL_TIMEOUT)
        
        # Check if connection is still alive - 检查连接是否仍然有效
        try:
            conn.ping(reconnect=True)
        except Exception:
            # Connection is dead, create a new one - 连接已失效，创建新连接
            conn = _create_connection()
        
        return conn
    except Empty:
        # Pool exhausted, create new connection - 连接池耗尽，创建新连接
        app_logger.warning("Connection pool exhausted, creating new connection")
        return _create_connection()
    except Exception as e:
        app_logger.error(f"Error getting connection from pool: {e}")
        return _create_connection()

def return_db_connection(conn):
    """
    Return database connection to pool
    将数据库连接返回到连接池
    
    Args:
        conn: Database connection to return
    """
    if _connection_pool is None:
        # Pool not initialized, just close connection - 连接池未初始化，直接关闭连接
        try:
            conn.close()
        except Exception:
            pass
        return
    
    try:
        # Check if connection is still alive - 检查连接是否仍然有效
        conn.ping(reconnect=False)
        # Return to pool - 返回到连接池
        _connection_pool.put_nowait(conn)
    except Exception:
        # Connection is dead, close it - 连接已失效，关闭它
        try:
            conn.close()
        except Exception:
            pass

def test_db_connection():
    """Test if database connection is successful"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"
