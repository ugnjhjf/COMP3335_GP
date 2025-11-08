#!/usr/bin/env python3
from db_connector import get_db_connection, return_db_connection

def logDataUpdate(user_id, role, sql_text):
    """Log data update operations to log table"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dataUpdateLog (user_id, user_role, sql_text)
                VALUES (%s, %s, %s)
                """,
                (user_id, role, sql_text)
            )
            conn.commit()
    finally:
        return_db_connection(conn)

def logAccountOperation(ip, user_id, user_role, log_content):
    """
    Log account operations to accountLog table
    
    Args:
        ip: IP address
        user_id: User ID (can be None)
        user_role: User role (can be None)
        log_content: Log content description
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO accountLog (ip, user_id, user_role, logContent)
                VALUES (%s, %s, %s, %s)
                """,
                (ip, user_id, user_role, log_content)
            )
            conn.commit()
    except Exception as e:
        # Log error but don't fail the operation
        import logging
        logging.error(f"Failed to log account operation: {e}")
    finally:
        return_db_connection(conn)

