"""
Teacher service for the School Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from storage.datastore import get_data, save_data
from utils.constants import USER_ROLES
from services.user_service import create_user
from utils.helpers import generate_id

def add_teacher(admin_username: str, username: str, password: str,
               first_name: str, last_name: str, email: str, phone: str,
               subjects: List[str], department: str) -> Tuple[bool, str]:
    """
    Add a new teacher.
    
    Args:
        admin_username: Username of the admin adding the teacher
        username: Username for the teacher
        password: Password for the teacher
        first_name: First name of the teacher
        last_name: Last name of the teacher
        email: Email of the teacher
        phone: Phone number of the teacher
        subjects: List of subjects taught by the teacher
        department: Department of the teacher
    
    Returns:
        Tuple of (success, message)
    """
    # Create user account first
    success, message, user_id = create_user(
        username, 
        password, 
        USER_ROLES.TEACHER, 
        first_name, 
        last_name, 
        email, 
        phone, 
        admin_username
    )
    
    if not success:
        return False, message
    
    # Generate teacher ID
    teacher_id = generate_id("TCH")
    
    # Update user record with proper ID
    users = get_data('users')
    users[username]["id"] = teacher_id
    save_data('users', users)
    
    # Create teacher record
    teachers = get_data('teachers')
    teachers[teacher_id] = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "subjects": subjects,
        "department": department,
        "hire_date": datetime.now().isoformat(),
        "classes": [],
        "created_at": datetime.now().isoformat(),
        "created_by": admin_username
    }
    
    save_data('teachers', teachers)
    
    return True, f"✅ Teacher '{first_name} {last_name}' added successfully."

def get_teacher_details(teacher_id: str) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific teacher.
    
    Args:
        teacher_id: ID of the teacher
    
    Returns:
        Teacher details if found, None otherwise
    """
    teachers = get_data('teachers')
    teacher = teachers.get(teacher_id)
    
    if teacher:
        return {**teacher, "id": teacher_id}
    
    return None

def update_teacher(teacher_id: str, update_data: Dict[str, Any], 
                  updater_username: str) -> Tuple[bool, str]:
    """
    Update a teacher's information.
    
    Args:
        teacher_id: ID of the teacher to update
        update_data: Data to update
        updater_username: Username of the user making the update
    
    Returns:
        Tuple of (success, message)
    """
    teachers = get_data('teachers')
    
    if teacher_id not in teachers:
        return False, f"❌ Teacher with ID '{teacher_id}' not found."
    
    # Update teacher data
    for key, value in update_data.items():
        teachers[teacher_id][key] = value
    
    # Update modification metadata
    teachers[teacher_id]["modified_at"] = datetime.now().isoformat()
    teachers[teacher_id]["modified_by"] = updater_username
    
    save_data('teachers', teachers)
    
    # If username is in update_data, update user record as well
    if "username" in update_data:
        users = get_data('users')
        old_username = None
        
        # Find the corresponding user
        for username, user in users.items():
            if user.get("id") == teacher_id:
                old_username = username
                break
        
        if old_username and old_username != update_data["username"]:
            # Create a new entry with updated username
            new_username = update_data["username"]
            users[new_username] = users[old_username]
            users[new_username]["username"] = new_username
            users[new_username]["modified_at"] = datetime.now().isoformat()
            users[new_username]["modified_by"] = updater_username
            
            # Remove old entry
            del users[old_username]
            
            save_data('users', users)
    
    return True, f"✅ Teacher information updated successfully."

def assign_class_to_teacher(teacher_id: str, course_id: str, 
                          assigning_username: str) -> Tuple[bool, str]:
    """
    Assign a class/course to a teacher.
    
    Args:
        teacher_id: ID of the teacher
        course_id: ID of the course
        assigning_username: Username of the user making the assignment
    
    Returns:
        Tuple of (success, message)
    """
    teachers = get_data('teachers')
    courses = get_data('courses')
    
    if teacher_id not in teachers:
        return False, f"❌ Teacher with ID '{teacher_id}' not found."
    
    if course_id not in courses:
        return False, f"❌ Course with ID '{course_id}' not found."
    
    # Check if teacher is already assigned to this class
    if course_id in teachers[teacher_id].get("classes", []):
        return False, f"❌ Teacher is already assigned to this class."
    
    # Add class to teacher's classes
    if "classes" not in teachers[teacher_id]:
        teachers[teacher_id]["classes"] = []
    
    teachers[teacher_id]["classes"].append(course_id)
    teachers[teacher_id]["modified_at"] = datetime.now().isoformat()
    teachers[teacher_id]["modified_by"] = assigning_username
    
    save_data('teachers', teachers)
    
    # Update course's teacher
    courses[course_id]["teacher_id"] = teacher_id
    courses[course_id]["modified_at"] = datetime.now().isoformat()
    courses[course_id]["modified_by"] = assigning_username
    
    save_data('courses', courses)
    
    teacher_name = f"{teachers[teacher_id].get('first_name', '')} {teachers[teacher_id].get('last_name', '')}".strip()
    course_name = courses[course_id].get('name', '')
    
    return True, f"✅ Assigned {course_name} to {teacher_name} successfully."

def unassign_class_from_teacher(teacher_id: str, course_id: str, 
                              unassigning_username: str) -> Tuple[bool, str]:
    """
    Unassign a class/course from a teacher.
    
    Args:
        teacher_id: ID of the teacher
        course_id: ID of the course
        unassigning_username: Username of the user making the unassignment
    
    Returns:
        Tuple of (success, message)
    """
    teachers = get_data('teachers')
    courses = get_data('courses')
    
    if teacher_id not in teachers:
        return False, f"❌ Teacher with ID '{teacher_id}' not found."
    
    if course_id not in courses:
        return False, f"❌ Course with ID '{course_id}' not found."
    
    # Check if teacher is assigned to this class
    if course_id not in teachers[teacher_id].get("classes", []):
        return False, f"❌ Teacher is not assigned to this class."
    
    # Check if this is the correct teacher for the course
    if courses[course_id].get("teacher_id") != teacher_id:
        return False, f"❌ This teacher is not the primary teacher for this course."
    
    # Remove class from teacher's classes
    teachers[teacher_id]["classes"].remove(course_id)
    teachers[teacher_id]["modified_at"] = datetime.now().isoformat()
    teachers[teacher_id]["modified_by"] = unassigning_username
    
    save_data('teachers', teachers)
    
    # Update course's teacher
    courses[course_id]["teacher_id"] = None
    courses[course_id]["modified_at"] = datetime.now().isoformat()
    courses[course_id]["modified_by"] = unassigning_username
    
    save_data('courses', courses)
    
    teacher_name = f"{teachers[teacher_id].get('first_name', '')} {teachers[teacher_id].get('last_name', '')}".strip()
    course_name = courses[course_id].get('name', '')
    
    return True, f"✅ Unassigned {course_name} from {teacher_name} successfully."

def get_teachers_by_department(department: str) -> List[Dict[str, Any]]:
    """
    Get a list of teachers in a specific department.
    
    Args:
        department: Department to filter by
    
    Returns:
        List of teacher dictionaries
    """
    teachers = get_data('teachers')
    
    return [
        {**teacher, "id": teacher_id}
        for teacher_id, teacher in teachers.items()
        if teacher.get("department") == department
    ]

def get_teachers_by_subject(subject: str) -> List[Dict[str, Any]]:
    """
    Get a list of teachers who teach a specific subject.
    
    Args:
        subject: Subject to filter by
    
    Returns:
        List of teacher dictionaries
    """
    teachers = get_data('teachers')
    
    return [
        {**teacher, "id": teacher_id}
        for teacher_id, teacher in teachers.items()
        if subject in teacher.get("subjects", [])
    ]

def get_teacher_courses(teacher_id: str) -> List[Dict[str, Any]]:
    """
    Get a list of courses that a teacher is assigned to.
    
    Args:
        teacher_id: ID of the teacher
    
    Returns:
        List of course dictionaries
    """
    teachers = get_data('teachers')
    courses = get_data('courses')
    
    if teacher_id not in teachers:
        return []
    
    teacher_classes = teachers[teacher_id].get("classes", [])
    
    return [
        {**courses[course_id], "id": course_id}
        for course_id in teacher_classes
        if course_id in courses
    ]