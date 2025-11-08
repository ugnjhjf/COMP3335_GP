#!/usr/bin/env python3
"""
CSRF protection module for database security
CSRF保护模块，用于数据库安全
"""
import secrets
import time
import hashlib
from typing import Optional, Dict

# In-memory CSRF token storage (for production, use Redis or database)
# 内存中的CSRF令牌存储（生产环境应使用Redis或数据库）
CSRF_TOKENS: Dict[str, Dict] = {}

# CSRF token expiration time (in seconds) - 1 hour
# CSRF令牌过期时间（秒）- 1小时
CSRF_TOKEN_EXPIRY = 60 * 60

def generate_csrf_token(user_id: str, session_token: str) -> str:
    """
    Generate CSRF token for user session
    为用户会话生成CSRF令牌
    
    Args:
        user_id: User ID
        session_token: Session token
        
    Returns:
        CSRF token string
    """
    # Create token from user_id, session_token, and random value
    # 从用户ID、会话令牌和随机值创建令牌
    random_value = secrets.token_urlsafe(16)
    token_data = f"{user_id}:{session_token}:{random_value}:{time.time()}"
    token = hashlib.sha256(token_data.encode('utf-8')).hexdigest()
    
    # Store token with expiration - 存储带过期时间的令牌
    CSRF_TOKENS[token] = {
        'user_id': user_id,
        'session_token': session_token,
        'created_at': time.time(),
        'expires_at': time.time() + CSRF_TOKEN_EXPIRY
    }
    
    return token

def validate_csrf_token(token: str, user_id: str, session_token: str) -> bool:
    """
    Validate CSRF token
    验证CSRF令牌
    
    Args:
        token: CSRF token to validate
        user_id: User ID
        session_token: Session token
        
    Returns:
        True if valid, False otherwise
    """
    if not token:
        return False
    
    token_info = CSRF_TOKENS.get(token)
    if not token_info:
        return False
    
    # Check expiration - 检查过期
    if time.time() > token_info['expires_at']:
        del CSRF_TOKENS[token]
        return False
    
    # Verify user_id and session_token match - 验证用户ID和会话令牌匹配
    if token_info['user_id'] != user_id or token_info['session_token'] != session_token:
        return False
    
    return True

def revoke_csrf_token(token: str):
    """
    Revoke CSRF token (e.g., on logout)
    撤销CSRF令牌（例如，登出时）
    
    Args:
        token: CSRF token to revoke
    """
    if token in CSRF_TOKENS:
        del CSRF_TOKENS[token]

def cleanup_expired_csrf_tokens():
    """
    Remove expired CSRF tokens (call periodically)
    移除过期的CSRF令牌（定期调用）
    """
    current_time = time.time()
    expired_tokens = [
        token for token, info in CSRF_TOKENS.items()
        if current_time > info['expires_at']
    ]
    for token in expired_tokens:
        del CSRF_TOKENS[token]

