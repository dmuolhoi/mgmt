"""
Teacher model for the School Management System
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.user import User
from utils.helpers import generate_id

class Teacher(User):
    """Teacher class representing a teacher in the school"""
    
    def __init__(self, username: str, teacher_id: Optional[str] = None, 
                 **kwargs: Any) -> None:
        """
        Initialize a Teacher object.
        
        Args:
            username: Username for the teacher
            teacher_id: Teacher ID (generated if not provided)
            **kwargs: Additional teacher attributes
        """
        super().__init__(username, "teacher", teacher_id or generate_id("TCH"), **kwargs)
        
        # Teacher-specific attributes
        self.subjects = kwargs.get('subjects', [])
        self.classes = kwargs.get('classes', [])
        self.qualifications = kwargs.get('qualifications', [])
        self.hire_date = kwargs.get('hire_date', datetime.now().isoformat())
        self.department = kwargs.get('department', '')
        self.salary = kwargs.get('salary', 0.0)
        self.schedule = kwargs.get('schedule', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert teacher object to dictionary.
        
        Returns:
            Dictionary representation of the teacher
        """
        data = super().to_dict()
        data.update({
            "subjects": self.subjects,
            "classes": self.classes,
            "qualifications": self.qualifications,
            "hire_date": self.hire_date,
            "department": self.department,
            "salary": self.salary,
            "schedule": self.schedule
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Teacher':
        """
        Create a Teacher object from a dictionary.
        
        Args:
            data: Dictionary containing teacher data
            
        Returns:
            Teacher object
        """
        return cls(
            username=data.get("username", ""),
            teacher_id=data.get("id"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            is_active=data.get("is_active", True),
            subjects=data.get("subjects", []),
            classes=data.get("classes", []),
            qualifications=data.get("qualifications", []),
            hire_date=data.get("hire_date", ""),
            department=data.get("department", ""),
            salary=data.get("salary", 0.0),
            schedule=data.get("schedule", {})
        )