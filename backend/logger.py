#!/usr/bin/env python3
from db_connector import get_db_connection

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
    finally:
        conn.close()

