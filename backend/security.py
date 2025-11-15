#!/usr/bin/env python3
"""
Security module for enhanced security features
新增的安全模块，提供加密解密、输入验证等功能
"""
import os
import base64
import re
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# RSA private key for decrypting passwords (should be loaded from secure storage)
# RSA私钥用于解密密码（应从安全存储加载）
_PRIVATE_KEY = None

def load_private_key(key_path=None):
    """
    Load RSA private key from file or environment variable
    从文件或环境变量加载RSA私钥
    
    Args:
        key_path: Path to private key file, or None to use environment variable
    """
    global _PRIVATE_KEY
    if _PRIVATE_KEY is not None:
        return _PRIVATE_KEY
    
    try:
        if key_path is None:
            key_path = os.getenv('RSA_PRIVATE_KEY_PATH', 'backend/keys/private_key.pem')
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                _PRIVATE_KEY = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            return _PRIVATE_KEY
        else:
            # Generate a new key pair if not exists (for development only)
            # 如果不存在则生成新的密钥对（仅用于开发）
            print(f"Warning: Private key not found at {key_path}. RSA decryption will be disabled.")
            return None
    except Exception as e:
        print(f"Error loading private key: {e}. RSA decryption will be disabled.")
        return None

def decrypt_password(encrypted_password_base64):
    """
    Decrypt RSA-OAEP encrypted password
    解密RSA-OAEP加密的密码
    
    Args:
        encrypted_password_base64: Base64 encoded encrypted password
        
    Returns:
        Decrypted password string, or None if decryption fails
    """
    if not encrypted_password_base64:
        return None
    
    private_key = load_private_key()
    if private_key is None:
        return None
    
    try:
        encrypted_bytes = base64.b64decode(encrypted_password_base64)
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error decrypting password: {e}")
        return None

def validate_email(email):
    """
    Validate email format
    验证邮箱格式
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    # Basic email regex pattern
    # 基本邮箱正则表达式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength
    验证密码强度
    
    Args:
        password: Password string to validate
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one letter and one number
    # 检查是否至少包含一个字母和一个数字
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_number = bool(re.search(r'\d', password))
    
    if not (has_letter and has_number):
        return False, "Password must contain at least one letter and one number"
    
    return True, None

def sanitize_input(input_str, max_length=1000):
    """
    Sanitize user input to prevent injection attacks
    清理用户输入以防止注入攻击
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string or None if invalid
    """
    if not isinstance(input_str, str):
        return None
    
    # Remove null bytes and control characters
    # 移除空字节和控制字符
    sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length
    # 限制长度
    if len(sanitized) > max_length:
        return None
    
    return sanitized.strip()

def validate_table_name(table_name):
    """
    Validate table name to prevent SQL injection
    验证表名以防止SQL注入
    
    Args:
        table_name: Table name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not table_name or not isinstance(table_name, str):
        return False
    
    # Only allow alphanumeric, underscore, and specific characters
    # 只允许字母数字、下划线和特定字符
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, table_name))

def validate_column_name(column_name):
    """
    Validate column name to prevent SQL injection
    验证列名以防止SQL注入
    
    Args:
        column_name: Column name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not column_name or not isinstance(column_name, str):
        return False
    
    # Only allow alphanumeric, underscore, and backtick
    # 只允许字母数字、下划线和反引号
    pattern = r'^[a-zA-Z0-9_`]+$'
    return bool(re.match(pattern, column_name.replace('`', '')))

def escape_identifier(identifier):
    """
    Escape SQL identifier (table/column name) to prevent injection
    转义SQL标识符（表名/列名）以防止注入
    
    Args:
        identifier: Table or column name to escape
        
    Returns:
        Escaped identifier with backticks, or None if invalid
    """
    if not identifier or not isinstance(identifier, str):
        return None
    
    # Remove backticks first, then validate
    # 先移除反引号，然后验证
    clean_identifier = identifier.replace('`', '')
    
    # Validate format
    # 验证格式
    if not validate_table_name(clean_identifier):
        return None
    
    # Escape with backticks
    # 使用反引号转义
    return f"`{clean_identifier}`"

def validate_table_name_whitelist(table_name, allowed_tables=None):
    """
    Validate table name against whitelist (more secure)
    根据白名单验证表名（更安全）
    
    Args:
        table_name: Table name to validate
        allowed_tables: List of allowed table names (None = use validation only)
        
    Returns:
        True if valid and in whitelist (if provided), False otherwise
    """
    if not validate_table_name(table_name):
        return False
    
    # If whitelist provided, check against it
    # 如果提供了白名单，则检查
    if allowed_tables is not None:
        return table_name in allowed_tables
    
    return True

def get_allowed_origins():
    """
    Get allowed CORS origins from environment variable
    从环境变量获取允许的CORS源
    
    Returns:
        List of allowed origins, or ['*'] if not set (for development)
    """
    origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '*')
    if origins_env == '*':
        return ['*']
    return [origin.strip() for origin in origins_env.split(',')]

def is_origin_allowed(origin):
    """
    Check if origin is allowed for CORS
    检查源是否允许CORS
    
    Args:
        origin: Origin string from request header
        
    Returns:
        True if allowed, False otherwise
    """
    allowed = get_allowed_origins()
    if '*' in allowed:
        return True
    return origin in allowed

def get_public_key_pem():
    """
    Get RSA public key in PEM format for frontend encryption
    获取RSA公钥的PEM格式用于前端加密
    
    Returns:
        Public key PEM string, or None if not available
    """
    private_key = load_private_key()
    if private_key is None:
        return None
    
    try:
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    except Exception as e:
        print(f"Error getting public key: {e}")
        return None

