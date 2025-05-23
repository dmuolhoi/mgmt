"""
Student service for the School Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from storage.datastore import get_data, save_data
from utils.constants import USER_ROLES
from services.user_service import create_user
from utils.helpers import generate_id

def add_student(admin_username: str, username: str, password: str,
                first_name: str, last_name: str, email: str, phone: str,
                grade_level: str, date_of_birth: str) -> Tuple[bool, str]:
    """
    Add a new student.
    
    Args:
        admin_username: Username of the admin adding the student
        username: Username for the student
        password: Password for the student
        first_name: First name of the student
        last_name: Last name of the student
        email: Email of the student
        phone: Phone number of the student
        grade_level: Grade level of the student
        date_of_birth: Date of birth of the student (YYYY-MM-DD)
    
    Returns:
        Tuple of (success, message)
    """
    # Create user account first
    success, message, user_id = create_user(
        username, 
        password, 
        USER_ROLES.STUDENT, 
        first_name, 
        last_name, 
        email, 
        phone, 
        admin_username
    )
    
    if not success:
        return False, message
    
    # Generate student ID
    student_id = generate_id("STU")
    
    # Update user record with proper ID
    users = get_data('users')
    users[username]["id"] = student_id
    save_data('users', users)
    
    # Create student record
    students = get_data('students')
    students[student_id] = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "grade_level": grade_level,
        "date_of_birth": date_of_birth,
        "enrollment_date": datetime.now().isoformat(),
        "parent_id": "",
        "courses": [],
        "created_at": datetime.now().isoformat(),
        "created_by": admin_username
    }
    
    save_data('students', students)
    
    return True, f"✅ Student '{first_name} {last_name}' added successfully."

def get_student_details(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific student.
    
    Args:
        student_id: ID of the student
    
    Returns:
        Student details if found, None otherwise
    """
    students = get_data('students')
    student = students.get(student_id)
    
    if student:
        return {**student, "id": student_id}
    
    return None

def update_student(student_id: str, update_data: Dict[str, Any], 
                  updater_username: str) -> Tuple[bool, str]:
    """
    Update a student's information.
    
    Args:
        student_id: ID of the student to update
        update_data: Data to update
        updater_username: Username of the user making the update
    
    Returns:
        Tuple of (success, message)
    """
    students = get_data('students')
    
    if student_id not in students:
        return False, f"❌ Student with ID '{student_id}' not found."
    
    # Update student data
    for key, value in update_data.items():
        students[student_id][key] = value
    
    # Update modification metadata
    students[student_id]["modified_at"] = datetime.now().isoformat()
    students[student_id]["modified_by"] = updater_username
    
    save_data('students', students)
    
    # If username is in update_data, update user record as well
    if "username" in update_data:
        users = get_data('users')
        old_username = None
        
        # Find the corresponding user
        for username, user in users.items():
            if user.get("id") == student_id:
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
    
    return True, f"✅ Student information updated successfully."

def enroll_student_in_course(student_id: str, course_id: str, 
                           enrolling_username: str) -> Tuple[bool, str]:
    """
    Enroll a student in a course.
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        enrolling_username: Username of the user making the enrollment
    
    Returns:
        Tuple of (success, message)
    """
    students = get_data('students')
    courses = get_data('courses')
    
    if student_id not in students:
        return False, f"❌ Student with ID '{student_id}' not found."
    
    if course_id not in courses:
        return False, f"❌ Course with ID '{course_id}' not found."
    
    # Check if student is already enrolled
    if course_id in students[student_id].get("courses", []):
        return False, f"❌ Student is already enrolled in this course."
    
    # Add course to student's courses
    if "courses" not in students[student_id]:
        students[student_id]["courses"] = []
    
    students[student_id]["courses"].append(course_id)
    students[student_id]["modified_at"] = datetime.now().isoformat()
    students[student_id]["modified_by"] = enrolling_username
    
    save_data('students', students)
    
    # Add student to course's students
    if "students" not in courses[course_id]:
        courses[course_id]["students"] = []
    
    courses[course_id]["students"].append(student_id)
    courses[course_id]["modified_at"] = datetime.now().isoformat()
    courses[course_id]["modified_by"] = enrolling_username
    
    save_data('courses', courses)
    
    student_name = f"{students[student_id].get('first_name', '')} {students[student_id].get('last_name', '')}".strip()
    course_name = courses[course_id].get('name', '')
    
    return True, f"✅ {student_name} enrolled in {course_name} successfully."

def unenroll_student_from_course(student_id: str, course_id: str, 
                               unenrolling_username: str) -> Tuple[bool, str]:
    """
    Unenroll a student from a course.
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        unenrolling_username: Username of the user making the unenrollment
    
    Returns:
        Tuple of (success, message)
    """
    students = get_data('students')
    courses = get_data('courses')
    
    if student_id not in students:
        return False, f"❌ Student with ID '{student_id}' not found."
    
    if course_id not in courses:
        return False, f"❌ Course with ID '{course_id}' not found."
    
    # Check if student is enrolled
    if course_id not in students[student_id].get("courses", []):
        return False, f"❌ Student is not enrolled in this course."
    
    # Remove course from student's courses
    students[student_id]["courses"].remove(course_id)
    students[student_id]["modified_at"] = datetime.now().isoformat()
    students[student_id]["modified_by"] = unenrolling_username
    
    save_data('students', students)
    
    # Remove student from course's students
    if "students" in courses[course_id] and student_id in courses[course_id]["students"]:
        courses[course_id]["students"].remove(student_id)
        courses[course_id]["modified_at"] = datetime.now().isoformat()
        courses[course_id]["modified_by"] = unenrolling_username
        
        save_data('courses', courses)
    
    student_name = f"{students[student_id].get('first_name', '')} {students[student_id].get('last_name', '')}".strip()
    course_name = courses[course_id].get('name', '')
    
    return True, f"✅ {student_name} unenrolled from {course_name} successfully."

def get_students_by_grade(grade_level: str) -> List[Dict[str, Any]]:
    """
    Get a list of students in a specific grade.
    
    Args:
        grade_level: Grade level to filter by
    
    Returns:
        List of student dictionaries
    """
    students = get_data('students')
    
    return [
        {**student, "id": student_id}
        for student_id, student in students.items()
        if student.get("grade_level") == grade_level
    ]

def get_student_courses(student_id: str) -> List[Dict[str, Any]]:
    """
    Get a list of courses that a student is enrolled in.
    
    Args:
        student_id: ID of the student
    
    Returns:
        List of course dictionaries
    """
    students = get_data('students')
    courses = get_data('courses')
    
    if student_id not in students:
        return []
    
    student_courses = students[student_id].get("courses", [])
    
    return [
        {**courses[course_id], "id": course_id}
        for course_id in student_courses
        if course_id in courses
    ]

def get_student_grades(student_id: str) -> List[Dict[str, Any]]:
    """
    Get a list of grades for a student.
    
    Args:
        student_id: ID of the student
    
    Returns:
        List of grade dictionaries
    """
    grades = get_data('grades')
    
    return [
        {**grade, "id": grade_id}
        for grade_id, grade in grades.items()
        if grade.get("student_id") == student_id
    ]