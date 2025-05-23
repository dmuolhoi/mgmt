"""
Base User model for the School Management System
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class User:
    """Base User class"""
    
    def __init__(self, username: str, role: str, 
                 user_id: Optional[str] = None, 
                 **kwargs: Any) -> None:
        """
        Initialize a User object.
        
        Args:
            username: Username for the user
            role: Role of the user (admin, teacher, student, etc.)
            user_id: User ID (generated if not provided)
            **kwargs: Additional user attributes
        """
        self.id = user_id or str(uuid.uuid4())
        self.username = username
        self.role = role
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.modified_at = kwargs.get('modified_at', self.created_at)
        
        # Additional attributes
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone', '')
        self.address = kwargs.get('address', '')
        self.is_active = kwargs.get('is_active', True)
    
    @property
    def full_name(self) -> str:
        """Get the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user object to dictionary.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User object from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User object
        """
        return cls(
            username=data.get("username", ""),
            role=data.get("role", ""),
            user_id=data.get("id"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            is_active=data.get("is_active", True)
        )