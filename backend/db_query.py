#!/usr/bin/env python3
from db_connector import get_db_connection

def db_query(sql, params=None):
    """Execute query SQL and return results"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()

def db_execute(sql, params=None):
    """Execute update SQL and return affected row count"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount
    finally:
        conn.close()

def getTableColumns(table_name):
    """Return all column information for the specified table"""
    rows = db_query(f"SHOW COLUMNS FROM `{table_name}`")
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
