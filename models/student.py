"""
Student model for the School Management System
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.user import User
from utils.helpers import generate_id

class Student(User):
    """Student class representing a student in the school"""
    
    def __init__(self, username: str, student_id: Optional[str] = None, 
                 **kwargs: Any) -> None:
        """
        Initialize a Student object.
        
        Args:
            username: Username for the student
            student_id: Student ID (generated if not provided)
            **kwargs: Additional student attributes
        """
        super().__init__(username, "student", student_id or generate_id("STU"), **kwargs)
        
        # Student-specific attributes
        self.grade_level = kwargs.get('grade_level', '')
        self.date_of_birth = kwargs.get('date_of_birth', '')
        self.parent_id = kwargs.get('parent_id', '')
        self.enrollment_date = kwargs.get('enrollment_date', datetime.now().isoformat())
        self.courses = kwargs.get('courses', [])
        self.emergency_contact = kwargs.get('emergency_contact', {})
        self.medical_info = kwargs.get('medical_info', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert student object to dictionary.
        
        Returns:
            Dictionary representation of the student
        """
        data = super().to_dict()
        data.update({
            "grade_level": self.grade_level,
            "date_of_birth": self.date_of_birth,
            "parent_id": self.parent_id,
            "enrollment_date": self.enrollment_date,
            "courses": self.courses,
            "emergency_contact": self.emergency_contact,
            "medical_info": self.medical_info
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """
        Create a Student object from a dictionary.
        
        Args:
            data: Dictionary containing student data
            
        Returns:
            Student object
        """
        return cls(
            username=data.get("username", ""),
            student_id=data.get("id"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            is_active=data.get("is_active", True),
            grade_level=data.get("grade_level", ""),
            date_of_birth=data.get("date_of_birth", ""),
            parent_id=data.get("parent_id", ""),
            enrollment_date=data.get("enrollment_date", ""),
            courses=data.get("courses", []),
            emergency_contact=data.get("emergency_contact", {}),
            medical_info=data.get("medical_info", {})
        )