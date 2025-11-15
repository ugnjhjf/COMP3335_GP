#!/usr/bin/env python3
"""
Data encryption module for sensitive fields
敏感字段数据加密模块
Uses MySQL AES_ENCRYPT/AES_DECRYPT functions
使用MySQL的AES_ENCRYPT/AES_DECRYPT函数
"""
import os
import secrets
from typing import Dict, Optional

# Encryption keys for different roles - 不同角色的加密密钥
# Keys should be stored in environment variables or key files (not in database)
# 密钥应存储在环境变量或密钥文件中（不在数据库中）
ENCRYPTION_KEYS = {
    'student': os.getenv('ENCRYPTION_KEY_STUDENT', secrets.token_hex(16)),
    'guardian': os.getenv('ENCRYPTION_KEY_GUARDIAN', secrets.token_hex(16)),
    'aro': os.getenv('ENCRYPTION_KEY_ARO', secrets.token_hex(16)),
    'dro': os.getenv('ENCRYPTION_KEY_DRO', secrets.token_hex(16)),
    'root': os.getenv('ENCRYPTION_KEY_ROOT', secrets.token_hex(16)),
}

# Sensitive fields that need encryption - 需要加密的敏感字段
SENSITIVE_FIELDS = {
    'students': ['identification_number', 'address'],
    'staffs': ['identification_number', 'address'],
    'guardians': ['address'],  # Add if address field exists - 如果存在地址字段则添加
}

def get_encryption_key(role: str) -> str:
    """
    Get encryption key for specific role
    获取特定角色的加密密钥
    
    Args:
        role: User role (student, guardian, aro, dro, root)
        
    Returns:
        Encryption key string
    """
    return ENCRYPTION_KEYS.get(role.lower(), ENCRYPTION_KEYS['root'])

def encrypt_field_sql(field_name: str, value: str, role: str) -> str:
    """
    Generate SQL for encrypting a field using MySQL AES_ENCRYPT
    生成使用MySQL AES_ENCRYPT加密字段的SQL
    
    Args:
        field_name: Field name to encrypt
        value: Value to encrypt
        role: User role for key selection
        
    Returns:
        SQL expression for encrypted field
    """
    if not value:
        return 'NULL'
    
    key = get_encryption_key(role)
    # Use AES_ENCRYPT with key - 使用AES_ENCRYPT和密钥
    # Note: In production, use prepared statements with parameterized queries
    # 注意：在生产环境中，使用参数化查询的预编译语句
    return f"AES_ENCRYPT(%s, '{key}')"

def decrypt_field_sql(field_name: str, role: str) -> str:
    """
    Generate SQL for decrypting a field using MySQL AES_DECRYPT
    生成使用MySQL AES_DECRYPT解密字段的SQL
    
    Args:
        field_name: Field name to decrypt
        role: User role for key selection
        
    Returns:
        SQL expression for decrypted field
    """
    key = get_encryption_key(role)
    # Use AES_DECRYPT with key - 使用AES_DECRYPT和密钥
    return f"AES_DECRYPT(`{field_name}`, '{key}') AS `{field_name}`"

def is_sensitive_field(table_name: str, field_name: str) -> bool:
    """
    Check if a field is sensitive and needs encryption
    检查字段是否为敏感字段需要加密
    
    Args:
        table_name: Table name
        field_name: Field name
        
    Returns:
        True if field is sensitive, False otherwise
    """
    return field_name in SENSITIVE_FIELDS.get(table_name.lower(), [])

def get_sensitive_fields(table_name: str) -> list:
    """
    Get list of sensitive fields for a table
    获取表的敏感字段列表
    
    Args:
        table_name: Table name
        
    Returns:
        List of sensitive field names
    """
    return SENSITIVE_FIELDS.get(table_name.lower(), [])

def process_encrypted_data(data: Dict, table_name: str, role: str) -> Dict:
    """
    Process query results to decrypt sensitive fields
    处理查询结果以解密敏感字段
    
    Args:
        data: Query result dictionary
        table_name: Table name
        role: User role for key selection
        
    Returns:
        Dictionary with decrypted sensitive fields
    """
    if not data:
        return data
    
    sensitive_fields = get_sensitive_fields(table_name)
    result = data.copy()
    
    # Decrypt sensitive fields - 解密敏感字段
    # Note: This is a fallback if decryption wasn't done in SQL
    # 注意：如果SQL中没有解密，这是备用方案
    for field in sensitive_fields:
        if field in result and result[field]:
            # If field is already decrypted in SQL, skip
            # 如果字段已在SQL中解密，跳过
            if isinstance(result[field], bytes):
                try:
                    key = get_encryption_key(role)
                    from db_query import db_query
                    # Decrypt using MySQL function - 使用MySQL函数解密
                    decrypted = db_query(
                        f"SELECT AES_DECRYPT(%s, %s) as decrypted",
                        (result[field], key)
                    )
                    if decrypted and decrypted[0].get('decrypted'):
                        result[field] = decrypted[0]['decrypted'].decode('utf-8') if isinstance(decrypted[0]['decrypted'], bytes) else decrypted[0]['decrypted']
                except Exception:
                    pass
    
    return result

