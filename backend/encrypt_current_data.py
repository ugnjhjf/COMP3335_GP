from typing import Tuple

from db_connector import get_db_connection
from encryption import (
    ENCRYPTED_COLUMNS,
    getEncryptionKey,
    getColumnTypeDefinition,
    isNullableColumn,
)


def alterColumnType(conn, table: str, column: str) -> None:
    column_type = getColumnTypeDefinition(table, column)
    nullable = isNullableColumn(table, column)
    null_clause = "NULL" if nullable else "NOT NULL"
    sql = f"ALTER TABLE `{table}` MODIFY `{column}` {column_type} {null_clause}"
    with conn.cursor() as cur:
        try:
            cur.execute(sql)
            print(f"✓ {table}.{column} set to {column_type} {null_clause}")
        except Exception as exc:
            print(f"! Skipped altering {table}.{column}: {exc}")


def encryptColumn(conn, table: str, column: str, key: str) -> None:
    sql = f"""
        UPDATE `{table}`
           SET `{column}` = AES_ENCRYPT(CONVERT(`{column}` USING utf8mb4), %s)
         WHERE `{column}` IS NOT NULL
           AND `{column}` <> ''
           AND AES_DECRYPT(`{column}`, %s) IS NULL
    """
    with conn.cursor() as cur:
        cur.execute(sql, (key, key))
        print(f"✓ Encrypted {cur.rowcount} row(s) in {table}.{column}")


def processTable(conn, table: str, columns: Tuple[str, ...], key: str) -> None:
    for column in columns:
        alterColumnType(conn, table, column)
        encryptColumn(conn, table, column, key)


def main() -> None:
    key = getEncryptionKey()
    conn = get_db_connection()
    try:
        for table, columns_meta in ENCRYPTED_COLUMNS.items():
            processTable(conn, table, tuple(columns_meta.keys()), key)
    finally:
        conn.close()


if __name__ == "__main__":
    main()