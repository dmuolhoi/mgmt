"""
Authentication module for the School Management System
"""
import hashlib
import uuid
import json
import os
from typing import Dict, Tuple, Optional, Any, List
from utils.constants import USER_ROLES, DATA_DIR
from storage.datastore import get_data, save_data

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password: The password to hash
        
    Returns:
        The hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user using username and password.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        User data if authentication successful, None otherwise
    """
    users = get_data('users')
    
    # Check if username exists
    if username not in users:
        return None
    
    user = users[username]
    hashed_password = hash_password(password)
    
    # Check if password matches
    if user["password"] == hashed_password:
        return user
    
    return None

def register_new_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user in the system.
    
    Args:
        username: The username for the new user
        password: The password for the new user
        
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    # Check if username already exists
    if username in users:
        return False, "❌ Username already exists"
    
    # If this is the first user, make them an admin
    if not users:
        role = USER_ROLES.ADMIN
        message = "✅ Admin account created successfully"
    else:
        # Otherwise, register as a pending user that needs admin approval
        role = "pending"
        message = "✅ Registration submitted. Awaiting admin approval."
    
    # Create user record
    users[username] = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": hash_password(password),
        "role": role,
        "created_at": __import__('datetime').datetime.now().isoformat()
    }
    
    # Save the updated users data
    save_data('users', users)
    
    return True, message

def update_user_role(username: str, new_role: str, admin_username: str) -> Tuple[bool, str]:
    """
    Update a user's role (admin only).
    
    Args:
        username: The username of the user to update
        new_role: The new role to assign
        admin_username: The username of the admin making the change
        
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    # Check if admin exists and is actually an admin
    if admin_username not in users or users[admin_username]["role"] != USER_ROLES.ADMIN:
        return False, "❌ Only administrators can change user roles"
    
    # Check if user exists
    if username not in users:
        return False, f"❌ User '{username}' not found"
    
    # Check if new_role is valid
    if new_role not in [USER_ROLES.ADMIN, USER_ROLES.TEACHER, USER_ROLES.STUDENT, USER_ROLES.PARENT, USER_ROLES.STAFF]:
        return False, "❌ Invalid role"
    
    # Update the user's role
    users[username]["role"] = new_role
    save_data('users', users)
    
    return True, f"✅ User '{username}' role updated to {new_role}"

def get_pending_registrations() -> List[Dict[str, Any]]:
    """
    Get a list of pending user registrations.
    
    Returns:
        List of pending user data
    """
    users = get_data('users')
    return [user for username, user in users.items() if user["role"] == "pending"]

def approve_registration(username: str, role: str, admin_username: str) -> Tuple[bool, str]:
    """
    Approve a pending registration (admin only).
    
    Args:
        username: The username of the pending user
        role: The role to assign to the user
        admin_username: The username of the admin making the approval
        
    Returns:
        Tuple of (success, message)
    """
    return update_user_role(username, role, admin_username)

def reject_registration(username: str, admin_username: str) -> Tuple[bool, str]:
    """
    Reject a pending registration (admin only).
    
    Args:
        username: The username of the pending user
        admin_username: The username of the admin making the rejection
        
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    # Check if admin exists and is actually an admin
    if admin_username not in users or users[admin_username]["role"] != USER_ROLES.ADMIN:
        return False, "❌ Only administrators can reject registrations"
    
    # Check if user exists and is pending
    if username not in users:
        return False, f"❌ User '{username}' not found"
    if users[username]["role"] != "pending":
        return False, f"❌ User '{username}' is not a pending registration"
    
    # Remove the user
    del users[username]
    save_data('users', users)
    
    return True, f"✅ Registration for '{username}' has been rejected"