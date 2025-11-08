#!/usr/bin/env python3
"""
Authentication module for user login and session management
"""
import hashlib
import secrets
import time
import os
import bcrypt
from db_query import db_query
from logger_config import app_logger

# Session storage - supports both in-memory and database
# 会话存储 - 支持内存和数据库两种方式
# Format: {token: {"user_id": str, "role": str, "name": str, "expires_at": float}}
ACTIVE_SESSIONS = {}

# Session expiration time (in seconds) - 2 hours (reduced from 24 hours for security)
# 会话过期时间（秒）- 2小时（从24小时减少以提高安全性）
SESSION_EXPIRY = 2 * 60 * 60

# Use database for session storage if enabled - 如果启用则使用数据库存储会话
USE_DB_SESSIONS = os.getenv('USE_DB_SESSIONS', 'false').lower() == 'true'

def hash_password(password, salt=None):
    """
    Hash password using bcrypt (more secure than SHA-256)
    使用bcrypt哈希密码（比SHA-256更安全）
    
    Args:
        password: Plain text password
        salt: Salt (ignored for bcrypt, kept for backward compatibility)
        
    Returns:
        Hashed password string
    """
    # Use bcrypt for password hashing - 使用bcrypt进行密码哈希
    # bcrypt automatically handles salt generation - bcrypt自动处理盐值生成
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password, salt, hashed_password):
    """
    Verify password against hashed password
    验证密码与哈希密码是否匹配
    
    Supports both bcrypt (new) and SHA-256 (legacy) for backward compatibility
    支持bcrypt（新）和SHA-256（旧）以保持向后兼容性
    """
    password_bytes = password.encode('utf-8')
    
    # Try bcrypt first (new format) - 先尝试bcrypt（新格式）
    try:
        hashed_bytes = hashed_password.encode('utf-8')
        if bcrypt.checkpw(password_bytes, hashed_bytes):
            return True
    except Exception:
        pass
    
    # Fallback to SHA-256 for legacy passwords - 回退到SHA-256以支持旧密码
    # This allows gradual migration - 这允许逐步迁移
    legacy_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return legacy_hash == hashed_password

def generate_token():
    """Generate a secure random token for session"""
    return secrets.token_urlsafe(32)

def authenticate_user(email, password):
    """
    Authenticate user based on email and password
    Searches in students, guardians, and staffs tables
    
    Args:
        email: User email address
        password: Plain text password
    
    Returns:
        dict with user info if successful, None if failed
        Format: {"user_id": str, "role": str, "name": str, "user_type": str}
    """
    try:
        email = str(email).strip().lower()
        
        # Try students table first
        result = db_query(
            "SELECT StuID, password, salt, first_name, last_name FROM students WHERE LOWER(email) = %s",
            (email,)
        )
        if result and result[0]:
            user = result[0]
            stored_password = user.get("password", "")
            salt = user.get("salt", "")
            
            # Verify password
            if verify_password(password, salt, stored_password):
                return {
                    "user_id": str(user["StuID"]),
                    "role": "student",
                    "name": f"{user['first_name']} {user['last_name']}",
                    "user_type": "student"
                }
        
        # Try guardians table
        result = db_query(
            "SELECT GuaID, password, salt, first_name, last_name FROM guardians WHERE LOWER(email) = %s",
            (email,)
        )
        if result and result[0]:
            user = result[0]
            stored_password = user.get("password", "")
            salt = user.get("salt", "")
            
            # Verify password
            if verify_password(password, salt, stored_password):
                return {
                    "user_id": str(user["GuaID"]),
                    "role": "guardian",
                    "name": f"{user['first_name']} {user['last_name']}",
                    "user_type": "guardian"
                }
        
        # Try staffs table
        result = db_query(
            "SELECT StfID, password, salt, role, department, first_name, last_name FROM staffs WHERE LOWER(email) = %s",
            (email,)
        )
        if result and result[0]:
            user = result[0]
            stored_password = user.get("password", "")
            salt = user.get("salt", "")
            
            # Verify password
            if verify_password(password, salt, stored_password):
                # Map staff role to system role based on department and role
                staff_role = user.get("role", "").lower()
                department = user.get("department", "").lower()
                
                # Determine system role based on department and role
                # Academic Affairs department typically handles grades -> aro
                # Disciplinary-related roles -> dro
                # Others -> root (for testing/admin access)
                system_role = None
                
                if "academic" in department:
                    # Academic Affairs department -> Academic Records Officer (aro)
                    system_role = "aro"
                elif "disciplinary" in staff_role or "disciplinary" in department:
                    # Disciplinary-related -> Disciplinary Records Officer (dro)
                    system_role = "dro"
                else:
                    # Default to root for other staff (testing/admin access)
                    # This includes: Human Resources, IT Support, etc.
                    system_role = "root"
                
                return {
                    "user_id": str(user["StfID"]),
                    "role": system_role,
                    "name": f"{user['first_name']} {user['last_name']}",
                    "user_type": "staff"
                }
        
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_session(user_info):
    """
    Create a new session for authenticated user
    为已认证用户创建新会话
    
    Args:
        user_info: Dict with user_id, role, name, user_type
    
    Returns:
        session token string
    """
    token = generate_token()
    session_data = {
        "user_id": user_info["user_id"],
        "role": user_info["role"],
        "name": user_info["name"],
        "user_type": user_info.get("user_type", ""),
        "expires_at": time.time() + SESSION_EXPIRY
    }
    
    # Store in memory - 存储在内存中
    ACTIVE_SESSIONS[token] = session_data
    
    # Also store in database if enabled - 如果启用则也存储在数据库中
    if USE_DB_SESSIONS:
        try:
            from db_query import db_execute
            db_execute(
                "INSERT INTO sessions (token, user_id, role, expires_at, created_at) VALUES (%s, %s, %s, %s, NOW()) "
                "ON DUPLICATE KEY UPDATE expires_at = %s",
                (token, user_info["user_id"], user_info["role"], session_data["expires_at"], session_data["expires_at"])
            )
            app_logger.info(f"Session stored in database for user {user_info['user_id']}")
        except Exception as e:
            app_logger.warning(f"Failed to store session in database: {e}, using memory only")
    
    app_logger.info(f"Session created for user {user_info['user_id']} with role {user_info['role']}")
    return token

def validate_session(token):
    """
    Validate session token and return user info
    验证会话令牌并返回用户信息
    
    Args:
        token: Session token
    
    Returns:
        dict with user info if valid, None if invalid/expired
    """
    if not token:
        return None
    
    # Try memory first - 先尝试内存
    session = ACTIVE_SESSIONS.get(token)
    
    # If not in memory and DB sessions enabled, try database - 如果不在内存中且启用了数据库会话，尝试数据库
    if not session and USE_DB_SESSIONS:
        try:
            result = db_query(
                "SELECT user_id, role, expires_at FROM sessions WHERE token = %s AND expires_at > NOW()",
                (token,)
            )
            if result and result[0]:
                session = {
                    "user_id": result[0]["user_id"],
                    "role": result[0]["role"],
                    "expires_at": result[0]["expires_at"].timestamp() if hasattr(result[0]["expires_at"], 'timestamp') else time.time() + SESSION_EXPIRY
                }
                # Cache in memory - 缓存在内存中
                ACTIVE_SESSIONS[token] = session
        except Exception as e:
            app_logger.warning(f"Failed to validate session from database: {e}")
    
    if not session:
        return None
    
    # Check expiration - 检查过期
    if time.time() > session["expires_at"]:
        if token in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[token]
        if USE_DB_SESSIONS:
            try:
                from db_query import db_execute
                db_execute("DELETE FROM sessions WHERE token = %s", (token,))
            except Exception:
                pass
        return None
    
    return {
        "user_id": session["user_id"],
        "role": session["role"],
        "personId": session["user_id"]
    }

def logout(token):
    """
    Remove session token
    移除会话令牌
    """
    removed = False
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
        removed = True
    
    # Also remove from database if enabled - 如果启用则也从数据库移除
    if USE_DB_SESSIONS:
        try:
            from db_query import db_execute
            db_execute("DELETE FROM sessions WHERE token = %s", (token,))
            removed = True
        except Exception as e:
            app_logger.warning(f"Failed to remove session from database: {e}")
    
    if removed:
        app_logger.info(f"Session logged out: {token[:8]}...")
    
    return removed

def cleanup_expired_sessions():
    """Remove expired sessions (call periodically)"""
    current_time = time.time()
    expired_tokens = [
        token for token, session in ACTIVE_SESSIONS.items()
        if current_time > session["expires_at"]
    ]
    for token in expired_tokens:
        del ACTIVE_SESSIONS[token]

