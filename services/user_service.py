"""
User service for the School Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from auth import hash_password
from storage.datastore import get_data, save_data
from utils.constants import USER_ROLES
from utils.helpers import validate_email, validate_phone

def create_user(username: str, password: str, role: str, 
                first_name: str = "", last_name: str = "", 
                email: str = "", phone: str = "", 
                created_by: str = None) -> Tuple[bool, str, Optional[str]]:
    """
    Create a new user.
    
    Args:
        username: Username for the new user
        password: Password for the new user
        role: Role of the new user
        first_name: First name of the user
        last_name: Last name of the user
        email: Email of the user
        phone: Phone number of the user
        created_by: Username of the user creating this user
    
    Returns:
        Tuple of (success, message, user_id)
    """
    # Validate inputs
    if not username or not password:
        return False, "❌ Username and password are required.", None
    
    if email and not validate_email(email):
        return False, "❌ Invalid email format.", None
    
    if phone and not validate_phone(phone):
        return False, "❌ Invalid phone number format.", None
    
    # Check if username already exists
    users = get_data('users')
    if username in users:
        return False, "❌ Username already exists.", None
    
    # Generate user ID based on role
    import uuid
    user_id = str(uuid.uuid4())
    
    # Create user
    users[username] = {
        "id": user_id,
        "username": username,
        "password": hash_password(password),
        "role": role,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "created_at": datetime.now().isoformat(),
        "created_by": created_by,
        "is_active": True
    }
    
    save_data('users', users)
    
    return True, f"✅ User '{username}' created successfully.", user_id

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user data by username.
    
    Args:
        username: The username to find
    
    Returns:
        User data if found, None otherwise
    """
    users = get_data('users')
    return users.get(username)

def list_users_by_role(role: str) -> List[Dict[str, Any]]:
    """
    Get a list of users with a specific role.
    
    Args:
        role: The role to filter by
    
    Returns:
        List of users with the specified role
    """
    users = get_data('users')
    
    return [
        user 
        for username, user in users.items() 
        if user.get("role") == role
    ]

def update_user(username: str, update_data: Dict[str, Any], 
                updater_username: str = None) -> Tuple[bool, str]:
    """
    Update a user's information.
    
    Args:
        username: The username of the user to update
        update_data: The data to update
        updater_username: The username of the user making the update
    
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    if username not in users:
        return False, f"❌ User '{username}' not found."
    
    # Update user data
    for key, value in update_data.items():
        if key != "password":  # Password should be updated separately
            users[username][key] = value
    
    # Update modification metadata
    users[username]["modified_at"] = datetime.now().isoformat()
    if updater_username:
        users[username]["modified_by"] = updater_username
    
    save_data('users', users)
    
    return True, f"✅ User '{username}' updated successfully."

def update_user_password(username: str, new_password: str, 
                        updater_username: str = None) -> Tuple[bool, str]:
    """
    Update a user's password.
    
    Args:
        username: The username of the user to update
        new_password: The new password
        updater_username: The username of the user making the update
    
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    if username not in users:
        return False, f"❌ User '{username}' not found."
    
    # Update password
    users[username]["password"] = hash_password(new_password)
    
    # Update modification metadata
    users[username]["modified_at"] = datetime.now().isoformat()
    if updater_username:
        users[username]["modified_by"] = updater_username
    
    save_data('users', users)
    
    return True, f"✅ Password for user '{username}' updated successfully."

def deactivate_user(username: str, 
                   deactivator_username: str = None) -> Tuple[bool, str]:
    """
    Deactivate a user.
    
    Args:
        username: The username of the user to deactivate
        deactivator_username: The username of the user making the deactivation
    
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    if username not in users:
        return False, f"❌ User '{username}' not found."
    
    # Deactivate user
    users[username]["is_active"] = False
    
    # Update modification metadata
    users[username]["modified_at"] = datetime.now().isoformat()
    if deactivator_username:
        users[username]["modified_by"] = deactivator_username
    
    save_data('users', users)
    
    return True, f"✅ User '{username}' deactivated successfully."

def activate_user(username: str, 
                 activator_username: str = None) -> Tuple[bool, str]:
    """
    Activate a user.
    
    Args:
        username: The username of the user to activate
        activator_username: The username of the user making the activation
    
    Returns:
        Tuple of (success, message)
    """
    users = get_data('users')
    
    if username not in users:
        return False, f"❌ User '{username}' not found."
    
    # Activate user
    users[username]["is_active"] = True
    
    # Update modification metadata
    users[username]["modified_at"] = datetime.now().isoformat()
    if activator_username:
        users[username]["modified_by"] = activator_username
    
    save_data('users', users)
    
    return True, f"✅ User '{username}' activated successfully."

def check_user_exists(username: str) -> bool:
    """
    Check if a user exists.
    
    Args:
        username: The username to check
    
    Returns:
        True if user exists, False otherwise
    """
    users = get_data('users')
    return username in users

def get_user_role(username: str) -> Optional[str]:
    """
    Get a user's role.
    
    Args:
        username: The username to check
    
    Returns:
        User's role if found, None otherwise
    """
    user = get_user_by_username(username)
    return user.get("role") if user else None

def count_users_by_role() -> Dict[str, int]:
    """
    Count users by role.
    
    Returns:
        Dictionary with counts for each role
    """
    users = get_data('users')
    counts = {
        USER_ROLES.ADMIN: 0,
        USER_ROLES.TEACHER: 0,
        USER_ROLES.STUDENT: 0,
        USER_ROLES.PARENT: 0,
        USER_ROLES.STAFF: 0,
        "pending": 0,
        "other": 0
    }
    
    for user in users.values():
        role = user.get("role", "other")
        if role in counts:
            counts[role] += 1
        else:
            counts["other"] += 1
    
    return counts