#!/usr/bin/env python3
from db_connector import get_db_connection
from logger_config import app_logger, log_database_operation

def db_query(sql, params=None, role=None):
    """
    Execute query SQL and return results
    执行查询SQL并返回结果
    
    Args:
        sql: SQL query string
        params: Query parameters (optional)
        role: User role for DBMS user selection (student, guardian, aro, dro)
    """
    conn = get_db_connection(role)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            result = cur.fetchall()
            # Log database operation - 记录数据库操作
            log_database_operation('SELECT', 'unknown', 'system', role or 'system', sql)
            return result
    except Exception as e:
        app_logger.error(f"Database query error: {e}, SQL: {sql[:100]}")
        raise
    finally:
        conn.close()

def db_execute(sql, params=None, role=None):
    """
    Execute update SQL and return affected row count
    执行更新SQL并返回受影响的行数
    
    Args:
        sql: SQL statement string
        params: Statement parameters (optional)
        role: User role for DBMS user selection (student, guardian, aro, dro)
    """
    conn = get_db_connection(role)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            result = cur.rowcount
            # Log database operation - 记录数据库操作
            log_database_operation('EXECUTE', 'unknown', 'system', role or 'system', sql)
            return result
    except Exception as e:
        app_logger.error(f"Database execute error: {e}, SQL: {sql[:100]}")
        raise
    finally:
        conn.close()

def getTableColumns(table_name, role=None):
    """
    Return all column information for the specified table
    
    Args:
        table_name: Name of the table
        role: User role for DBMS user selection (student, guardian, aro, dro)
    """
    # Use parameterized query to prevent SQL injection - 使用参数化查询防止SQL注入
    # Note: SHOW COLUMNS doesn't support parameters, so we validate table_name first
    # 注意：SHOW COLUMNS不支持参数，所以先验证表名
    from security import validate_table_name
    if not validate_table_name(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    # Escape table name to prevent injection - 转义表名防止注入
    # Since table_name is validated, this is safe - 由于表名已验证，这是安全的
    rows = db_query(f"SHOW COLUMNS FROM `{table_name}`", role=role)
    return rows

def checkPrimaryKey(columnData, keyPair):
    """Check if primary key is complete"""
    if not keyPair or not columnData:
        return False
    for col in columnData:
        if col.get("Key") == "PRI":
            keyName = col.get("Field")
            if keyName not in keyPair.keys():
                return False
    return True

def checkUpdatableColumns(updatableColumnList, updateValues):
    """Check if updated columns are in the allowed list"""
    if not updateValues or not updatableColumnList:
        return False
    for colName in list(updateValues.keys()):
        if colName not in updatableColumnList:
            return False
    return True
