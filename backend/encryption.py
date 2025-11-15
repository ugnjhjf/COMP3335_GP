import os
from functools import lru_cache
from typing import Any, Dict
from pathlib import Path
from dotenv import load_dotenv

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


def _find_env_file() -> Path:
    """
    Find .env file by searching from current directory up to project root
    从当前目录向上查找项目根目录的.env文件
    """
    current = Path(__file__).resolve().parent  # backend directory
    root = current.parent  # project root
    
    # Try project root first
    env_path = root / ".env"
    if env_path.exists():
        return env_path
    
    # Try backend directory
    env_path = current / ".env"
    if env_path.exists():
        return env_path
    
    # Try current working directory
    env_path = Path(".env").resolve()
    if env_path.exists():
        return env_path
    
    # Return project root path (will be used by load_dotenv to search)
    return root


@lru_cache(maxsize=1)
def getEncryptionKey() -> str:
    # Find .env file location
    env_path = _find_env_file()
    
    # Load .env file - load_dotenv will search upward if file not found at exact path
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        # If .env not found, let load_dotenv search from project root
        load_dotenv(dotenv_path=env_path / ".env", override=True)
        # Also try without specifying path (searches from current directory upward)
        load_dotenv(override=True)
    
    key = os.environ.get("DATA_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError(
            f"DATA_ENCRYPTION_KEY environment variable is required to handle encrypted columns.\n"
            f"Please ensure .env file exists in project root or backend directory with DATA_ENCRYPTION_KEY set.\n"
            f"Searched paths: {env_path}, {Path(__file__).parent / '.env'}, {Path('.env').resolve()}"
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