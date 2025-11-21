#!/usr/bin/env python3
"""
Data encryption module for sensitive fields
Uses MySQL AES_ENCRYPT/AES_DECRYPT functions
"""
import os
import secrets
from typing import Dict, Optional

# Encryption keys for different roles
# Keys should be stored in environment variables or key files (not in database)
ENCRYPTION_KEYS = {
    'student': os.getenv('ENCRYPTION_KEY_STUDENT', secrets.token_hex(16)),
    'guardian': os.getenv('ENCRYPTION_KEY_GUARDIAN', secrets.token_hex(16)),
    'aro': os.getenv('ENCRYPTION_KEY_ARO', secrets.token_hex(16)),
    'dro': os.getenv('ENCRYPTION_KEY_DRO', secrets.token_hex(16)),
    'root': os.getenv('ENCRYPTION_KEY_ROOT', secrets.token_hex(16)),
}

# Sensitive fields that need encryption
SENSITIVE_FIELDS = {
    'students': ['identification_number', 'address'],
    'staffs': ['identification_number', 'address'],
    'guardians': ['address'],  # Add if address field exists
}

def get_encryption_key(role: str) -> str:
    """
    Get encryption key for specific role
    
    Args:
        role: User role (student, guardian, aro, dro, root)
        
    Returns:
        Encryption key string
    """
    return ENCRYPTION_KEYS.get(role.lower(), ENCRYPTION_KEYS['root'])

def encrypt_field_sql(field_name: str, value: str, role: str) -> str:
    """
    Generate SQL for encrypting a field using MySQL AES_ENCRYPT
    
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
    # Use AES_ENCRYPT with key
    # Note: In production, use prepared statements with parameterized queries
    return f"AES_ENCRYPT(%s, '{key}')"

def decrypt_field_sql(field_name: str, role: str) -> str:
    """
    Generate SQL for decrypting a field using MySQL AES_DECRYPT
    
    Args:
        field_name: Field name to decrypt
        role: User role for key selection
        
    Returns:
        SQL expression for decrypted field
    """
    key = get_encryption_key(role)
    # Use AES_DECRYPT with key
    return f"AES_DECRYPT(`{field_name}`, '{key}') AS `{field_name}`"

def is_sensitive_field(table_name: str, field_name: str) -> bool:
    """
    Check if a field is sensitive and needs encryption
    
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
    
    Args:
        table_name: Table name
        
    Returns:
        List of sensitive field names
    """
    return SENSITIVE_FIELDS.get(table_name.lower(), [])

def process_encrypted_data(data: Dict, table_name: str, role: str) -> Dict:
    """
    Process query results to decrypt sensitive fields
    
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
    
    # Decrypt sensitive fields
    # Note: This is a fallback if decryption wasn't done in SQL
    for field in sensitive_fields:
        if field in result and result[field]:
            # If field is already decrypted in SQL, skip
            if isinstance(result[field], bytes):
                try:
                    key = get_encryption_key(role)
                    from db_query import db_query
                    # Decrypt using MySQL function
                    decrypted = db_query(
                        f"SELECT AES_DECRYPT(%s, %s) as decrypted",
                        (result[field], key)
                    )
                    if decrypted and decrypted[0].get('decrypted'):
                        result[field] = decrypted[0]['decrypted'].decode('utf-8') if isinstance(decrypted[0]['decrypted'], bytes) else decrypted[0]['decrypted']
                except Exception:
                    pass
    
    return result

