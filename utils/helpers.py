"""
Helper functions for the School Management System
"""
import os
import re
import json
import random
import string
from datetime import datetime
from typing import List, Dict, Any, Optional

def clear_screen() -> None:
    """Clear the terminal screen."""
    print("\n" * 100)

def format_date(date_str: str) -> str:
    """
    Format ISO date string to a more readable format.
    
    Args:
        date_str: ISO format date string
    
    Returns:
        Formatted date string (e.g., 'January 1, 2023')
    """
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str

def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: The email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: The phone number to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Remove any non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    # Check if it has 10-15 digits (international numbers can be longer)
    return 10 <= len(digits_only) <= 15

def generate_id(prefix: str, length: int = 6) -> str:
    """
    Generate a unique ID with a given prefix.
    
    Args:
        prefix: Prefix for the ID (e.g., 'STU' for students)
        length: Length of the random part of the ID
    
    Returns:
        Generated ID (e.g., 'STU123456')
    """
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}{random_part}"

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user data by ID.
    
    Args:
        user_id: The ID of the user to find
    
    Returns:
        User data if found, None otherwise
    """
    from storage.datastore import get_data
    
    users = get_data('users')
    
    for username, user in users.items():
        if user["id"] == user_id:
            return user
    
    return None

def get_username_by_id(user_id: str) -> Optional[str]:
    """
    Get username by user ID.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        Username if found, None otherwise
    """
    user = get_user_by_id(user_id)
    return user["username"] if user else None

def format_currency(amount: float) -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
    
    Returns:
        Formatted currency string (e.g., '$1,234.56')
    """
    return f"${amount:,.2f}"

def calculate_grade_letter(score: float) -> str:
    """
    Calculate letter grade from a numerical score.
    
    Args:
        score: Numerical score (0-100)
    
    Returns:
        Letter grade based on GRADE_SCALE
    """
    from utils.constants import GRADE_SCALE
    
    for grade, (min_score, max_score) in GRADE_SCALE.items():
        if min_score <= score <= max_score:
            return grade
    
    return "F"  # Default to F if no match found

def paginate(items: List[Any], page_size: int = 10, 
             page: int = 1) -> List[Any]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page_size: Number of items per page
        page: Page number (1-based)
    
    Returns:
        Items for the requested page
    """
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return items[start_idx:end_idx]

def get_current_term() -> str:
    """
    Get the current academic term based on the date.
    
    Returns:
        Current term (e.g., 'Fall 2023')
    """
    now = datetime.now()
    year = now.year
    
    # Determine semester based on month
    if 1 <= now.month <= 5:
        term = "Spring"
    elif 6 <= now.month <= 7:
        term = "Summer"
    else:
        term = "Fall"
    
    return f"{term} {year}"