import os
from functools import lru_cache
from typing import Any, Dict
from pathlib import Path
from dotenv import load_dotenv
import os

ENCRYPTED_COLUMNS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "students": {
        "Id_No": {"cast": "CHAR(32)", "type": "VARBINARY(255)", "nullable": False},
        "address": {"cast": "TEXT", "type": "BLOB", "nullable": True},
        "phone": {"cast": "CHAR(32)", "type": "VARBINARY(64)", "nullable": False},
    },
    "guardians": {
        "phone": {"cast": "CHAR(32)", "type": "VARBINARY(64)", "nullable": False},
    },
    "staffs": {
        "Id_No": {"cast": "CHAR(32)", "type": "VARBINARY(255)", "nullable": False},
        "address": {"cast": "TEXT", "type": "BLOB", "nullable": True},
        "phone": {"cast": "CHAR(32)", "type": "VARBINARY(64)", "nullable": False},
    },
}


@lru_cache(maxsize=1)
def getEncryptionKey() -> str:
    load_dotenv(dotenv_path=Path(".env"))
    key = os.environ.get("DATA_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError(
            "DATA_ENCRYPTION_KEY environment variable is required to handle encrypted columns."
        )
    return key


def ensureEncryptionKey() -> None:
    getEncryptionKey()


def getEncryptedColumns(table: str) -> Dict[str, Dict[str, Any]]:
    return ENCRYPTED_COLUMNS.get(table.lower(), {})


def isEncryptedColumn(table: str, column: str) -> bool:
    return column in getEncryptedColumns(table)


def buildSelectDecryptExpr(table: str, column: str, table_alias: str) -> str:
    columns = getEncryptedColumns(table)
    if column not in columns:
        raise KeyError(f"Column '{column}' is not marked as encrypted in table '{table}'.")
    cast = columns[column].get("cast", "TEXT").upper()
    expr = f"AES_DECRYPT({table_alias}.`{column}`, %s)"
    if cast == "TEXT":
        return f"CONVERT({expr} USING utf8mb4)"
    return f"CAST({expr} AS {cast})"


def getColumnTypeDefinition(table: str, column: str) -> str:
    columns = getEncryptedColumns(table)
    if column not in columns:
        raise KeyError(f"Column '{column}' is not marked as encrypted in table '{table}'.")
    return columns[column]["type"]


def isNullableColumn(table: str, column: str) -> bool:
    columns = getEncryptedColumns(table)
    if column not in columns:
        raise KeyError(f"Column '{column}' is not marked as encrypted in table '{table}'.")
    return bool(columns[column].get("nullable", False))