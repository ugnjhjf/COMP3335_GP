#!/usr/bin/env python3
"""
Authentication module for user login and session management
"""
import hashlib
import secrets
import time
from db_query import db_query

# In-memory session storage (for production, use Redis or database)
# Format: {token: {"user_id": str, "role": str, "name": str, "expires_at": float}}
ACTIVE_SESSIONS = {}

# Session expiration time (in seconds) - 24 hours
SESSION_EXPIRY = 24 * 60 * 60

def hash_password(password, salt):
    """Hash password with salt using SHA-256"""
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_password(password, salt, hashed_password):
    """Verify password against hashed password with salt"""
    return hash_password(password, salt) == hashed_password

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
    
    Args:
        user_info: Dict with user_id, role, name, user_type
    
    Returns:
        session token string
    """
    token = generate_token()
    ACTIVE_SESSIONS[token] = {
        "user_id": user_info["user_id"],
        "role": user_info["role"],
        "name": user_info["name"],
        "user_type": user_info.get("user_type", ""),
        "expires_at": time.time() + SESSION_EXPIRY
    }
    return token

def validate_session(token):
    """
    Validate session token and return user info
    
    Args:
        token: Session token
    
    Returns:
        dict with user info if valid, None if invalid/expired
    """
    if not token:
        return None
    
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        return None
    
    # Check expiration
    if time.time() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        return None
    
    return {
        "user_id": session["user_id"],
        "role": session["role"],
        "personId": session["user_id"]
    }

def logout(token):
    """Remove session token"""
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
        return True
    return False

def cleanup_expired_sessions():
    """Remove expired sessions (call periodically)"""
    current_time = time.time()
    expired_tokens = [
        token for token, session in ACTIVE_SESSIONS.items()
        if current_time > session["expires_at"]
    ]
    for token in expired_tokens:
        del ACTIVE_SESSIONS[token]

