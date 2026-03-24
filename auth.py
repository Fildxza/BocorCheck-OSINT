"""
Authentication module for FYP OSINT Dashboard.
Handles user registration, login, password hashing, and validation.
"""

import re
from typing import Optional, Tuple, Dict, Any
from mysql.connector import Error as MySQLError
from mysql.connector import connect
import bcrypt
import os


def get_db_connection():
    """Create MySQL connection from environment configuration."""
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }
    return connect(**config)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with salt rounds of 12.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string (bcrypt format)
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify plain text password against bcrypt hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Bcrypt hash from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format using RFC 5322 simplified pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    email = email.strip().lower()
    
    if not email or len(email) > 255:
        return False, "Email is required and must be under 255 characters."
    
    # Simplified RFC 5322 pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Please enter a valid email address (e.g., user@example.com)."
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    Rules: 3-50 chars, alphanumeric + underscore/hyphen, no spaces.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    username = username.strip()
    
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters."
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Rules: min 8 chars, at least 1 uppercase, 1 lowercase, 1 number, 1 special char.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?]', password):
        return False, "Password must contain at least one special character (!@#$%^&* etc)."
    
    return True, ""


def check_user_exists(email: str = "", username: str = "") -> bool:
    """
    Check if user exists by email or username.
    
    Args:
        email: Email to check (optional)
        username: Username to check (optional)
        
    Returns:
        True if user exists, False otherwise
    """
    if not email and not username:
        return False
    
    query = "SELECT id FROM users WHERE 1=0"
    params: list = []
    
    if email:
        query += " OR email = %s"
        params.append(email.strip().lower())
    
    if username:
        query += " OR username = %s"
        params.append(username.strip())
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result is not None
    except MySQLError:
        return False


def create_user(username: str, email: str, password: str, role: str = "user") -> Tuple[bool, str, Optional[int]]:
    """
    Create new user account.
    
    Args:
        username: Desired username
        email: User email
        password: Plain text password
        role: User role (default: "user")
        
    Returns:
        Tuple of (success, message, user_id)
    """
    # Validate inputs
    is_valid, msg = validate_username(username)
    if not is_valid:
        return False, msg, None
    
    is_valid, msg = validate_email(email)
    if not is_valid:
        return False, msg, None
    
    is_valid, msg = validate_password(password)
    if not is_valid:
        return False, msg, None
    
    # Check for duplicates
    email_lower = email.strip().lower()
    username_lower = username.strip()
    
    if check_user_exists(email=email_lower, username=username_lower):
        return False, "Email or username is already registered.", None
    
    # Hash password securely
    password_hash = hash_password(password)
    
    # Insert into database
    insert_query = """
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, TRUE)
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    insert_query,
                    (username_lower, email_lower, password_hash, role)
                )
            conn.commit()
            
            # Return the newly created user_id
            with conn.cursor() as cursor:
                cursor.execute("SELECT LAST_INSERT_ID()")
                user_id = cursor.fetchone()[0]
            
            return True, "User account created successfully.", user_id
    
    except MySQLError as e:
        return False, f"Database error: {str(e)[:100]}", None


def login_user(email_or_username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate user and return user data if successful.
    
    Args:
        email_or_username: Email or username
        password: Plain text password
        
    Returns:
        Tuple of (success, message, user_data_dict or None)
    """
    if not email_or_username or not password:
        return False, "Email/username and password are required.", None
    
    identifier = email_or_username.strip().lower()
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Find user by email or username
                query = """
                    SELECT id, username, email, password_hash, role, is_active
                    FROM users
                    WHERE (email = %s OR username = %s) AND is_active = TRUE
                    LIMIT 1
                """
                cursor.execute(query, (identifier, identifier))
                user = cursor.fetchone()
        
        if not user:
            return False, "Invalid email/username or password.", None
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return False, "Invalid email/username or password.", None
        
        # Return user data without password hash
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
        }
        
        return True, "Login successful.", user_data
    
    except MySQLError:
        return False, "Database error during login. Please try again.", None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user information by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User data dictionary or None if not found
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, username, email, role, is_active, created_at
                    FROM users
                    WHERE id = %s
                    LIMIT 1
                """
                cursor.execute(query, (user_id,))
                return cursor.fetchone()
    except MySQLError:
        return None
